"""End-to-end tests for the core: vault, permissions, and the full
propose → approve → execute → audit flow with a scripted LLM."""

import asyncio

import pytest

from mystic_agent.agent import AgentLoop
from mystic_agent.audit import AuditLog
from mystic_agent.db import init_db
from mystic_agent.events import Event, EventBus
from mystic_agent.llm import LLMReply, ToolCall
from mystic_agent.permissions import DecisionInbox, Level, PermissionStore
from mystic_agent.tools import ToolRegistry, builtin_tools
from mystic_agent.vault import Vault


@pytest.fixture()
def paths(tmp_path):
    db = tmp_path / "test.sqlite3"
    init_db(db)
    return db, tmp_path / "vault.key"


def test_vault_roundtrip(paths):
    db, key = paths
    vault = Vault(db, key)
    vault.set("telegram_bot_token", "123:abc")
    assert vault.get("telegram_bot_token") == "123:abc"
    # value on disk is encrypted, not plaintext
    raw = db.read_bytes()
    assert b"123:abc" not in raw
    # a second vault instance reuses the same key file
    assert Vault(db, key).get("telegram_bot_token") == "123:abc"


def test_permission_store_defaults_to_propose(paths):
    db, _ = paths
    store = PermissionStore(db)
    assert store.get("anything") == Level.PROPOSE
    store.set("notes", Level.ACT_SILENT)
    assert store.get("notes") == Level.ACT_SILENT


class ScriptedProvider:
    """Calls add_note once, then finishes with a text reply."""

    def __init__(self) -> None:
        self.calls = 0

    async def chat(self, system, messages, tools):
        self.calls += 1
        if self.calls == 1:
            return LLMReply(
                tool_calls=[ToolCall("add_note", {"text": "kup mleko"})]
            )
        return LLMReply(text="Zapisane!")


def make_loop(db_path, level: Level):
    bus = EventBus()
    audit = AuditLog(db_path)
    permissions = PermissionStore(db_path)
    permissions.set("notes", level)
    inbox = DecisionInbox(db_path)
    registry = ToolRegistry()
    notes: list[str] = []
    for tool in builtin_tools(notes):
        registry.register(tool)
    sent: list[str] = []

    async def notify(text, meta=None):
        sent.append(text)

    loop = AgentLoop(
        bus, ScriptedProvider(), registry, permissions, inbox, audit, notify
    )
    return loop, bus, inbox, audit, notes, sent


async def test_act_silent_executes_directly(paths):
    db, _ = paths
    loop, bus, inbox, audit, notes, sent = make_loop(db, Level.ACT_SILENT)
    await loop.handle(
        Event(type="telegram.message", payload={"text": "zanotuj: kup mleko"},
              source="test")
    )
    assert notes == ["kup mleko"]
    assert inbox.pending() == []
    actions = [row["action"] for row in audit.recent()]
    assert "tool.executed:add_note" in actions


async def test_propose_waits_then_executes_on_approval(paths):
    db, _ = paths
    loop, bus, inbox, audit, notes, sent = make_loop(db, Level.PROPOSE)
    await loop.handle(
        Event(type="telegram.message", payload={"text": "zanotuj: kup mleko"},
              source="test")
    )
    # nothing executed yet — proposal is waiting
    assert notes == []
    pending = inbox.pending()
    assert len(pending) == 1 and pending[0]["tool"] == "add_note"
    assert any("Proponuję" in s for s in sent)

    # the user approves → decision event → execution + audit
    decision = inbox.resolve(pending[0]["id"], approved=True)
    await loop.handle(
        Event(type="decision.approved", payload=decision, source="test")
    )
    assert notes == ["kup mleko"]
    actions = [row["action"] for row in audit.recent()]
    assert "tool.executed:add_note" in actions
    assert "tool.proposed:add_note" in actions


async def test_off_blocks_execution(paths):
    db, _ = paths
    loop, bus, inbox, audit, notes, sent = make_loop(db, Level.OFF)
    await loop.handle(
        Event(type="telegram.message", payload={"text": "zanotuj: kup mleko"},
              source="test")
    )
    assert notes == []
    assert inbox.pending() == []
    actions = [row["action"] for row in audit.recent()]
    assert "tool.blocked:add_note" in actions
