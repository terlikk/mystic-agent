"""End-to-end tests for the core: vault, permissions, and the full
propose → approve → execute → audit flow with a scripted LLM."""

import pytest

from mystic_agent.agent import AgentLoop
from mystic_agent.audit import AuditLog
from mystic_agent.db import db, init_db
from mystic_agent.events import Event, EventBus
from mystic_agent.llm import LLMReply, ToolCall
from mystic_agent.permissions import DecisionInbox, Level, PermissionStore
from mystic_agent.tools import ToolRegistry, builtin_tools
from mystic_agent.vault import Vault


@pytest.fixture()
def paths(tmp_path):
    db_path = tmp_path / "test.sqlite3"
    init_db(db_path)
    return db_path, tmp_path / "vault.key"


def saved_notes(db_path) -> list[str]:
    with db(db_path) as conn:
        return [r["text"] for r in conn.execute("SELECT text FROM notes")]


def test_vault_roundtrip(paths):
    db_path, key = paths
    vault = Vault(db_path, key)
    vault.set("telegram_bot_token", "123:abc")
    assert vault.get("telegram_bot_token") == "123:abc"
    # value on disk is encrypted, not plaintext
    raw = db_path.read_bytes()
    assert b"123:abc" not in raw
    # a second vault instance reuses the same key file
    assert Vault(db_path, key).get("telegram_bot_token") == "123:abc"


def test_permission_store_defaults_to_propose(paths):
    db_path, _ = paths
    store = PermissionStore(db_path)
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
    for tool in builtin_tools(db_path):
        registry.register(tool)
    sent: list[str] = []

    async def notify(text, meta=None):
        sent.append(text)

    loop = AgentLoop(
        bus, ScriptedProvider(), registry, permissions, inbox, audit, notify
    )
    return loop, bus, inbox, audit, sent


async def test_act_silent_executes_directly(paths):
    db_path, _ = paths
    loop, bus, inbox, audit, sent = make_loop(db_path, Level.ACT_SILENT)
    await loop.handle(
        Event(type="telegram.message", payload={"text": "zanotuj: kup mleko"},
              source="test")
    )
    assert saved_notes(db_path) == ["kup mleko"]
    assert inbox.pending() == []
    actions = [row["action"] for row in audit.recent()]
    assert "tool.executed:add_note" in actions


async def test_propose_waits_then_executes_on_approval(paths):
    db_path, _ = paths
    loop, bus, inbox, audit, sent = make_loop(db_path, Level.PROPOSE)
    await loop.handle(
        Event(type="telegram.message", payload={"text": "zanotuj: kup mleko"},
              source="test")
    )
    # nothing executed yet — proposal is waiting
    assert saved_notes(db_path) == []
    pending = inbox.pending()
    assert len(pending) == 1 and pending[0]["tool"] == "add_note"
    assert any("Proponuję" in s for s in sent)

    # the user approves → decision event → execution + audit
    decision = inbox.resolve(pending[0]["id"], approved=True)
    await loop.handle(
        Event(type="decision.approved", payload=decision, source="test")
    )
    assert saved_notes(db_path) == ["kup mleko"]
    actions = [row["action"] for row in audit.recent()]
    assert "tool.executed:add_note" in actions
    assert "tool.proposed:add_note" in actions


async def test_off_blocks_execution(paths):
    db_path, _ = paths
    loop, bus, inbox, audit, sent = make_loop(db_path, Level.OFF)
    await loop.handle(
        Event(type="telegram.message", payload={"text": "zanotuj: kup mleko"},
              source="test")
    )
    assert saved_notes(db_path) == []
    assert inbox.pending() == []
    actions = [row["action"] for row in audit.recent()]
    assert "tool.blocked:add_note" in actions


def test_email_host_derivation():
    from mystic_agent.email_tools import derive_hosts

    assert derive_hosts("jan@gmail.com") == ("imap.gmail.com", "smtp.gmail.com")
    assert derive_hosts("jan@outlook.com") == (
        "outlook.office365.com",
        "smtp-mail.outlook.com",
    )
    assert derive_hosts("jan@firma.pl") == ("imap.firma.pl", "smtp.firma.pl")


async def test_remind_tool_schedules_reminder(paths):
    db_path, _ = paths
    tools = {t.name: t for t in builtin_tools(db_path)}
    out = await tools["remind"].func({"text": "wyjmij pranie", "minutes": 1})
    assert "przypomnę" in out
    with db(db_path) as conn:
        rows = conn.execute("SELECT * FROM reminders").fetchall()
    assert len(rows) == 1
    assert rows[0]["text"] == "wyjmij pranie"
    assert rows[0]["status"] == "pending"


def test_memory_recall_block(paths):
    from mystic_agent.memory import Memory

    db_path, _ = paths
    mem = Memory(db_path)
    assert mem.recall_block() == ""
    mem.add("księgowa to Anna, anna@example.com")
    mem.add("auto: przegląd w marcu")
    block = mem.recall_block()
    assert "Anna" in block and "przegląd" in block


class RememberProvider:
    """Calls remember once, then replies."""

    def __init__(self) -> None:
        self.calls = 0
        self.seen_system = ""

    async def chat(self, system, messages, tools):
        self.seen_system = system
        self.calls += 1
        if self.calls == 1:
            return LLMReply(
                tool_calls=[ToolCall("remember", {"fact": "mam na imię Filip"})]
            )
        return LLMReply(text="Zapamiętane, Filip.")


async def test_conversation_history_persists_and_feeds_back(paths):
    from mystic_agent.memory import Conversation, Memory

    db_path, _ = paths
    bus = EventBus()
    audit = AuditLog(db_path)
    permissions = PermissionStore(db_path)
    permissions.set("memory", Level.ACT_SILENT)
    inbox = DecisionInbox(db_path)
    registry = ToolRegistry()
    for tool in builtin_tools(db_path):
        registry.register(tool)
    provider = RememberProvider()

    async def notify(text, meta=None):
        pass

    loop = AgentLoop(
        bus, provider, registry, permissions, inbox, audit, notify,
        memory=Memory(db_path), conversation=Conversation(db_path),
    )
    await loop.handle(
        Event(type="telegram.message", payload={"text": "zapamiętaj: mam na imię Filip"},
              source="test")
    )
    # the fact was stored and the conversation recorded
    assert any("Filip" in f for _, f in Memory(db_path).all())
    history = Conversation(db_path).recent()
    assert history[0]["role"] == "user"
    assert history[-1]["role"] == "assistant"

    # next turn sees the memory injected into the system prompt
    provider2 = RememberProvider()
    provider2.calls = 5  # force a plain reply
    loop2 = AgentLoop(
        bus, provider2, registry, permissions, inbox, audit, notify,
        memory=Memory(db_path), conversation=Conversation(db_path),
    )
    await loop2.handle(
        Event(type="telegram.message", payload={"text": "jak mam na imię?"},
              source="test")
    )
    assert "Filip" in provider2.seen_system


class ForgeProvider:
    """Returns a valid skill file that doubles a number."""

    async def chat(self, system, messages, tools):
        return LLMReply(
            text=(
                "SKILL = {\n"
                '    "name": "double",\n'
                '    "capability": "math",\n'
                '    "description": "Podwaja liczbę.",\n'
                '    "parameters": {"type": "object", "properties":'
                ' {"n": {"type": "number"}}, "required": ["n"]},\n'
                "}\n\n"
                "def run(args):\n"
                '    return str(args["n"] * 2)\n\n'
                "def test():\n"
                '    assert run({"n": 3}) == "6"\n'
            )
        )


async def test_forge_generates_tests_and_proposes(paths, tmp_path):
    from mystic_agent.forge import Forge

    forge = Forge(ForgeProvider())
    result = await forge.forge("podwój liczbę")
    assert result.ok, result.error
    assert result.name == "double"
    assert "def run" in result.code


async def test_learn_end_to_end_registers_skill(paths, tmp_path):
    from mystic_agent.forge import Forge
    from mystic_agent.skills_loader import skills_dir

    db_path, _ = paths
    bus = EventBus()
    audit = AuditLog(db_path)
    permissions = PermissionStore(db_path)
    inbox = DecisionInbox(db_path)
    registry = ToolRegistry()
    sent: list[str] = []

    async def notify(text, meta=None):
        sent.append(text)

    loop = AgentLoop(
        bus, ForgeProvider(), registry, permissions, inbox, audit, notify,
        forge=Forge(ForgeProvider()),
        skills_dir=skills_dir(tmp_path),
    )

    # /learn → forge → proposal in the inbox
    await loop.handle(
        Event(type="forge.request", payload={"description": "podwój liczbę"},
              source="test")
    )
    pending = inbox.pending()
    assert len(pending) == 1 and pending[0]["tool"] == "__forge__"

    # approve → skill file written and registered, usable via sandbox
    decision = inbox.resolve(pending[0]["id"], approved=True)
    await loop.handle(
        Event(type="decision.approved", payload=decision, source="test")
    )
    assert (skills_dir(tmp_path) / "double.py").exists()
    tool = registry.get("double")
    assert tool is not None
    assert await tool.func({"n": 5}) == "10"
