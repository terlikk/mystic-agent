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


# 3D extrusion: the letters cast a solid diagonal side, from a mid indigo
# down to near-black, so the wordmark reads as raised blocks on the terminal.
_EXTRUDE = [
    (1, 1, "#6f64c8"),
    (2, 2, "#4c4590"),
    (3, 3, "#332d63"),
]


def print_banner(console: Console | None = None) -> None:
    console = console or Console()
    # a clean, dedicated splash screen
    try:
        console.clear()
    except Exception:
        pass
    console.print()
    console.print()

    # Composite on a character grid: paint the extrusion layers first (deepest
    # to shallowest, each only where still empty), then the bright gradient
    # letters on top. Per-cell rendering lets the 3D side peek out down-right.
    src_h = len(BANNER)
    src_w = max(len(line) for line in BANNER)
    rows = [line.ljust(src_w) for line in BANNER]
    depth = max(dy for _, dy, _ in _EXTRUDE)
    grid_h, grid_w = src_h + depth, src_w + depth
    cell = [[None] * grid_w for _ in range(grid_h)]  # None empty, else style
    for dx, dy, color in sorted(_EXTRUDE, key=lambda e: -e[1]):  # deepest first
        for r in range(src_h):
            for c in range(src_w):
                if rows[r][c] != " ":
                    cell[r + dy][c + dx] = color
    for r in range(src_h):
        for c in range(src_w):
            if rows[r][c] != " ":
                cell[r][c] = f"bold {_shade(r, src_h)}"  # letter face on top

    margin = max(0, (console.size.width - grid_w) // 2)
    pad = " " * margin
    for r in range(grid_h):
        line = Text(pad)
        for c in range(grid_w):
            style = cell[r][c]
            line.append("█" if style else " ", style=style or "")
        console.print(line)
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
