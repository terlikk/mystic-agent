"""Shared look for the terminal setup: block headers + arrow prompts,
tuned to match the pixel banner (graphite + electric cyan + violet).
"""

from rich.panel import Panel
from rich.text import Text

cyan = "#22d3ee"
violet = "#a78bfa"
line = "#1a2330"


def block(title: str, subtitle: str = "", step: str = "") -> Panel:
    """A bordered block header, like the banner's slabs."""
    body = Text()
    if step:
        body.append(f"{step}  ", style=f"bold {violet}")
    body.append(title, style=f"bold {cyan}")
    if subtitle:
        body.append(f"\n{subtitle}", style="dim")
    return Panel(body, border_style=line, padding=(0, 2), expand=False)
