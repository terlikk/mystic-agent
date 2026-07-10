"""CLI visuals: the pixel banner (shown first) and the neofetch status
table (shown once the agent is up).
"""

from rich.console import Console
from rich.table import Table
from rich.text import Text

from . import __version__
from .branding import BANNER, CLI_NAME, NAME, REPO_URL
from .config import settings

# blue → violet, one shade per banner line (same gradient as the site)
_GRADIENT = ["#2563eb", "#3b5aec", "#5150ed", "#6747ed", "#7c3aed"]


def _shade(i: int, total: int) -> str:
    if total <= 1:
        return _GRADIENT[0]
    return _GRADIENT[min(int(i / (total - 1) * (len(_GRADIENT) - 1)), len(_GRADIENT) - 1)]


def print_banner(console: Console | None = None) -> None:
    console = console or Console()
    # a clean, dedicated splash screen
    try:
        console.clear()
    except Exception:
        pass
    console.print()
    console.print()
    for i, line in enumerate(BANNER):
        console.print(Text(line, style=f"bold {_shade(i, len(BANNER))}"), justify="center")
    console.print()
    tagline = Text()
    tagline.append("Twój Jarvis.  ", style="bold #e7edf5")
    tagline.append("Twój serwer.  ", style="bold #e7edf5")
    tagline.append("Twoje zasady.", style=f"bold {_GRADIENT[-1]}")
    console.print(tagline, justify="center")
    console.print()
    console.print(
        Text("open source · self-hosted · zero chmury", style="dim"),
        justify="center",
    )
    console.print()


def print_status(
    telegram_on: bool, model: str, tool_count: int, console: Console | None = None
) -> None:
    console = console or Console()
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold #22d3ee")
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
    console.print(Text(f"● w budowie — {REPO_URL}", style="#7c3aed"))
    console.print(Text(f"$ {CLI_NAME} czeka na zdarzenia…", style="dim"))
    console.print()
