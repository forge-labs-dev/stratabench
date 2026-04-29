# Results format

Each published score is a single JSON file under
[`results/`](https://github.com/forge-labs-dev/stratabench/tree/main/results)
in the repo. The leaderboard notebook reads everything in that
directory and renders the published table.

## File naming

```
results/
├── mmlu_redux_2_0_generative_zeroshot__gpt-4o-mini.json
├── mmlu_redux_2_0_generative_zeroshot__claude-sonnet-4-6.json
├── gsm8k_cot_zeroshot__gpt-4o-mini.json
└── ...
```

Pattern: `{eval_name}__{model_id}.json` with `/` characters in model
IDs replaced with `-`.

## Schema

```json
{
  "eval_name": "mmlu_redux_2_0_generative_zeroshot",
  "model_id": "claude-sonnet-4-6",
  "score": 0.7421,
  "n": 5712,
  "details": {
    "micro_score": 0.7388,
    "parse_failure_rate": 0.0014,
    "per_subject": { "abstract_algebra": 0.45 }
  },
  "provenance_hash": "7f3afdc31b3bb0d6c5816622758a297c2c28f2a0d011696616b962555b55e2d1",
  "stratabench_commit": "abc1234",
  "stratabench_version": "0.1.0",
  "run_at": "2026-04-27T10:00:00Z",
  "reproduced_by": []
}
```

| Field | Required | Description |
|---|---|---|
| `eval_name` | ✓ | Canonical eval identifier from the score cell |
| `model_id` | ✓ | Model ID as it appears in `stratabench.REGISTRY` |
| `score` | ✓ | Headline score (the eval's primary metric) |
| `n` | ✓ | Number of items scored |
| `details` | ✓ | Eval-specific breakdown |
| `provenance_hash` | ✓ | Strata artifact hash for the score cell's output |
| `stratabench_commit` | ✓ | Git commit of `forge-labs-dev/stratabench` the run executed against |
| `stratabench_version` | ✓ | `__version__` from `src/stratabench/__init__.py` |
| `run_at` | ✓ | ISO-8601 timestamp of the run |
| `reproduced_by` | optional | List of confirmed reproductions |

## Publishing a result

After running an eval notebook, call the helper from a Python cell:

```python
from stratabench import publish_score

publish_score(
    score_cell_output,                 # the EvalResult artifact
    results_dir="../../../results",
    provenance_hash="7f3afdc...",      # from the score cell's metadata
)
```

The helper writes a properly-named, schema-conformant JSON file under
`results/`. Commit it and open a PR.

## Reproductions

To confirm a published score, run the same notebook at the same
commit, get a matching provenance hash, and add yourself to that
file's `reproduced_by` list:

```json
{
  "reproduced_by": [
    {
      "name": "alice",
      "run_at": "2026-04-28T15:00:00Z",
      "provenance_hash": "7f3afdc...",
      "score": 0.7415
    }
  ]
}
```

Confirmed reproductions are surfaced as a "Reproduced by" column on
the leaderboard. See [Reproducing results](reproduce.md) for the
step-by-step.
