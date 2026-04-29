# stratabench

**Reproducible, content-addressed LLM evaluations with auditable provenance.**

Every benchmark score this harness produces is paired with a provenance
hash that covers the eval dataset version, prompt template, decoding
configuration, model identifier, and harness code. Same inputs + same
harness = same hash. Match the hash and you've matched the methodology
end-to-end — even if the numbers themselves drift slightly because of
provider non-determinism.

stratabench is built on [Strata](https://forge-labs-dev.github.io/strata/),
the content-addressed notebook runtime that gives every cell output a
deterministic hash. Each eval lives in its own Strata notebook; reading
the cells is reading the spec.

## What it measures

The v1 bundle covers six benchmarks across capability axes that matter
for app builders:

| Eval | Type | What it measures |
|------|------|-------------------|
| MMLU-redux | Multiple choice | World knowledge |
| GSM8K | Generative + exact-match | Grade-school math |
| HumanEval | Code, unit-tested | Function synthesis |
| TruthfulQA-mc1 | Multiple choice | Factuality / falsehood resistance |
| Schema adherence | Generative + jsonschema | Structured output reliability |
| IFEval | Generative + rule-checked | Instruction following |

See [Methodology](methodology.md) for the full spec, including
deviations from canonical lm-eval and the limitations of v1.

## What's different about it

- **One hash per score.** Strata's per-cell provenance hash combines
  every input that affects a score: dataset version, prompt template,
  decoding config, model ID, harness commit, environment lockfile.
  Match the hash, you've matched the chain.
- **Cells are the spec.** No `import lm_eval`. Open one notebook, read
  five cells (~30 lines each), and you have the entire methodology.
- **Cache-aware re-runs.** Adding a model to the registry doesn't
  re-pay for evals you've already computed — only the new model's
  slice misses Strata's cache.
- **Honest about deviations.** Where the methodology differs from
  lm-eval (closed-API generation-based MC scoring, IFEval rule
  coverage, etc.) it says so loudly in the cell and the methodology
  doc.

## How to use it

- **Reproduce a published score.** Clone the repo at the cited commit,
  open the notebook, set your provider key, run all cells. Compare
  hashes. See [Reproducing results](reproduce.md).
- **Score a new model.** Add it to `src/stratabench/models.py`,
  run any eval notebook with `MODEL_ID = "<your-model>"`. Strata
  caches everything else; only your new model's slice runs.
- **Add a new eval.** Make a new notebook directory `stratabench-<eval>/`
  with five cells (helpers / dataset / prompts / inference / score).
  The library's plumbing is the only shared code; the methodology is
  yours.

## Status

Pre-v1.0. The full eval bundle is implemented; the model registry
covers eleven frontier and open models; published results land in
[`results/`](https://github.com/forge-labs-dev/stratabench/tree/main/results)
as runs accumulate. See the GitHub repo for the live state.
