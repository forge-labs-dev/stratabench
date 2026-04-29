# @name Load published results
#
# Walks ``results/`` and loads every score JSON into a pandas frame.
# Empty results dir → empty frame; the leaderboard cell handles that
# case gracefully so the notebook is openable before the first run.
#
# The path is relative to the notebook directory (``../../results/``).
# Run-from-anywhere is intentional: the same notebook works on a fresh
# clone, in CI, and inside a Strata server pointed at this checkout.

import json
from pathlib import Path

import pandas as pd

RESULTS_DIR = Path("../../results")

records = []
if RESULTS_DIR.exists():
    for path in sorted(RESULTS_DIR.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        # Flatten the headline fields for the leaderboard table; keep
        # ``details`` and ``reproduced_by`` nested for the inspector.
        records.append(
            {
                "eval_name": data.get("eval_name"),
                "model_id": data.get("model_id"),
                "score": data.get("score"),
                "n": data.get("n"),
                "provenance_hash": data.get("provenance_hash"),
                "stratabench_commit": data.get("stratabench_commit"),
                "run_at": data.get("run_at"),
                "n_reproductions": len(data.get("reproduced_by") or []),
                "details": data.get("details") or {},
            }
        )

results = pd.DataFrame(records)
print(f"loaded {len(results)} published results from {RESULTS_DIR.resolve()}")
if len(results):
    print(f"  evals covered: {results['eval_name'].nunique()}")
    print(f"  models covered: {results['model_id'].nunique()}")
results
