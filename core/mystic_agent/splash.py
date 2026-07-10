"""The CLI splash: pixel banner + neofetch-style status table."""

from rich.console import Console
from rich.table import Table
from rich.text import Text

from . import __version__
from .branding import BANNER, CLI_NAME, NAME, REPO_URL
from .config import settings

# blue → violet, one shade per banner line (same gradient as the site)
_GRADIENT = ["#2563eb", "#3b5aec", "#5150ed", "#6747ed", "#7c3aed"]


def print_splash(telegram_on: bool, model: str, tool_count: int) -> None:
    console = Console()
    console.print()
    for i, line in enumerate(BANNER):
        shade = _GRADIENT[min(i % 5, len(_GRADIENT) - 1)] if i < 5 else _GRADIENT[
            min(i - 5, len(_GRADIENT) - 1)
        ]
        console.print(Text(line, style=f"bold {shade}"))
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold #2563eb")
    table.add_column(style="white")
    table.add_row("DESIGNATION", f"{NAME} v{__version__}")
    table.add_row("RUNTIME", f"http://{settings.host}:{settings.port}")
    table.add_row("MODEL", model)
    table.add_row("CHANNELS", "telegram ✓" if telegram_on else "telegram — brak tokenu")
    table.add_row("TOOLS", str(tool_count))
    table.add_row("DATA", str(settings.data_dir))
    table.add_row("LICENSE", "MIT · open source")
    console.print(table)
    console.print()

    url = f"http://{settings.host}:{settings.port}"
    panel = Text()
    panel.append("  ▸ Panel sterowania: ", style="bold #22d3ee")
    panel.append(url, style="bold underline #22d3ee")
    panel.append("  (otwórz w przeglądarce)", style="dim")
    console.print(panel)
    console.print(
        Text("    tylko na tej maszynie — Twój agent, Twój panel", style="dim")
    )
    console.print()
    console.print(
        Text(f"● w budowie — {REPO_URL}", style="#7c3aed"),
    )
    console.print(
        Text(f"$ {CLI_NAME} czeka na zdarzenia…", style="dim"),
    )
    console.print()
