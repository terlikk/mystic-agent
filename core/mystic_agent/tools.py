"""Tool registry. A tool = an executable capability with a JSON schema.

Skills forged by the agent (stage 4) will register here too.
"""

import asyncio
import html
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable

from .db import db
from .llm import ToolSpec

ToolFunc = Callable[[dict[str, Any]], Awaitable[str]]


@dataclass
class Tool:
    name: str
    capability: str  # permission group, e.g. "notes", "reminders", "web"
    description: str
    parameters: dict[str, Any]  # JSON schema
    func: ToolFunc

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(self.name, self.description, self.parameters)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def specs(self) -> list[ToolSpec]:
        return [t.spec for t in self._tools.values()]

    def all(self) -> list[Tool]:
        return list(self._tools.values())


_TAG_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>|<[^>]+>", re.S | re.I)


def builtin_tools(db_path: Path) -> list[Tool]:
    """The starter skill pack: time, persistent notes, reminders, web."""

    async def get_time(_: dict[str, Any]) -> str:
        return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

    async def add_note(args: dict[str, Any]) -> str:
        text = str(args.get("text", "")).strip()
        if not text:
            return "pusta notatka — nic nie zapisano"
        with db(db_path) as conn:
            conn.execute(
                "INSERT INTO notes (ts, text) VALUES (?, ?)",
                (datetime.now(timezone.utc).isoformat(), text),
            )
        return f"zapisano notatkę: {text}"

    async def list_notes(_: dict[str, Any]) -> str:
        with db(db_path) as conn:
            rows = conn.execute(
                "SELECT id, text FROM notes ORDER BY id"
            ).fetchall()
        if not rows:
            return "brak notatek"
        return "\n".join(f"{r['id']}. {r['text']}" for r in rows)

    async def remember(args: dict[str, Any]) -> str:
        from .memory import Memory

        fact = str(args.get("fact", "")).strip()
        if not fact:
            return "nic do zapamiętania"
        Memory(db_path).add(fact)
        return f"zapamiętane: {fact}"

    async def recall(_: dict[str, Any]) -> str:
        from .memory import Memory

        facts = Memory(db_path).all()
        if not facts:
            return "nic jeszcze nie zapamiętałem"
        return "\n".join(f"{i}. {f}" for i, f in facts)

    async def remind(args: dict[str, Any]) -> str:
        text = str(args.get("text", "")).strip()
        minutes = float(args.get("minutes", 0))
        if not text or minutes <= 0:
            return "podaj treść i dodatnią liczbę minut"
        due = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        with db(db_path) as conn:
            conn.execute(
                "INSERT INTO reminders (created_at, due_at, text) VALUES (?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    due.isoformat(),
                    text,
                ),
            )
        local = due.astimezone().strftime("%H:%M")
        return f"przypomnę o {local}: {text}"

    async def run_shell(args: dict[str, Any]) -> str:
        command = str(args.get("command", "")).strip()
        if not command:
            return "podaj komendę"
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
        except asyncio.TimeoutError:
            proc.kill()
            return "przekroczono limit czasu (30s)"
        text = out.decode("utf-8", "replace").strip()
        return f"(kod {proc.returncode})\n{text[:3000]}" if text else f"(kod {proc.returncode})"

    async def read_url(args: dict[str, Any]) -> str:
        import httpx

        url = str(args.get("url", ""))
        if not url.startswith(("http://", "https://")):
            return "podaj pełny adres http(s)"
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=20
        ) as client:
            resp = await client.get(url)
        text = _TAG_RE.sub(" ", resp.text)
        text = html.unescape(re.sub(r"\s+", " ", text)).strip()
        return text[:4000] or "(pusta strona)"

    async def track_package(args: dict[str, Any]) -> str:
        import httpx

        number = str(args.get("number", "")).strip()
        carrier = str(args.get("carrier", "")).strip().lower()
        if not number:
            return "podaj numer przesyłki"
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        ) as client:
            # InPost has a clean public JSON API
            if carrier in ("inpost", "") and number.isalnum():
                try:
                    r = await client.get(
                        f"https://api-shipx-pl.easypack24.net/v1/tracking/{number}"
                    )
                    if r.status_code == 200:
                        d = r.json()
                        status = d.get("status", "?")
                        track = d.get("tracking_details") or []
                        last = track[-1]["status_description"] if track else status
                        return f"InPost {number}: {last} (status: {status})"
                except Exception:
                    pass
            urls = {
                "dpd": f"https://tracktrace.dpd.com.pl/parcelDetails?p1={number}",
                "dhl": f"https://www.dhl.com/pl-pl/home/sledzenie.html?tracking-id={number}",
                "poczta": f"https://emonitoring.poczta-polska.pl/?numer={number}",
                "gls": f"https://gls-group.com/PL/pl/sledzenie-paczek?match={number}",
                "ups": f"https://www.ups.com/track?tracknum={number}",
            }
            url = urls.get(carrier)
            if not url:
                return (
                    f"Nie znam przewoźnika „{carrier}”. Podaj: inpost, dpd, dhl,"
                    " poczta, gls lub ups — albo daj mi link do śledzenia."
                )
            resp = await client.get(url)
            text = _TAG_RE.sub(" ", resp.text)
            text = html.unescape(re.sub(r"\s+", " ", text)).strip()
            return (
                f"{carrier.upper()} {number} — {url}\n{text[:1200]}"
                if text
                else f"otwórz: {url}"
            )

    async def web_search(args: dict[str, Any]) -> str:
        import httpx

        query = str(args.get("query", "")).strip()
        if not query:
            return "podaj zapytanie"
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        ) as client:
            resp = await client.post(
                "https://html.duckduckgo.com/html/", data={"q": query}
            )
        results = []
        for m in re.finditer(
            r'result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', resp.text, re.S
        ):
            link = html.unescape(m.group(1))
            title = html.unescape(_TAG_RE.sub("", m.group(2))).strip()
            if title:
                results.append(f"- {title}\n  {link}")
            if len(results) >= 6:
                break
        return "\n".join(results) or "brak wyników"

    async def add_event(args: dict[str, Any]) -> str:
        start = str(args.get("start", "")).strip()
        title = str(args.get("title", "")).strip()
        if not start or not title:
            return "podaj datę (RRRR-MM-DD GG:MM) i tytuł"
        with db(db_path) as conn:
            conn.execute(
                "INSERT INTO calendar (created_at, start_at, title, notes)"
                " VALUES (?, ?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    start,
                    title,
                    str(args.get("notes", "")),
                ),
            )
        return f"dodano: {start} — {title}"

    async def agenda(args: dict[str, Any]) -> str:
        with db(db_path) as conn:
            rows = conn.execute(
                "SELECT start_at, title FROM calendar"
                " WHERE start_at >= ? ORDER BY start_at LIMIT 20",
                (str(args.get("from", "0000")),),
            ).fetchall()
        if not rows:
            return "kalendarz pusty"
        return "\n".join(f"{r['start_at']} — {r['title']}" for r in rows)

    async def read_file(args: dict[str, Any]) -> str:
        from pathlib import Path as _Path

        raw = str(args.get("path", "")).strip()
        if not raw:
            return "podaj ścieżkę do pliku"
        path = _Path(raw).expanduser()
        if not path.is_file():
            return f"nie ma pliku: {path}"
        if path.suffix.lower() == ".pdf":
            try:
                from pypdf import PdfReader
            except ImportError:
                return "czytanie PDF wymaga pakietu pypdf"
            reader = PdfReader(str(path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
        return text[:6000].strip() or "(pusty plik)"

    async def write_file(args: dict[str, Any]) -> str:
        from pathlib import Path as _Path

        raw = str(args.get("path", "")).strip()
        content = str(args.get("content", ""))
        if not raw:
            return "podaj ścieżkę do zapisu"
        path = _Path(raw).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"zapisano {len(content)} znaków do {path}"

    # ── contacts ─────────────────────────────────────────────────
    async def add_contact(args: dict[str, Any]) -> str:
        name = str(args.get("name", "")).strip()
        if not name:
            return "podaj imię/nazwę kontaktu"
        with db(db_path) as conn:
            conn.execute(
                "INSERT INTO contacts (ts, name, email, phone, note)"
                " VALUES (?, ?, ?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    name,
                    str(args.get("email", "")),
                    str(args.get("phone", "")),
                    str(args.get("note", "")),
                ),
            )
        return f"dodano kontakt: {name}"

    async def find_contact(args: dict[str, Any]) -> str:
        q = f"%{str(args.get('query', '')).strip()}%"
        with db(db_path) as conn:
            rows = conn.execute(
                "SELECT name, email, phone, note FROM contacts"
                " WHERE name LIKE ? OR email LIKE ? OR note LIKE ?"
                " ORDER BY name LIMIT 10",
                (q, q, q),
            ).fetchall()
        if not rows:
            return "brak pasujących kontaktów"
        return "\n".join(
            f"{r['name']} · {r['email'] or '—'} · {r['phone'] or '—'}"
            + (f" · {r['note']}" if r["note"] else "")
            for r in rows
        )

    async def list_contacts(_: dict[str, Any]) -> str:
        with db(db_path) as conn:
            rows = conn.execute(
                "SELECT name, email FROM contacts ORDER BY name"
            ).fetchall()
        if not rows:
            return "książka kontaktów pusta"
        return "\n".join(f"{r['name']} · {r['email'] or '—'}" for r in rows)

    # ── tasks / to-do ────────────────────────────────────────────
    async def add_task(args: dict[str, Any]) -> str:
        text = str(args.get("text", "")).strip()
        if not text:
            return "podaj treść zadania"
        with db(db_path) as conn:
            conn.execute(
                "INSERT INTO tasks (ts, text, due) VALUES (?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    text,
                    str(args.get("due", "")),
                ),
            )
        return f"dodano zadanie: {text}"

    async def list_tasks(args: dict[str, Any]) -> str:
        status = str(args.get("status", "open"))
        with db(db_path) as conn:
            rows = conn.execute(
                "SELECT id, text, due FROM tasks WHERE status = ? ORDER BY id",
                (status,),
            ).fetchall()
        if not rows:
            return "brak zadań" if status == "open" else "brak w tym statusie"
        return "\n".join(
            f"[{r['id']}] {r['text']}" + (f" (do {r['due']})" if r["due"] else "")
            for r in rows
        )

    async def complete_task(args: dict[str, Any]) -> str:
        tid = int(args.get("id", 0))
        with db(db_path) as conn:
            cur = conn.execute(
                "UPDATE tasks SET status = 'done' WHERE id = ? AND status = 'open'",
                (tid,),
            )
        return f"odhaczono zadanie #{tid}" if cur.rowcount else f"nie ma otwartego #{tid}"

    return [
        Tool(
            name="get_time",
            capability="system",
            description="Zwraca aktualną datę i godzinę na maszynie użytkownika.",
            parameters={"type": "object", "properties": {}},
            func=get_time,
        ),
        Tool(
            name="add_note",
            capability="notes",
            description="Zapisuje trwałą notatkę użytkownika.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Treść notatki"}
                },
                "required": ["text"],
            },
            func=add_note,
        ),
        Tool(
            name="list_notes",
            capability="notes",
            description="Wyświetla zapisane notatki użytkownika.",
            parameters={"type": "object", "properties": {}},
            func=list_notes,
        ),
        Tool(
            name="remember",
            capability="memory",
            description="Zapamiętuje trwały fakt o użytkowniku (imię, preferencje,"
            " ważne dane), by pamiętać go w przyszłych rozmowach.",
            parameters={
                "type": "object",
                "properties": {
                    "fact": {"type": "string", "description": "Fakt do zapamiętania"}
                },
                "required": ["fact"],
            },
            func=remember,
        ),
        Tool(
            name="recall",
            capability="memory",
            description="Wypisuje wszystko, co agent zapamiętał o użytkowniku.",
            parameters={"type": "object", "properties": {}},
            func=recall,
        ),
        Tool(
            name="remind",
            capability="reminders",
            description="Ustawia przypomnienie — agent odezwie się na telegramie"
            " po zadanym czasie.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "O czym przypomnieć"},
                    "minutes": {
                        "type": "number",
                        "description": "Za ile minut przypomnieć",
                    },
                },
                "required": ["text", "minutes"],
            },
            func=remind,
        ),
        Tool(
            name="run_shell",
            capability="shell",
            description="Uruchamia komendę powłoki na komputerze użytkownika"
            " (potężne — domyślnie wymaga zgody).",
            parameters={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Komenda do wykonania"}
                },
                "required": ["command"],
            },
            func=run_shell,
        ),
        Tool(
            name="read_url",
            capability="web",
            description="Pobiera stronę WWW i zwraca jej tekst (do researchu"
            " i sprawdzania cen/treści).",
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Adres strony"}
                },
                "required": ["url"],
            },
            func=read_url,
        ),
        Tool(
            name="track_package",
            capability="web",
            description="Sprawdza status przesyłki po numerze (InPost, DPD, DHL,"
            " Poczta Polska, GLS, UPS). Do stałego pilnowania użyj watch_url.",
            parameters={
                "type": "object",
                "properties": {
                    "number": {"type": "string", "description": "Numer przesyłki"},
                    "carrier": {
                        "type": "string",
                        "description": "inpost / dpd / dhl / poczta / gls / ups",
                    },
                },
                "required": ["number"],
            },
            func=track_package,
        ),
        Tool(
            name="web_search",
            capability="web",
            description="Szuka w internecie i zwraca listę wyników z linkami"
            " (użyj, gdy nie znasz adresu strony).",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Czego szukać"}
                },
                "required": ["query"],
            },
            func=web_search,
        ),
        Tool(
            name="add_event",
            capability="calendar",
            description="Dodaje wydarzenie do kalendarza.",
            parameters={
                "type": "object",
                "properties": {
                    "start": {"type": "string", "description": "RRRR-MM-DD GG:MM"},
                    "title": {"type": "string", "description": "Tytuł"},
                    "notes": {"type": "string", "description": "Notatki (opc.)"},
                },
                "required": ["start", "title"],
            },
            func=add_event,
        ),
        Tool(
            name="agenda",
            capability="calendar",
            description="Pokazuje nadchodzące wydarzenia z kalendarza.",
            parameters={
                "type": "object",
                "properties": {
                    "from": {"type": "string", "description": "Od kiedy (opc.)"}
                },
            },
            func=agenda,
        ),
        Tool(
            name="read_file",
            capability="files",
            description="Czyta lokalny plik tekstowy lub PDF (faktury, umowy,"
            " dokumenty).",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Ścieżka do pliku"}
                },
                "required": ["path"],
            },
            func=read_file,
        ),
        Tool(
            name="write_file",
            capability="files_write",
            description="Zapisuje treść do lokalnego pliku (raport, notatka,"
            " eksport). Tworzy foldery, jeśli trzeba.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Ścieżka pliku"},
                    "content": {"type": "string", "description": "Co zapisać"},
                },
                "required": ["path", "content"],
            },
            func=write_file,
        ),
        Tool(
            name="add_contact",
            capability="contacts",
            description="Dodaje osobę do książki kontaktów (imię, mail, telefon).",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "note": {"type": "string", "description": "Kto to / kontekst"},
                },
                "required": ["name"],
            },
            func=add_contact,
        ),
        Tool(
            name="find_contact",
            capability="contacts",
            description="Szuka kontaktu po imieniu/mailu/notatce (użyj, zanim"
            " napiszesz do kogoś, by znaleźć jego adres).",
            parameters={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            func=find_contact,
        ),
        Tool(
            name="list_contacts",
            capability="contacts",
            description="Wypisuje wszystkie zapisane kontakty.",
            parameters={"type": "object", "properties": {}},
            func=list_contacts,
        ),
        Tool(
            name="add_task",
            capability="tasks",
            description="Dodaje zadanie do listy rzeczy do zrobienia.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "due": {"type": "string", "description": "Termin (opcjonalnie)"},
                },
                "required": ["text"],
            },
            func=add_task,
        ),
        Tool(
            name="list_tasks",
            capability="tasks",
            description="Pokazuje zadania (domyślnie otwarte).",
            parameters={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "open lub done"}
                },
            },
            func=list_tasks,
        ),
        Tool(
            name="complete_task",
            capability="tasks",
            description="Odhacza zadanie po numerze.",
            parameters={
                "type": "object",
                "properties": {"id": {"type": "integer"}},
                "required": ["id"],
            },
            func=complete_task,
        ),
    ]


def payment_tools(wallet) -> list[Tool]:
    """Spending guard — a hard budget ceiling on top of the permission gate.
    Use a capped virtual card as the real payment method, never a main card."""

    async def authorize_payment(args: dict[str, Any]) -> str:
        try:
            amount = float(args.get("amount", 0))
        except (TypeError, ValueError):
            return "podaj kwotę liczbą"
        merchant = str(args.get("merchant", "")).strip() or "?"
        url = str(args.get("url", ""))
        ok, msg = wallet.check(amount)
        if not ok:
            return f"ODMOWA płatności {amount:.2f} u {merchant}: {msg}"
        wallet.record(amount, merchant, url)
        return f"autoryzowano płatność {amount:.2f} u {merchant} ({msg})"

    async def set_budget(args: dict[str, Any]) -> str:
        per_txn = float(args.get("per_txn", 0))
        monthly = float(args.get("monthly", 0))
        currency = str(args.get("currency", "PLN"))
        wallet.set_policy(per_txn, monthly, currency)
        return (
            f"budżet: max {per_txn:.2f} {currency}/transakcja,"
            f" {monthly:.2f} {currency}/miesiąc"
        )

    async def budget_status(_: dict[str, Any]) -> str:
        per_txn, monthly, cur = wallet.policy()
        if per_txn <= 0:
            return "budżet nie ustawiony — agent nie może płacić bez ręcznej zgody"
        return (
            f"limit/transakcja: {per_txn:.2f} {cur}\n"
            f"limit/miesiąc: {monthly:.2f} {cur}\n"
            f"wydano w tym miesiącu: {wallet.spent_this_month():.2f} {cur}"
        )

    return [
        Tool(
            name="authorize_payment",
            capability="payment",
            description="Autoryzuje płatność (kwota + sprzedawca) w ramach budżetu."
            " Wywołaj TUŻ PRZED finalnym potwierdzeniem zakupu.",
            parameters={
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "merchant": {"type": "string"},
                    "url": {"type": "string"},
                },
                "required": ["amount", "merchant"],
            },
            func=authorize_payment,
        ),
        Tool(
            name="set_budget",
            capability="payment",
            description="Ustawia limity wydatków agenta (na transakcję i miesiąc).",
            parameters={
                "type": "object",
                "properties": {
                    "per_txn": {"type": "number"},
                    "monthly": {"type": "number"},
                    "currency": {"type": "string"},
                },
                "required": ["per_txn"],
            },
            func=set_budget,
        ),
        Tool(
            name="budget_status",
            capability="system",
            description="Pokazuje limity i ile agent wydał w tym miesiącu.",
            parameters={"type": "object", "properties": {}},
            func=budget_status,
        ),
    ]


def phone_tools(vault, owner_name: str) -> list[Tool]:
    """Outbound calling via Twilio. Config is read from the vault at call
    time, so updated credentials / tunnel take effect without a restart."""

    async def call(args: dict[str, Any]) -> str:
        from .telephony import TwilioConfig, place_call

        to = str(args.get("to", "")).strip()
        goal = str(args.get("goal", "")).strip()
        if not to or not goal:
            return "podaj numer i cel rozmowy"
        cfg = TwilioConfig(
            account_sid=vault.get("twilio_account_sid") or "",
            auth_token=vault.get("twilio_auth_token") or "",
            from_number=vault.get("twilio_number") or "",
            public_url=vault.get("public_url") or "",
            elevenlabs_voice=vault.get("elevenlabs_voice") or "",
        )
        name = vault.get("user_name") or owner_name
        ok, res = await place_call(cfg, to, goal, name)
        if ok:
            return f"dzwonię na {to} w sprawie: {goal} (call {res}) — zdam raport po rozmowie"
        return f"nie udało się zadzwonić: {res}"

    return [
        Tool(
            name="call",
            capability="phone",
            description="Dzwoni na podany numer i prowadzi rozmowę w Twoim"
            " imieniu (jawnie jako asystent AI), by osiągnąć cel. Po rozmowie"
            " raportuje wynik i transkrypcję.",
            parameters={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Numer w formacie +48…"},
                    "goal": {
                        "type": "string",
                        "description": "Co ma załatwić przez telefon",
                    },
                },
                "required": ["to", "goal"],
            },
            func=call,
        ),
    ]


def automation_tools(store) -> list[Tool]:
    """Tools that let the agent set up its own standing instructions —
    so 'pilnuj maili od klientów i odpowiadaj' just works."""

    async def watch_email(args: dict[str, Any]) -> str:
        instruction = str(args.get("instruction", "")).strip()
        if not instruction:
            return "podaj, co robić z nowymi mailami"
        spec = {}
        if args.get("sender"):
            spec["sender"] = str(args["sender"])
        aid = store.add("email", instruction, spec)
        who = f" od '{spec['sender']}'" if spec.get("sender") else ""
        return f"[#{aid}] pilnuję nowych maili{who}: {instruction}"

    async def schedule_task(args: dict[str, Any]) -> str:
        instruction = str(args.get("instruction", "")).strip()
        if not instruction:
            return "podaj zadanie do wykonania"
        spec = {}
        if args.get("at"):
            spec["at"] = str(args["at"])
        elif args.get("every_minutes"):
            spec["every_minutes"] = int(args["every_minutes"])
        else:
            spec["every_minutes"] = 60
        aid = store.add("schedule", instruction, spec)
        when = spec.get("at") or f"co {spec.get('every_minutes')} min"
        return f"[#{aid}] zaplanowane ({when}): {instruction}"

    async def watch_url(args: dict[str, Any]) -> str:
        url = str(args.get("url", "")).strip()
        instruction = str(args.get("instruction", "")).strip()
        if not url or not instruction:
            return "podaj url i co zrobić przy zmianie"
        every = int(args.get("every_minutes", 60))
        aid = store.add("url", instruction, {"url": url, "every_minutes": every})
        return f"[#{aid}] pilnuję {url} (co {every} min): {instruction}"

    async def list_automations(_: dict[str, Any]) -> str:
        autos = store.all()
        if not autos:
            return "brak aktywnych automatyzacji"
        return "\n".join(
            f"[#{a['id']}] {a['kind']}: {a['instruction']}" for a in autos
        )

    async def stop_automation(args: dict[str, Any]) -> str:
        aid = int(args.get("id", 0))
        return f"zatrzymano #{aid}" if store.disable(aid) else f"nie ma aktywnej #{aid}"

    common = {
        "instruction": {"type": "string", "description": "Co agent ma zrobić"}
    }
    return [
        Tool(
            name="watch_email",
            capability="automations",
            description="Ustawia stałe pilnowanie skrzynki: dla KAŻDEGO nowego"
            " maila agent wykona podaną instrukcję (np. odpisz, eskaluj).",
            parameters={
                "type": "object",
                "properties": {
                    **common,
                    "sender": {
                        "type": "string",
                        "description": "Tylko od tego nadawcy (opcjonalnie)",
                    },
                },
                "required": ["instruction"],
            },
            func=watch_email,
        ),
        Tool(
            name="schedule_task",
            capability="automations",
            description="Planuje cykliczne zadanie — o danej godzinie (at:"
            " 'GG:MM') lub co N minut (every_minutes).",
            parameters={
                "type": "object",
                "properties": {
                    **common,
                    "at": {"type": "string", "description": "Godzina GG:MM"},
                    "every_minutes": {"type": "integer"},
                },
                "required": ["instruction"],
            },
            func=schedule_task,
        ),
        Tool(
            name="watch_url",
            capability="automations",
            description="Pilnuje strony WWW i wykonuje instrukcję, gdy się zmieni.",
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    **common,
                    "every_minutes": {"type": "integer"},
                },
                "required": ["url", "instruction"],
            },
            func=watch_url,
        ),
        Tool(
            name="list_automations",
            capability="automations",
            description="Wypisuje aktywne automatyzacje.",
            parameters={"type": "object", "properties": {}},
            func=list_automations,
        ),
        Tool(
            name="stop_automation",
            capability="automations",
            description="Wyłącza automatyzację po numerze.",
            parameters={
                "type": "object",
                "properties": {"id": {"type": "integer"}},
                "required": ["id"],
            },
            func=stop_automation,
        ),
    ]
