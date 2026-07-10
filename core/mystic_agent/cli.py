import logging

import click
import uvicorn

from . import __version__
from .branding import CLI_NAME, NAME
from .config import settings


@click.group()
@click.version_option(__version__, prog_name=CLI_NAME)
def main() -> None:
    f"""{NAME} — Twój Jarvis. Twój serwer. Twoje zasady."""


@main.command()
@click.option("--host", default=None, help="Adres nasłuchu (domyślnie 127.0.0.1)")
@click.option("--port", default=None, type=int, help="Port (domyślnie 7700)")
def start(host: str | None, port: int | None) -> None:
    """Uruchom agenta (serwis + pętla zdarzeń + telegram)."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(name)s: %(message)s"
    )
    if host:
        settings.host = host
    if port:
        settings.port = port

    from .server import build_app
    from .setup_wizard import is_configured, run_wizard
    from .splash import print_splash

    import sys

    if not is_configured() and sys.stdin.isatty():
        run_wizard()

    app = build_app()
    print_splash(
        telegram_on=app.state.telegram_on,
        model=app.state.model,
        tool_count=app.state.tool_count,
    )
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="warning")


@main.command()
@click.confirmation_option(
    prompt="Na pewno? Usunie sejf z kluczami, notatki, audyt i uprawnienia"
)
def reset() -> None:
    """Wyczyść wszystkie dane agenta — onboarding zacznie się od zera."""
    import shutil

    if settings.data_dir.exists():
        shutil.rmtree(settings.data_dir)
        click.echo(f"✓ usunięto {settings.data_dir}")
    else:
        click.echo("nie było czego czyścić")
    click.echo(f"Następny '{CLI_NAME} start' poprowadzi konfigurację od nowa.")


@main.command()
def setup() -> None:
    """Skonfiguruj klucze od nowa (klucz LLM, telegram) — trafiają do sejfu."""
    from .setup_wizard import run_wizard

    run_wizard(force=True)


@main.command()
def status() -> None:
    """Sprawdź, czy agent działa."""
    import json
    import urllib.request

    url = f"http://{settings.host}:{settings.port}/health"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            data = json.load(resp)
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    except OSError:
        click.echo(f"{NAME} nie odpowiada na {url}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
