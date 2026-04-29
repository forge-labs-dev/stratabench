"""Model registry and ModelSpec.

Every eval notebook iterates over (or selects from) ``REGISTRY`` and uses
the resulting ``ModelSpec`` to dispatch the inference call. Decoding params
bake into Strata's per-cell provenance hash, so changing temperature here
invalidates every cached score that used the old value — exactly what we
want for an audit-trail benchmark harness.

The v1 bundle covers seven frontier closed-API models, three competitive
open models served via Together, and one Mistral. All entries point at
OpenAI-compatible chat-completions endpoints — Anthropic, Google, and
Mistral all expose those alongside their native APIs and our thin
``chat_completion`` doesn't need provider-specific code for v1.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    """Identifies a model + its provider + decoding defaults."""

    id: str
    """Canonical model identifier (e.g. ``gpt-4o-mini``)."""

    provider: str
    """``openai`` | ``anthropic`` | ``google`` | ``together`` | ``mistral``."""

    base_url: str
    """OpenAI-compatible endpoint."""

    api_key_env: str
    """Environment variable carrying the provider key."""

    temperature: float = 0.0
    max_tokens: int = 1024


# Provider base URLs — pulled out so adding a model from an existing
# provider is a one-line edit.
_OPENAI = "https://api.openai.com/v1"
_ANTHROPIC = "https://api.anthropic.com/v1"
_GEMINI = "https://generativelanguage.googleapis.com/v1beta/openai"
_TOGETHER = "https://api.together.xyz/v1"
_MISTRAL = "https://api.mistral.ai/v1"


REGISTRY: dict[str, ModelSpec] = {
    # --- OpenAI ---
    "gpt-4o-mini": ModelSpec(
        id="gpt-4o-mini",
        provider="openai",
        base_url=_OPENAI,
        api_key_env="OPENAI_API_KEY",
    ),
    "gpt-4o": ModelSpec(
        id="gpt-4o",
        provider="openai",
        base_url=_OPENAI,
        api_key_env="OPENAI_API_KEY",
    ),
    # --- Anthropic ---
    "claude-haiku-4-5": ModelSpec(
        id="claude-haiku-4-5",
        provider="anthropic",
        base_url=_ANTHROPIC,
        api_key_env="ANTHROPIC_API_KEY",
    ),
    "claude-sonnet-4-6": ModelSpec(
        id="claude-sonnet-4-6",
        provider="anthropic",
        base_url=_ANTHROPIC,
        api_key_env="ANTHROPIC_API_KEY",
    ),
    "claude-opus-4-7": ModelSpec(
        id="claude-opus-4-7",
        provider="anthropic",
        base_url=_ANTHROPIC,
        api_key_env="ANTHROPIC_API_KEY",
    ),
    # --- Google Gemini ---
    "gemini-2.5-flash": ModelSpec(
        id="gemini-2.5-flash",
        provider="google",
        base_url=_GEMINI,
        api_key_env="GEMINI_API_KEY",
    ),
    "gemini-2.5-pro": ModelSpec(
        id="gemini-2.5-pro",
        provider="google",
        base_url=_GEMINI,
        api_key_env="GEMINI_API_KEY",
    ),
    # --- Open models via Together ---
    "llama-3.1-8b-instruct": ModelSpec(
        id="meta-llama/Llama-3.1-8B-Instruct-Turbo",
        provider="together",
        base_url=_TOGETHER,
        api_key_env="TOGETHER_API_KEY",
    ),
    "llama-3.3-70b-instruct": ModelSpec(
        id="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        provider="together",
        base_url=_TOGETHER,
        api_key_env="TOGETHER_API_KEY",
    ),
    "qwen-2.5-72b-instruct": ModelSpec(
        id="Qwen/Qwen2.5-72B-Instruct-Turbo",
        provider="together",
        base_url=_TOGETHER,
        api_key_env="TOGETHER_API_KEY",
    ),
    # --- Mistral ---
    "mistral-small-latest": ModelSpec(
        id="mistral-small-latest",
        provider="mistral",
        base_url=_MISTRAL,
        api_key_env="MISTRAL_API_KEY",
    ),
}
