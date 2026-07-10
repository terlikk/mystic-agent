"""Load forged skills from disk as Tools.

A skill is a single Python file with this shape:

    SKILL = {
        "name": "weather",
        "capability": "web",
        "description": "…",
        "parameters": { JSON schema },
    }

    def run(args: dict) -> str: ...
    def test() -> None: ...   # must not raise

    if __name__ == "__main__":  # standard footer, see SKILL_FOOTER
        ...

Skills always execute in the sandbox subprocess — even after approval —
so generated code never touches the vault or the main process.
"""

import json
from pathlib import Path
from typing import Any

from .sandbox import run_skill_file
from .tools import Tool

SKILL_FOOTER = '''

if __name__ == "__main__":
    import json as _json, sys as _sys
    _mode = _sys.argv[1] if len(_sys.argv) > 1 else "run"
    if _mode == "meta":
        print(_json.dumps(SKILL, ensure_ascii=False))
    elif _mode == "test":
        test()
        print("OK")
    else:
        _args = _json.loads(_sys.argv[2]) if len(_sys.argv) > 2 else {}
        print(run(_args))
'''


def skills_dir(data_dir: Path) -> Path:
    d = data_dir / "skills"
    d.mkdir(parents=True, exist_ok=True)
    return d


async def read_meta(path: Path) -> dict[str, Any] | None:
    result = await run_skill_file(path, "meta", timeout=8)
    if not result.ok:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def _make_tool(path: Path, meta: dict[str, Any]) -> Tool:
    async def run(args: dict[str, Any]) -> str:
        result = await run_skill_file(path, "run", args)
        if result.ok:
            return result.stdout or "(brak wyniku)"
        return f"skill zgłosił błąd: {result.stderr or 'nieznany'}"

    return Tool(
        name=meta["name"],
        capability=meta.get("capability", "skills"),
        description=meta.get("description", "Wyuczone narzędzie."),
        parameters=meta.get("parameters", {"type": "object", "properties": {}}),
        func=run,
    )


async def load_skills(data_dir: Path) -> list[Tool]:
    tools: list[Tool] = []
    for path in sorted(skills_dir(data_dir).glob("*.py")):
        meta = await read_meta(path)
        if meta and "name" in meta:
            tools.append(_make_tool(path, meta))
    return tools


async def load_one(path: Path) -> Tool | None:
    meta = await read_meta(path)
    if meta and "name" in meta:
        return _make_tool(path, meta)
    return None
