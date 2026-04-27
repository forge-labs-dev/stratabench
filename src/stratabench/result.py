"""The eval-result dataclass that every notebook publishes."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvalResult:
    """One eval × one model = one EvalResult.

    Stored as the artifact of an eval cell. The leaderboard notebook joins
    these into the published table. ``score`` is the headline number,
    ``details`` carries per-question outcomes for audit (what the model
    answered, what we expected, why it was right or wrong).

    Provenance is implicit: Strata's artifact hash for the cell that
    produced this EvalResult is the audit identifier. A reproducer matching
    the hash has matched the methodology end-to-end.
    """

    eval_name: str
    model_id: str
    score: float
    n: int
    details: dict = field(default_factory=dict)
