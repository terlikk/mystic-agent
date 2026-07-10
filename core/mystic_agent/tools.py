"""Tool registry. A tool = an executable capability with a JSON schema.

Skills forged by the agent (stage 4) will register here too.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Awaitable, Callable

from .llm import ToolSpec

ToolFunc = Callable[[dict[str, Any]], Awaitable[str]]


@dataclass
class Tool:
    name: str
    capability: str  # permission group, e.g. "notes", "system"
    description: str
    parameters: dict[str, Any]
    func: ToolFunc

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(self.name, self.description, self.parameters)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def specs(self) -> list[ToolSpec]:
        return [t.spec for t in self._tools.values()]

    def all(self) -> list[Tool]:
        return list(self._tools.values())


def builtin_tools(notes: list[str]) -> list[Tool]:
    """A minimal starter set so the loop has something real to call."""

    async def get_time(_: dict[str, Any]) -> str:
        return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

    async def add_note(args: dict[str, Any]) -> str:
        notes.append(str(args.get("text", "")))
        return f"zapisano notatkę #{len(notes)}"

    async def list_notes(_: dict[str, Any]) -> str:
        if not notes:
            return "brak notatek"
        return "\n".join(f"{i + 1}. {n}" for i, n in enumerate(notes))

    return [
        Tool(
            name="get_time",
            capability="system",
            description="Zwraca aktualną datę i godzinę na maszynie użytkownika.",
            parameters={"type": "object", "properties": {}},
            func=get_time,
        ),
        Tool(
            name="add_note",
            capability="notes",
            description="Zapisuje krótką notatkę użytkownika.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Treść notatki"}
                },
                "required": ["text"],
            },
            func=add_note,
        ),
        Tool(
            name="list_notes",
            capability="notes",
            description="Wyświetla zapisane notatki użytkownika.",
            parameters={"type": "object", "properties": {}},
            func=list_notes,
        ),
    ]
