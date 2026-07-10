"""First-run setup: collect the LLM key and Telegram token interactively
and store them in the encrypted vault. Every user brings their own keys —
nothing is ever bundled with the project. Styled to match the banner.
"""

from rich.console import Console
from rich.prompt import IntPrompt, Prompt

from .config import settings
from .db import init_db
from .vault import Vault
from .wizard_ui import block, cyan


def _vault() -> Vault:
    settings.ensure_dirs()
    init_db(settings.db_path)
    return Vault(settings.db_path, settings.vault_key_path)


def is_configured() -> bool:
    vault = _vault()
    has_llm = bool(
        settings.anthropic_api_key
        or settings.openai_api_key
        or vault.get("anthropic_api_key")
        or vault.get("openai_api_key")
    )
    has_telegram = bool(
        settings.telegram_bot_token or vault.get("telegram_bot_token")
    )
    return has_llm and has_telegram


def _ask(label: str, **kw) -> str:
    return Prompt.ask(f"  [bold {cyan}]▸[/] {label}", **kw).strip()


def run_wizard(force: bool = False) -> None:
    console = Console()
    vault = _vault()

    console.print(
        block(
            "KONFIGURACJA",
            "Wszystko ląduje w szyfrowanym sejfie na tej maszynie.\n"
            "Nic nie opuszcza Twojego sprzętu.  ·  Enter = pomiń pole.",
        )
    )

    # ── 1. LLM ───────────────────────────────────────────────────
    has_llm = bool(
        settings.anthropic_api_key
        or settings.openai_api_key
        or vault.get("anthropic_api_key")
        or vault.get("openai_api_key")
    )
    if force or not has_llm:
        console.print(block("KLUCZ AI", "Mózg agenta — Anthropic lub OpenAI", step="1/5"))
        key = _ask(
            "Klucz API ([dim]sk-ant-…[/] lub [dim]sk-…[/])",
            password=True,
            default="",
            show_default=False,
        )
        if key.startswith("sk-ant"):
            vault.set("anthropic_api_key", key)
            vault.set("llm_model", _ask("Model", default="claude-sonnet-5"))
            console.print("    [green]✓[/] klucz Anthropic w sejfie")
        elif key:
            vault.set("openai_api_key", key)
            vault.set("llm_model", _ask("Model OpenAI (np. gpt-5.2)"))
            console.print("    [green]✓[/] klucz OpenAI w sejfie")
        else:
            console.print("    [yellow]•[/] pominięto — agent nie ruszy bez klucza LLM")

    # ── 2. Telegram ──────────────────────────────────────────────
    has_telegram = bool(
        settings.telegram_bot_token or vault.get("telegram_bot_token")
    )
    if force or not has_telegram:
        console.print(
            block("TELEGRAM", "Bota tworzysz u @BotFather → /newbot → token", step="2/5")
        )
        token = _ask("Token bota", password=True, default="", show_default=False)
        if token:
            vault.set("telegram_bot_token", token)
            owner = IntPrompt.ask(
                f"  [bold {cyan}]▸[/] Twoje ID (0 = przypnij pierwszą osobę, która napisze)",
                default=0,
            )
            vault.set("telegram_owner_id", str(owner))
            console.print("    [green]✓[/] telegram skonfigurowany")
        else:
            console.print("    [yellow]•[/] pominięto — zostaje samo API")

    # ── 3. E-mail (opcjonalnie) ──────────────────────────────────
    if force or not vault.get("email_address"):
        console.print(
            block(
                "E-MAIL  (opcjonalnie)",
                "Agent poczyta skrzynkę i — za zgodą — odpisze.\n"
                "Gmail: hasło aplikacji z myaccount.google.com/apppasswords",
                step="3/5",
            )
        )
        address = _ask("Adres e-mail (enter = pomiń)", default="", show_default=False)
        if address:
            password = _ask("Hasło aplikacji", password=True)
            from .email_tools import derive_hosts

            imap_default, smtp_default = derive_hosts(address)
            imap_host = _ask("Serwer IMAP", default=imap_default)
            smtp_host = _ask("Serwer SMTP", default=smtp_default)
            vault.set("email_address", address)
            vault.set("email_password", password)
            vault.set("email_imap_host", imap_host)
            vault.set("email_smtp_host", smtp_host)
            console.print("    [green]✓[/] skrzynka podpięta")

    # ── 4. Osobowość ─────────────────────────────────────────────
    if force or not vault.get("persona_key"):
        from .personas import select_persona

        key, prompt = select_persona(console)
        vault.set("persona_key", key)
        vault.set("persona_prompt", prompt)
        name = _ask(
            "Jak agent ma się do Ciebie zwracać? (enter = bez imienia)",
            default="",
            show_default=False,
        )
        if name:
            vault.set("user_name", name)

    # ── 5. O Tobie ───────────────────────────────────────────────
    if force or not vault.get("user_profiled"):
        console.print(
            block(
                "O TOBIE",
                "Kim jesteś, czym się zajmujesz? Trafi do pamięci — zrozumiem\n"
                "Twój kontekst od pierwszej wiadomości.  ·  Enter = pomiń.",
                step="5/5",
            )
        )
        about = _ask("O Tobie", default="", show_default=False)
        if about:
            from .memory import Memory

            Memory(settings.db_path).add(f"O użytkowniku: {about}")
            vault.set("user_profiled", "1")
            console.print("    [green]✓[/] zapamiętane")

    console.print()
    console.print(f"  [bold {cyan}]▸[/] Gotowe. Uruchamiam agenta…\n")
