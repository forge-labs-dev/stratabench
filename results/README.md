# Published results

Each file in this directory is one `(eval, model)` score, persisted as
JSON. The leaderboard notebook reads everything in here and renders
the published table.

## File naming

```
results/
├── mmlu_redux_2_0_generative_zeroshot__gpt-4o-mini.json
├── mmlu_redux_2_0_generative_zeroshot__claude-sonnet-4-6.json
├── gsm8k_cot_zeroshot__gpt-4o-mini.json
└── ...
```

Pattern: `{eval_name}__{model_id}.json` (model `/` characters
replaced with `-`).

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
    "per_subject": { "abstract_algebra": 0.45, ... }
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
| `details` | ✓ | Eval-specific breakdown (per-subject, per-bucket, parse failures, etc.) |
| `provenance_hash` | ✓ | Strata artifact hash for the score cell's output |
| `stratabench_commit` | ✓ | Git commit of `forge-labs-dev/stratabench` the run executed against |
| `stratabench_version` | ✓ | `__version__` from `src/stratabench/__init__.py` |
| `run_at` | ✓ | ISO-8601 timestamp of the run |
| `reproduced_by` | optional | List of `{name, run_at, provenance_hash}` for confirmed reproductions |

## Publishing a result

After running an eval notebook, call `stratabench.publish.publish_score(...)`
from a Python cell or via the CLI:

```python
from stratabench.publish import publish_score
publish_score(<eval_result>, results_dir="../../../results")
```

Or, manually: copy the values from your score cell's printout into a
new JSON file matching the schema above, and commit.

## Reproductions

If you re-ran someone's published result and got matching provenance,
add yourself to that file's `reproduced_by` list:

```json
{
  ...,
  "reproduced_by": [
    {
      "name": "alice",
      "run_at": "2026-04-28T15:00:00Z",
      "provenance_hash": "7f3afdc31b3bb0d6c5816622758a297c2c28f2a0d011696616b962555b55e2d1",
      "score": 0.7415
    }
  ]
}
```

The leaderboard surfaces a "Reproduced by" column for results with
≥1 confirmed entry.
