# @name Helpers & Schema
# Module cell — types, the eval-result schema, and the model registry.
# Every downstream eval cell imports EvalResult, the registry, and the
# provenance-hash extractor from here.

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModelSpec:
    """Identifies a model + its provider + decoding defaults.

    Decoding params bake into Strata's per-cell provenance hash, so changing
    temperature or max_tokens yields a fresh artifact and a fresh score.
    """

    id: str  # canonical name, e.g. "gpt-4o-mini"
    provider: str  # "openai" | "anthropic" | "google" | "together" | ...
    base_url: str  # OpenAI-compatible endpoint
    api_key_env: str  # env var name that carries the key
    temperature: float = 0.0
    max_tokens: int = 1024


# v1 model registry. Intentionally short — the substrate is the point.
# Models will land as we ship; once the list grows past a handful this
# moves to its own cell.
REGISTRY: dict[str, ModelSpec] = {
    "gpt-4o-mini": ModelSpec(
        id="gpt-4o-mini",
        provider="openai",
        base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
    ),
}


@dataclass(frozen=True)
class EvalResult:
    """One eval × one model = one EvalResult.

    Persisted as the artifact for each eval cell; a downstream leaderboard
    cell joins these into the published table. ``score`` is the headline
    number; ``details`` may carry per-question outcomes for debugging or
    audit, including the model's raw output.
    """

    eval_name: str
    model_id: str
    score: float
    n: int  # items scored
    details: dict = field(default_factory=dict)
