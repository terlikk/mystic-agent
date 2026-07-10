"""The tool forge: the agent writes a new skill, tests it in the sandbox,
and — only if the test passes — proposes it to the owner for approval.
This is what powers the /learn command.
"""

import re
import tempfile
from pathlib import Path

from .llm import LLMProvider
from .sandbox import run_skill_file
from .skills_loader import SKILL_FOOTER

_SYSTEM = """Jesteś generatorem narzędzi (skilli) dla agenta MysticAgent.
Na podstawie opisu piszesz JEDEN plik w Pythonie w dokładnie takim formacie:

SKILL = {
    "name": "krotka_nazwa_snake_case",
    "capability": "grupa_uprawnien",   # np. web, system, notes, math
    "description": "Co robi, po polsku.",
    "parameters": {"type": "object", "properties": { ... }, "required": [ ... ]},
}

def run(args: dict) -> str:
    # implementacja; ZAWSZE zwraca string
    ...

def test() -> None:
    # samotest; wywołaj run(...) z przykładowymi argumentami
    # i sprawdź asertami. Ma NIE rzucać wyjątku, gdy działa.
    ...

Zasady:
- tylko biblioteka standardowa Pythona (+ httpx jest dostępne, jeśli trzeba sieci)
- żadnych sekretów, żadnych ścieżek do plików użytkownika
- NIE dołączaj bloku `if __name__ == "__main__"` — zostanie dodany automatycznie
- odpowiedz WYŁĄCZNIE kodem, bez komentarza wstępnego i bez ```-ów."""


def _strip_fences(text: str) -> str:
    fenced = re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    body = fenced.group(1) if fenced else text
    # drop any footer the model added despite instructions
    body = re.split(r'\nif __name__ == ["\']__main__["\']', body)[0]
    return body.strip()


class ForgeResult:
    def __init__(self, ok: bool, name: str = "", code: str = "", error: str = ""):
        self.ok = ok
        self.name = name
        self.code = code
        self.error = error


class Forge:
    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    async def forge(self, description: str) -> ForgeResult:
        reply = await self._provider.chat(
            _SYSTEM,
            [{"role": "user", "content": f"Napisz skill: {description}"}],
            tools=[],
        )
        code = _strip_fences(reply.text)
        if "def run(" not in code or "SKILL" not in code:
            return ForgeResult(False, error="model nie zwrócił poprawnego skilla")

        full = code + "\n" + SKILL_FOOTER
        tmp = Path(tempfile.mkdtemp(prefix="mystic-forge-")) / "skill.py"
        tmp.write_text(full, encoding="utf-8")

        meta = await run_skill_file(tmp, "meta", timeout=8)
        if not meta.ok:
            return ForgeResult(False, error=f"zły format: {meta.stderr[:300]}")
        import json

        try:
            name = json.loads(meta.stdout)["name"]
        except (json.JSONDecodeError, KeyError):
            return ForgeResult(False, error="brak nazwy w SKILL")

        test = await run_skill_file(tmp, "test", timeout=12)
        if not test.ok:
            return ForgeResult(
                False, name=name, error=f"samotest nie przeszedł: {test.stderr[:300]}"
            )

        return ForgeResult(True, name=name, code=full)
