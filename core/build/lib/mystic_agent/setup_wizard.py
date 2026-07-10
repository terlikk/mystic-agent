"""First-run setup: collect the LLM key and Telegram token interactively
and store them in the encrypted vault. Every user brings their own keys —
nothing is ever bundled with the project.
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt

from .branding import NAME
from .config import settings
from .db import init_db
from .vault import Vault


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


def run_wizard(force: bool = False) -> None:
    console = Console()
    vault = _vault()

    console.print(
        Panel.fit(
            f"[bold]⚙  Konfiguracja {NAME}[/bold]\n\n"
            "Wszystko, co tu podasz, ląduje w [bold]szyfrowanym sejfie[/bold] "
            f"na tej maszynie\n({settings.db_path}) — nigdy nie opuszcza "
            "Twojego sprzętu.\nEnter = pomiń pole.",
            border_style="#7c3aed",
        )
    )

    # ── LLM ──────────────────────────────────────────────────────
    has_llm = bool(
        settings.anthropic_api_key
        or settings.openai_api_key
        or vault.get("anthropic_api_key")
        or vault.get("openai_api_key")
    )
    if force or not has_llm:
        key = Prompt.ask(
            "[bold #2563eb]Klucz API[/] (Anthropic [dim]sk-ant-…[/] "
            "lub OpenAI [dim]sk-…[/])",
            password=True,
            default="",
            show_default=False,
        ).strip()
        if key.startswith("sk-ant"):
            vault.set("anthropic_api_key", key)
            model = Prompt.ask(
                "[bold #2563eb]Model[/]", default="claude-sonnet-5"
            ).strip()
            vault.set("llm_model", model)
            console.print("  [green]✓[/] klucz Anthropic zapisany w sejfie")
        elif key:
            vault.set("openai_api_key", key)
            model = Prompt.ask(
                "[bold #2563eb]Model OpenAI[/] (np. gpt-5.2)"
            ).strip()
            vault.set("llm_model", model)
            console.print("  [green]✓[/] klucz OpenAI zapisany w sejfie")
        else:
            console.print("  [yellow]•[/] pominięto — agent nie ruszy bez klucza LLM")

    # ── Telegram ─────────────────────────────────────────────────
    has_telegram = bool(
        settings.telegram_bot_token or vault.get("telegram_bot_token")
    )
    if force or not has_telegram:
        console.print(
            "\nBota tworzysz w Telegramie u [bold]@BotFather[/] → /newbot "
            "→ dostajesz token."
        )
        token = Prompt.ask(
            "[bold #2563eb]Token bota Telegram[/]",
            password=True,
            default="",
            show_default=False,
        ).strip()
        if token:
            vault.set("telegram_bot_token", token)
            owner = IntPrompt.ask(
                "[bold #2563eb]Twoje ID na Telegramie[/] "
                "(0 = przypnij do pierwszego, kto napisze)",
                default=0,
            )
            vault.set("telegram_owner_id", str(owner))
            console.print("  [green]✓[/] telegram skonfigurowany")
        else:
            console.print(
                "  [yellow]•[/] pominięto — bez telegrama zostaje samo API"
            )

    # ── Osobowość ────────────────────────────────────────────────
    if force or not vault.get("persona_key"):
        from .personas import select_persona

        key, prompt = select_persona(console)
        vault.set("persona_key", key)
        vault.set("persona_prompt", prompt)
        name = Prompt.ask(
            "[bold #2563eb]Jak agent ma się do Ciebie zwracać?[/] "
            "(enter = bez imienia)",
            default="",
            show_default=False,
        ).strip()
        if name:
            vault.set("user_name", name)

    console.print()
