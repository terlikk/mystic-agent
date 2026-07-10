"""Provider-agnostic LLM layer.

The provider is inferred from the model name: claude-* → Anthropic,
gpt-*/o* → OpenAI. Both are called through their native tool-use APIs
and normalised to (text, tool_calls).
"""

import json
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]  # JSON schema


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]


@dataclass
class LLMReply:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)


class LLMProvider(Protocol):
    async def chat(
        self,
        system: str,
        messages: list[dict[str, str]],
        tools: list[ToolSpec],
    ) -> LLMReply: ...


class AnthropicProvider:
    def __init__(self, api_key: str, model: str) -> None:
        import anthropic

        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def describe_image(self, image_b64: str, prompt: str) -> str:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        return "".join(b.text for b in response.content if b.type == "text")

    async def chat(
        self,
        system: str,
        messages: list[dict[str, str]],
        tools: list[ToolSpec],
    ) -> LLMReply:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=system,
            messages=messages,
            tools=[
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.parameters,
                }
                for t in tools
            ],
        )
        reply = LLMReply()
        for block in response.content:
            if block.type == "text":
                reply.text += block.text
            elif block.type == "tool_use":
                reply.tool_calls.append(ToolCall(block.name, dict(block.input)))
        return reply


class OpenAIProvider:
    def __init__(self, api_key: str, model: str) -> None:
        import openai

        self._client = openai.AsyncOpenAI(api_key=api_key)
        self._model = model

    async def describe_image(self, image_b64: str, prompt: str) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            },
                        },
                    ],
                }
            ],
        )
        return response.choices[0].message.content or ""

    async def chat(
        self,
        system: str,
        messages: list[dict[str, str]],
        tools: list[ToolSpec],
    ) -> LLMReply:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system}, *messages],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters,
                    },
                }
                for t in tools
            ],
        )
        choice = response.choices[0].message
        reply = LLMReply(text=choice.content or "")
        for call in choice.tool_calls or []:
            reply.tool_calls.append(
                ToolCall(call.function.name, json.loads(call.function.arguments))
            )
        return reply


def make_provider(model: str, anthropic_key: str, openai_key: str) -> LLMProvider:
    if model.startswith("claude"):
        if not anthropic_key:
            raise RuntimeError(
                "MYSTIC_ANTHROPIC_API_KEY is required for Claude models"
            )
        return AnthropicProvider(anthropic_key, model)
    if not openai_key:
        raise RuntimeError("MYSTIC_OPENAI_API_KEY is required for OpenAI models")
    return OpenAIProvider(openai_key, model)
