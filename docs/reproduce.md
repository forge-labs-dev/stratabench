# Reproducing stratabench results

stratabench is reproducible by construction: every published score is
paired with a provenance hash that anchors the entire methodology
(dataset version, prompt template, decoding params, harness code,
environment lockfile). Match the hash and you've matched the
methodology. The numbers themselves may drift a percentage point
because closed-API inference isn't perfectly deterministic — that's
expected and is what makes the reproduction proof valuable.

This is the step-by-step.

## What you'll need

- **Strata** — the notebook runtime stratabench is built on.
  See [strata install](https://forge-labs-dev.github.io/strata/getting-started/installation/).
- **One or more provider API keys** for whatever model(s) you're
  scoring. The registry covers OpenAI, Anthropic, Google, Together,
  and Mistral; you only need keys for the providers you'll actually
  hit.
- **A free disk budget** of ~5 GB (HuggingFace dataset cache + the
  notebook's uv venv).

## 1. Clone at the right commit

stratabench provenance hashes match within a commit. To reproduce a
published score, clone the same commit hash:

```bash
git clone https://github.com/forge-labs-dev/stratabench.git
cd stratabench
git checkout <COMMIT_HASH>   # the SHA the published score cites
```

The commit hash is printed in every score's `provenance` field in
`results/`.

## 2. Open one notebook

stratabench has one notebook per benchmark. Pick the one whose score
you're reproducing — say MMLU:

```
notebook/stratabench-mmlu/
```

Point your local Strata server's `STRATA_NOTEBOOK_STORAGE_DIR` at
`stratabench/notebook` and use **Open Existing** to open
`stratabench-mmlu`.

## 3. Configure the model

Each eval notebook ships with `gpt-4o-mini` as the default model.
Change the `MODEL_ID` constant in the inference cell to the model
whose score you're reproducing — e.g. `claude-sonnet-4-6`,
`gemini-2.5-pro`, `llama-3.3-70b-instruct`. The registry of supported
IDs is in
[`src/stratabench/models.py`](https://github.com/forge-labs-dev/stratabench/blob/main/src/stratabench/models.py).

In the Runtime panel, set the corresponding API key:

| Provider | Env var |
|---|---|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Google | `GEMINI_API_KEY` |
| Together | `TOGETHER_API_KEY` |
| Mistral | `MISTRAL_API_KEY` |

## 4. Choose smoke vs. full

Each eval's dataset cell has a `MAX_QUESTIONS` (or `MAX_PROBLEMS`,
or `MAX_PROMPTS`) constant near the top. For a smoke run, leave it at
the small default (~30). For a publication-grade reproduction, set it
to `None`.

A smoke run on `gpt-4o-mini` is typically under a dollar; a full run
across the bundle is typically $10–$30 depending on model.

## 5. Run all cells

Click **Run All**. The score cell prints:

- The headline number (e.g. `mmlu_redux_2_0 (macro): 0.7234`).
- The model ID and number of questions scored.
- The provenance hash (visible in the cell's artifact metadata).

## 6. Compare to the published score

Find the published score in `results/<eval>_<model>.json`:

```json
{
  "eval_name": "mmlu_redux_2_0_generative_zeroshot",
  "model_id": "claude-sonnet-4-6",
  "score": 0.7421,
  "n": 5712,
  "provenance_hash": "7f3afdc31b3bb0d6c5816622758a297c2c28f2a0d011696616b962555b55e2d1",
  "stratabench_commit": "abc1234",
  "run_at": "2026-04-27T10:00:00Z",
  "details": {...}
}
```

Two things should match:

1. **Provenance hash exact match.** If yours differs, your methodology
   chain differs from the published one — usually because you're on a
   different commit, or the notebook env's `uv.lock` differs (perhaps a
   transitive dep updated).

2. **Numeric score within ~1 percentage point.** Closed APIs aren't
   bit-deterministic even at temperature 0, and HumanEval timeouts can
   flake on slower hardware. ±1 point is normal. Larger gaps suggest
   something material is different.

If both match, you've reproduced. Open a PR adding your `scores.json`
to `results/` (see [Results format](results-format.md) for the schema)
and we'll list you on the leaderboard's "Reproduced by" column.

## Common gotchas

**"My provenance hash doesn't match."**
Check `git rev-parse HEAD` is the cited commit. Check you didn't edit
any cell. Check `notebook/<eval>/uv.lock` matches the committed one
(no manual `uv add` since clone).

**"My score is 5+ points off."**
- Did you change `temperature` or `max_tokens` in the registry?
  Those bake into the hash.
- Did the provider rotate the model behind the same ID? OpenAI does
  this occasionally; checking the model card date on their dashboard
  can help diagnose.
- Are you on the same dataset version? `datasets` may have updated
  the underlying data. Pin via the `uv.lock` in the notebook.

**"HumanEval failed with timeouts."**
The per-task timeout is 10 seconds. Slow CI runners can hit it. Bump
`PER_TASK_TIMEOUT_SECONDS` in the score cell if needed; document the
change in your reproduction PR.

**"My API key works for chat but the eval errors."**
Most likely the registry's model ID isn't valid on your tier (e.g.
`gpt-4o` requires a paid OpenAI account; `claude-opus-4-7` requires
Anthropic API access). Check the provider's model availability for
your account.

## Reporting a reproduction

Open a PR to `forge-labs-dev/stratabench` that adds your
`scores.json` files under `results/`. Include:

1. The `scores.json` payload with your provenance hashes.
2. A note in the PR body about your environment (OS, Python version,
   commit you ran).
3. Any deviations you had to make (e.g. timeout bumps).

We list confirmed reproductions on the leaderboard with the
reproducer's name and date.
