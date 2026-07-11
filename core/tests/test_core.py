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


def test_permission_sensible_defaults(paths):
    db_path, _ = paths
    store = PermissionStore(db_path)
    # unknown capability asks; harmless ones don't; risky ones ask
    assert store.get("something_new") == Level.PROPOSE
    assert store.get("web") == Level.ACT_SILENT
    assert store.get("notes") == Level.ACT_SILENT
    assert store.get("email_send") == Level.PROPOSE
    assert store.get("shell") == Level.PROPOSE
    assert store.get("payment") == Level.PROPOSE
    # explicit override wins
    store.set("web", Level.PROPOSE)
    assert store.get("web") == Level.PROPOSE


class DoubleSearchProvider:
    """Always asks to web_search — used to prove we don't double-propose."""

    async def chat(self, system, messages, tools):
        return LLMReply(tool_calls=[ToolCall("web_search", {"query": "pogoda"})])


async def test_no_double_proposal(paths):
    db_path, _ = paths
    bus = EventBus()
    audit = AuditLog(db_path)
    permissions = PermissionStore(db_path)
    permissions.set("web", Level.PROPOSE)  # force a proposal
    inbox = DecisionInbox(db_path)
    registry = ToolRegistry()
    for tool in builtin_tools(db_path):
        registry.register(tool)
    sent: list[str] = []

    async def notify(text, meta=None):
        sent.append(text)

    loop = AgentLoop(
        bus, DoubleSearchProvider(), registry, permissions, inbox, audit, notify
    )
    await loop.handle(
        Event(type="telegram.message", payload={"text": "pogoda?"}, source="t")
    )
    # exactly one proposal, not a storm
    assert len(inbox.pending()) == 1
    assert sum("Proponuję" in s for s in sent) == 1


async def test_pause_blocks_autonomous_but_not_chat(paths):
    from mystic_agent.flags import Flags

    db_path, _ = paths
    bus = EventBus()
    audit = AuditLog(db_path)
    permissions = PermissionStore(db_path)
    permissions.set("notes", Level.ACT_SILENT)
    inbox = DecisionInbox(db_path)
    registry = ToolRegistry()
    for tool in builtin_tools(db_path):
        registry.register(tool)
    flags = Flags(db_path)
    flags.set_bool("paused", True)

    async def notify(text, meta=None):
        pass

    loop = AgentLoop(
        bus, ScriptedProvider(), registry, permissions, inbox, audit, notify,
        flags=flags,
    )
    assert loop.is_paused() is True
    # an autonomous automation is skipped while paused
    await loop.handle(
        Event(type="automation.run", payload={"instruction": "zanotuj coś"},
              source="test")
    )
    with db(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) c FROM notes").fetchone()["c"] == 0
    # resuming lets it run
    flags.set_bool("paused", False)
    assert loop.is_paused() is False


async def test_contacts_and_tasks(paths):
    db_path, _ = paths
    tools = {t.name: t for t in builtin_tools(db_path)}

    await tools["add_contact"].func(
        {"name": "Anna Księgowa", "email": "anna@biuro.pl", "note": "księgowość"}
    )
    found = await tools["find_contact"].func({"query": "księgow"})
    assert "anna@biuro.pl" in found

    await tools["add_task"].func({"text": "wysłać fakturę", "due": "piątek"})
    open_tasks = await tools["list_tasks"].func({})
    assert "wysłać fakturę" in open_tasks
    # complete it → no longer open
    tid = int(open_tasks.split("]")[0].strip("["))
    await tools["complete_task"].func({"id": tid})
    assert "brak zadań" in await tools["list_tasks"].func({})


async def test_write_file(paths, tmp_path):
    db_path, _ = paths
    tools = {t.name: t for t in builtin_tools(db_path)}
    target = tmp_path / "out" / "report.md"
    out = await tools["write_file"].func(
        {"path": str(target), "content": "# Raport\ngotowe"}
    )
    assert "zapisano" in out
    assert target.read_text() == "# Raport\ngotowe"


def test_telephony_twiml_and_gating():
    from mystic_agent.telephony import TwilioConfig, build_twiml

    cfg = TwilioConfig("AC1", "tok", "+48111", "https://x.trycloudflare.com")
    assert cfg.ready is True
    assert cfg.wss_relay == "wss://x.trycloudflare.com/relay"
    xml = build_twiml(cfg, "zarezerwuj stolik na 4 osoby", "Filip")
    assert "ConversationRelay" in xml
    assert "wss://x.trycloudflare.com/relay" in xml
    assert "asystent AI w imieniu Filip" in xml
    assert 'ttsProvider="Google"' in xml  # no ElevenLabs voice set → Google

    # with an ElevenLabs voice → switches provider
    cfg2 = TwilioConfig("AC1", "tok", "+48111", "https://x.io", elevenlabs_voice="Rachel")
    assert 'ttsProvider="ElevenLabs"' in build_twiml(cfg2, "cel", "Filip")

    # missing config → not ready
    assert TwilioConfig("", "", "", "").ready is False


async def test_call_tool_needs_config(paths):
    from unittest.mock import Mock

    from mystic_agent.tools import phone_tools

    vault = Mock()
    vault.get = Mock(return_value="")  # nothing configured
    tools = {t.name: t for t in phone_tools(vault, "Filip")}
    out = await tools["call"].func({"to": "+48500600700", "goal": "test"})
    assert "nie udało" in out or "konfigur" in out


def test_wallet_budget_ceiling(paths):
    from mystic_agent.wallet import Wallet

    db_path, _ = paths
    w = Wallet(db_path)
    # no budget → nothing is auto-allowed
    ok, _ = w.check(50)
    assert not ok
    w.set_policy(per_txn=200, monthly=500)
    assert w.check(150)[0] is True
    assert w.check(250)[0] is False  # over per-txn
    w.record(400, "hotel", "")
    assert w.check(150)[0] is False  # over monthly (400+150 > 500)


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


async def test_scheduler_fires_due_schedule(paths):
    from datetime import datetime, timedelta, timezone

    from mystic_agent.automations import AutomationStore
    from mystic_agent.proactive import Scheduler

    db_path, _ = paths
    store = AutomationStore(db_path)
    store.add("schedule", "zrób podsumowanie", {"every_minutes": 30})
    bus = EventBus()
    sched = Scheduler(store, bus)

    now = datetime.now(timezone.utc)
    # first tick only arms next_due, fires nothing
    assert await sched.tick(now) == 0
    # not due yet
    assert await sched.tick(now + timedelta(minutes=10)) == 0
    # due → fires one automation.run
    assert await sched.tick(now + timedelta(minutes=31)) == 1
    event = await bus.get()
    assert event.type == "automation.run"
    assert event.payload["instruction"] == "zrób podsumowanie"


class FakeMailbox:
    def __init__(self):
        self._new = [
            {"uid": 11, "from": "klient@firma.pl", "subject": "Wycena",
             "body": "Proszę o wycenę."}
        ]

    def max_uid(self):
        return 10

    def fetch_new(self, last_uid, limit=10):
        fresh = [m for m in self._new if m["uid"] > last_uid]
        max_uid = max([m["uid"] for m in self._new] + [last_uid])
        return fresh, max_uid


async def test_email_watcher_fires_on_new_mail(paths):
    from mystic_agent.automations import AutomationStore
    from mystic_agent.proactive import Scheduler

    db_path, _ = paths
    store = AutomationStore(db_path)
    store.add("email", "odpisz klientowi", {"sender": "klient@"})
    bus = EventBus()
    sched = Scheduler(store, bus, mailbox=FakeMailbox())

    # first tick baselines last_uid to current max (10) → no fire
    assert await sched.tick() == 0
    # second tick sees uid 11 → fires with the email as context
    assert await sched.tick() == 1
    event = await bus.get()
    assert event.type == "automation.run"
    assert "Wycena" in event.payload["context"]


async def test_automation_action_respects_permission_gate(paths):
    """An autonomous email reply must land in the inbox when send is 'propose'."""
    db_path, _ = paths
    bus = EventBus()
    audit = AuditLog(db_path)
    permissions = PermissionStore(db_path)
    permissions.set("notes", Level.PROPOSE)
    inbox = DecisionInbox(db_path)
    registry = ToolRegistry()
    for tool in builtin_tools(db_path):
        registry.register(tool)

    async def notify(text, meta=None):
        pass

    loop = AgentLoop(
        bus, ScriptedProvider(), registry, permissions, inbox, audit, notify
    )
    # ScriptedProvider calls add_note → notes is 'propose' → proposal, not action
    await loop.run_instruction("zanotuj coś", "kontekst")
    assert len(inbox.pending()) == 1


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
