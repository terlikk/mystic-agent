"""Run agent-written skill files in an isolated subprocess.

Isolation (defense in depth — a human still approves every skill before
it is registered):
  * separate process, killed on timeout
  * CPU + address-space rlimits (POSIX)
  * a scratch working dir, not the project or home
  * a minimal environment — NO vault, NO API keys, NO tokens are passed
"""

import asyncio
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SandboxResult:
    ok: bool
    stdout: str
    stderr: str


def _limiter(cpu_seconds: int, mem_bytes: int):
    def _apply() -> None:
        try:
            import resource

            resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
        except Exception:
            pass  # non-POSIX or restricted — the timeout still guards us

    return _apply


async def run_skill_file(
    path: Path,
    mode: str,
    args: dict | None = None,
    timeout: int = 12,
    mem_mb: int = 512,
) -> SandboxResult:
    argv = [sys.executable, "-I", str(path), mode]
    if args is not None:
        argv.append(json.dumps(args, ensure_ascii=False))

    scratch = tempfile.mkdtemp(prefix="mystic-skill-")
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": scratch,
        "TMPDIR": scratch,
        "PYTHONIOENCODING": "utf-8",
    }

    try:
        proc = await asyncio.create_subprocess_exec(
            *argv,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=scratch,
            env=env,
            preexec_fn=_limiter(timeout, mem_mb * 1024 * 1024),
        )
    except Exception as exc:  # pragma: no cover - platform dependent
        return SandboxResult(False, "", f"nie udało się uruchomić: {exc}")

    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout + 2)
    except asyncio.TimeoutError:
        proc.kill()
        return SandboxResult(False, "", f"przekroczono limit czasu ({timeout}s)")

    return SandboxResult(
        proc.returncode == 0,
        out.decode("utf-8", "replace").strip(),
        err.decode("utf-8", "replace").strip(),
    )
