"""Minimal HTTP clients for LLM providers.

Deliberately thin — `httpx` directly, no provider SDK. The notebook cells
that call these clients are part of the methodology; we don't want a fat
SDK to obscure what request is actually going over the wire. Reproducers
read the cell + this module and see the entire interaction.

Currently OpenAI-compatible chat completions only. Anthropic native and
Google native go in this file when the relevant evals add them.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import httpx

from stratabench.models import ModelSpec


@dataclass(frozen=True)
class ChatResponse:
    """Result of a single chat completion call.

    ``content`` is the model's text. ``input_tokens`` / ``output_tokens``
    feed cost accounting downstream. ``raw`` is the full provider JSON for
    debugging / audit.
    """

    content: str
    input_tokens: int
    output_tokens: int
    raw: dict


def chat_completion(
    spec: ModelSpec,
    user: str,
    *,
    system: str | None = None,
    timeout_seconds: float = 60.0,
) -> ChatResponse:
    """Send one chat completion request to an OpenAI-compatible endpoint.

    The request body keeps to the OpenAI canonical shape so this works
    against OpenAI itself, vLLM, Together, OpenRouter, and most hosted
    open-model providers without modification.
    """
    api_key = os.environ.get(spec.api_key_env)
    if not api_key:
        raise RuntimeError(
            f"Missing API key: set {spec.api_key_env} in the Runtime panel"
        )

    messages: list[dict] = []
    if system is not None:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})

    payload = {
        "model": spec.id,
        "messages": messages,
        "temperature": spec.temperature,
        "max_tokens": spec.max_tokens,
    }

    url = spec.base_url.rstrip("/") + "/chat/completions"
    response = httpx.post(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    body = response.json()

    # Defensive parsing — providers occasionally return non-OpenAI shapes
    # under load. Failing loudly with the body in the message beats
    # surfacing a None deep in the score cell.
    try:
        content = body["choices"][0]["message"]["content"]
        usage = body.get("usage", {})
        input_tokens = int(usage.get("prompt_tokens", 0))
        output_tokens = int(usage.get("completion_tokens", 0))
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected response shape from {spec.id}: {body!r}") from exc

    return ChatResponse(
        content=content,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        raw=body,
    )
