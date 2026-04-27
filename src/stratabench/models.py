"""Model registry and ModelSpec.

Every eval notebook iterates over (or selects from) ``REGISTRY`` and uses
the resulting ``ModelSpec`` to dispatch the inference call. Decoding params
bake into Strata's per-cell provenance hash, so changing temperature here
invalidates every cached score that used the old value — exactly what we
want for an audit-trail benchmark harness.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    """Identifies a model + its provider + decoding defaults."""

    id: str
    """Canonical model identifier (e.g. ``gpt-4o-mini``)."""

    provider: str
    """``openai`` | ``anthropic`` | ``google`` | ``together`` | ..."""

    base_url: str
    """OpenAI-compatible endpoint. Anthropic native callers ignore this."""

    api_key_env: str
    """Environment variable carrying the provider key."""

    temperature: float = 0.0
    max_tokens: int = 1024


# v1 registry. Intentionally tight — adding a model is a one-line edit and
# Strata's cache makes "score the new model" cheap (only its slice misses).
REGISTRY: dict[str, ModelSpec] = {
    "gpt-4o-mini": ModelSpec(
        id="gpt-4o-mini",
        provider="openai",
        base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
    ),
}
