"""Helper for persisting EvalResult artifacts as published-score JSON files.

Eval notebooks call ``publish_score(result, results_dir=...)`` after the
score cell to write a structured JSON file under ``results/``. The
leaderboard notebook then reads everything in that directory to render
the published table.

The published shape is documented in ``results/README.md``. Keeping the
schema centralized here means contributor PRs and the leaderboard agree
on the field names.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from stratabench.result import EvalResult


def _git_commit(repo_dir: Path) -> str | None:
    """Best-effort Git commit lookup. Returns None outside a clone."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_dir,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _slugify_model_id(model_id: str) -> str:
    """Make a model ID safe for use in a filename.

    Together's IDs (``meta-llama/Llama-3.3-70B-Instruct-Turbo``) carry
    slashes; replacing them with dashes keeps the filename portable
    without obscuring the source ID.
    """
    return re.sub(r"[^A-Za-z0-9._-]+", "-", model_id).strip("-")


def publish_score(
    result: EvalResult,
    *,
    results_dir: Path | str,
    provenance_hash: str | None = None,
    stratabench_commit: str | None = None,
    stratabench_version: str | None = None,
    extra: dict[str, Any] | None = None,
) -> Path:
    """Write ``result`` plus reproducibility metadata to ``results/``.

    Returns the path to the written file. The file name follows the
    ``{eval_name}__{model_slug}.json`` convention so the leaderboard
    can list scores deterministically.

    Pass ``provenance_hash`` if you have the score cell's artifact hash
    handy (Strata exposes it via the runtime state). Pass it as
    ``"unknown"`` or skip if you're publishing manually outside a
    Strata session — the field is still recorded so a downstream
    reproducer knows what's missing.
    """
    from stratabench import __version__

    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    if stratabench_commit is None:
        # Walk up from the package install to find a containing repo.
        from stratabench import __file__ as pkg_path

        stratabench_commit = _git_commit(Path(pkg_path).resolve().parents[2])

    payload: dict[str, Any] = {
        **asdict(result),
        "provenance_hash": provenance_hash or "unknown",
        "stratabench_commit": stratabench_commit or "unknown",
        "stratabench_version": stratabench_version or __version__,
        "run_at": datetime.now(tz=UTC).isoformat(timespec="seconds"),
        "reproduced_by": [],
    }
    if extra:
        payload.update(extra)

    filename = f"{result.eval_name}__{_slugify_model_id(result.model_id)}.json"
    target = results_dir / filename
    with open(target, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
    return target
