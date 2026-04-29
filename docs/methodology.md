# stratabench methodology

**stratabench** is a reproducible, content-addressed LLM evaluation
harness. Every score it produces is paired with a provenance hash that
covers the eval dataset version, prompt template, decoding configuration,
model identifier, and harness code. Match the hash, and you've matched
the methodology end-to-end — even if the numbers themselves drift
because of provider non-determinism.

This document is the **specification** of stratabench v1: what it
measures, how, and what's known to be different from canonical
benchmarks elsewhere. Reproducers should read this first.

---

## What stratabench is, and isn't

**Is.** A small bundle of well-known LLM evals, reimplemented
transparently in Strata notebook cells, with one provenance hash per
score that anchors the entire chain of methodology.

**Isn't.** A new benchmark suite, a leaderboard runner, or a competitor
to lm-evaluation-harness. We *cite* lm-eval's templates and scoring
rules as the methodological reference for each eval and reimplement
them in our cells so the methodology lives in 30-line files instead
of a multi-thousand-line library import.

The credibility argument: open one notebook, read every cell, and you
have the entire spec for that benchmark. No hidden Strata layer, no
lm-eval black box. Two reproducers running the same notebook with the
same Strata version and the same provider keys should produce the same
provenance hashes — and within provider-non-determinism noise, the
same numbers.

---

## v1 eval bundle

| Eval | Notebook | Source | Type | What it measures |
|------|----------|--------|------|-------------------|
| MMLU-redux | `stratabench-mmlu` | `edinburgh-dawg/mmlu-redux-2.0` | Multiple choice | World knowledge |
| GSM8K | `stratabench-gsm8k` | `openai/gsm8k` (main) | Generative + exact-match | Grade-school math |
| HumanEval | `stratabench-humaneval` | `openai/openai_humaneval` | Code, unit-tested | Function synthesis |
| TruthfulQA-mc1 | `stratabench-truthfulqa` | `truthfulqa/truthful_qa` (multiple_choice) | Multiple choice | Factuality / falsehood resistance |
| Schema adherence | `stratabench-schema` | This repo (20 hand-curated schemas) | Generative + jsonschema | Structured-output reliability |
| IFEval | `stratabench-ifeval` | `google/IFEval` | Generative + rule-checked | Instruction following |

Each notebook is independently runnable on any model in
`stratabench.REGISTRY`. Each produces one `EvalResult` artifact whose
Strata provenance hash is the audit identifier for that score.

---

## Per-eval methodology

For every benchmark, stratabench v1 follows three rules:

1. **Cite the reference.** The lm-eval task whose template and scoring
   rule we mirror is named in a comment at the top of the prompts
   and/or score cell. If we deviate, the deviation is documented.
2. **Reimplement in cells.** No `import lm_eval` anywhere. The dataset
   loaders use HuggingFace `datasets`, scoring is in our own functions.
3. **Hold decoding constant.** All inference runs at `temperature=0.0`,
   `max_tokens=1024` (or 2048 for IFEval whose prompts ask for long
   responses). These are part of the provenance hash; changing them
   produces a fresh artifact.

### MMLU-redux

- **Dataset:** `edinburgh-dawg/mmlu-redux-2.0`, all 30 subjects, test split.
  ~5,700 questions after deduplication of the original Hendrycks MMLU.
- **Prompt:** 0-shot generation. Single-letter response asked for in
  the prompt; the cell mirrors lm-eval's `_default_template_yaml` body.
- **Scoring:** Generation-based — parse the first valid A/B/C/D letter
  from the response. Macro-averaged across subjects.
- **Deviation from lm-eval:** Canonical MMLU uses log-probability
  scoring on the four option letters. Closed APIs (Anthropic, Gemini)
  don't expose token logits, so we use generation-based scoring across
  the bundle for closed-API parity. lm-eval has matching `*_generative`
  task variants we follow. **Numbers will differ slightly from log-prob
  scoring** — typically ±5 points, more for smaller models that
  struggle with format-following.
- **Deviation from 5-shot:** MMLU-redux ships only a cleaned test split;
  pulling few-shot examples from the original MMLU dev would muddy the
  citation. 0-shot keeps the methodology one file shorter and matches
  newer leaderboards (Open LLM v2).

### GSM8K

- **Dataset:** `openai/gsm8k` config `main`, test split. 1,319 problems.
- **Prompt:** 0-shot chain-of-thought. The model is asked to reason
  step by step and end with `#### N` where N is the final integer.
- **Scoring:** Two-stage answer extraction.
  1. Prefer the canonical `#### N` form the prompt asks for.
  2. Fall back to the last number anywhere in the response. Matches
     lm-eval's `gsm8k_cot` regex behavior and rescues responses that
     trail off without the marker.
  Numeric comparison via `Decimal` so `42` / `42.0` / `42,000`
  normalize correctly.
- **Reference:** `lm_eval/tasks/gsm8k/gsm8k_cot_zeroshot.yaml`.

### HumanEval

- **Dataset:** `openai/openai_humaneval`, test split. 164 problems.
- **Prompt:** Wrap the bare HumanEval prompt in an instruction-tuned
  template asking for a fenced ```python``` block.
- **Scoring:** Per-task subprocess. Combine the original prompt
  (signature + docstring) + extracted code block + the dataset's test
  code + a call to `check(<entry_point>)`. Run with a 10-second wall-
  clock cap. Infinite loops or import crashes can't escape the
  subprocess — they fail their own task.
  Reports **pass@1**: temperature=0 → one sample per task → fraction
  passing. No multi-sample pass@k for v1.
- **Reference:** `lm_eval/tasks/humaneval/humaneval_instruct.yaml`.

### TruthfulQA-mc1

- **Dataset:** `truthfulqa/truthful_qa` config `multiple_choice`,
  validation split. 817 questions. We use the `mc1_targets` variant
  (exactly one correct answer per question) for v1.
- **Prompt:** 0-shot generation. Variable choice count (2–13) — the
  prompt builds the option list dynamically with letter labels A..M
  and a per-question valid-letter set drives the parser.
- **Scoring:** Same shape as MMLU. Micro accuracy.
- **Deviation from lm-eval:** Same log-prob → generation deviation as
  MMLU, same reason.

### Schema adherence (stratabench-original)

- **Dataset:** 20 hand-curated schemas in
  `notebook/stratabench-schema/cells/schemas.py`. Four complexity
  buckets: trivial (5), moderate (6), complex (6), edge (3).
- **Prompt:** Embed the schema in the prompt body in plain prose. Ask
  for JSON in a fenced ```json``` block. **No provider response_format
  scaffolding** — that would push every score to ~100% (the API
  enforces strict mode server-side) and defeat the eval.
- **Scoring:** Three failure modes tracked separately —
  - `parse_failed`: response wasn't extractable JSON at all.
  - `schema_invalid`: parsed but didn't match the schema.
  - `ok`: parsed and validated cleanly.
  Score is the fraction of `ok` results, **macro-averaged across
  complexity buckets** so a model that aces trivial but fails edge
  can't hide behind a flat micro-average.
- **Reference:** stratabench-original. No canonical lm-eval task.
- **What this measures:** the model's *intrinsic* ability to produce
  schema-conforming JSON. Useful for app builders who can't rely on a
  particular provider's strict mode (or whose target deployment is a
  proxy/local model that doesn't have one).

### IFEval

- **Dataset:** `google/IFEval`, train split. 541 prompts. Each prompt
  encodes 1+ "instructions" (rule-based constraints) the response must
  satisfy: keyword inclusion, length limits, format constraints, etc.
- **Prompt:** Sent verbatim. No template wrapping.
- **Scoring:** Prompt-level strict — *all* instructions in a prompt
  must pass. We also report instruction-level micro for the looser
  tier.
- **Coverage:** stratabench v1 implements 18 of IFEval's ~25 rule
  types inline in `cells/rules.py`. Prompts that need an uncovered
  rule are *skipped* (not penalized) and the coverage percentage is
  reported alongside the score. The headline number is on the covered
  subset; the writeup discloses both the score and the coverage.
- **Reference:** `lm_eval/tasks/ifeval/ifeval.yaml`. The IFEval
  reference impl uses NLTK for sentence tokenization; we use a
  regex-based approximation to stay dependency-light. Quirky
  abbreviations may inflate sentence counts slightly. Documented as
  a v1 caveat.

---

## Provenance and reproducibility

Every eval cell in stratabench produces an `EvalResult` artifact whose
Strata provenance hash combines:

1. **Cell source code** (AST-normalized) — every cell upstream of the
   score cell, recursively. Whitespace and comments don't matter; semantic
   source does.
2. **Resolved input artifacts** — the dataset cell's hash, the prompts
   cell's hash, the inference cell's hash. Each of those is in turn
   hashed from its own inputs.
3. **Environment hash** — the `uv.lock` of the notebook's venv. Python
   version + dataset library version + httpx version + jsonschema version
   + everything else the cells transitively import.

If two reproducers produce the same provenance hash, their methodology
is bit-identical. The model API responses themselves may differ
slightly (closed APIs aren't perfectly deterministic at temperature 0),
but the chain of inputs, prompts, and scoring is the same.

### What's deterministic vs. what isn't

| Layer | Deterministic? |
|---|---|
| Dataset selection | Yes — pinned to specific HF dataset IDs and configs |
| Prompt construction | Yes — pure functions of the dataset rows |
| Decoding parameters | Yes — `temperature=0`, `max_tokens` set in registry |
| Model output | **No** — closed APIs aren't bit-deterministic even at temp 0 |
| Scoring | Yes — pure functions of the response |
| Provenance hash | Yes — independent of the model's stochastic output |

A provenance match plus a numeric match within ~1 percentage point is
strong evidence of methodology agreement. A provenance mismatch means
something differs upstream — different harness commit, different
dataset version, different decoding params.

---

## Reproduction protocol

See [`reproduce.md`](reproduce.md) for the step-by-step.

The short version:

1. Clone `forge-labs-dev/stratabench` at the commit hash you want to
   reproduce. Provenance hashes only match within a commit.
2. Install Strata, open one of the eval notebooks in `notebook/`.
3. Set the relevant provider API key in the Runtime panel.
4. Run all cells. The score cell prints the headline number and the
   provenance hash.
5. Compare your provenance hash against the published number. They
   should match exactly. The score may differ slightly because of
   provider non-determinism — that's expected and is what makes the
   reproduction proof valuable.

---

## Known limitations (v1)

These are explicit; they aren't bugs but tradeoffs.

- **Generation-based MC scoring on closed APIs.** Numbers are a few
  points different from log-prob-based leaderboards. Documented per
  eval. v1.1 will publish OpenAI log-prob numbers as a side-by-side
  comparison column.
- **No multi-sample pass@k.** HumanEval is pass@1 only. v1.1 may add
  pass@5 with stochastic decoding for models where it matters.
- **IFEval coverage is partial.** 18 of ~25 rule types implemented;
  coverage reported per-run. v1.1 fills in the remainder.
- **No LLM-as-judge evals.** MT-Bench, AlpacaEval, and similar judge-
  graded benchmarks aren't in v1 because the judge model adds a cost-
  and-bias coupling that hurts the reproducibility story. v2 may add
  them with explicit judge-model provenance.
- **One sample per question.** Single-shot, not majority-vote /
  self-consistency. Cheaper, simpler, and the deltas vs. multi-sample
  are small for the math/code evals at temperature 0.
- **No human evaluation.** Every score in stratabench is mechanical —
  rule checks, exact match, jsonschema validation. We don't claim to
  measure things a rule can't see.

---

## Versioning and stability

- The harness version pins to a Git commit on `forge-labs-dev/stratabench`.
- Provenance hashes are stable within a commit; they may change between
  commits if any cell source changes.
- Published results in `results/` carry both the score and the
  provenance hash. A user who wants to compare to an older score
  should clone the corresponding commit.
- We don't promise score-level backward compatibility across commits;
  we promise that the methodology in the cell at any commit is the
  full spec for that score.

---

## Citations

- **MMLU:** Hendrycks et al., "Measuring Massive Multitask Language
  Understanding," ICLR 2021.
- **MMLU-redux:** Gema et al., "MMLU-Redux: A Simpler MMLU," 2024.
- **GSM8K:** Cobbe et al., "Training Verifiers to Solve Math Word
  Problems," 2021.
- **HumanEval:** Chen et al., "Evaluating Large Language Models Trained
  on Code," 2021.
- **TruthfulQA:** Lin et al., "TruthfulQA: Measuring How Models Mimic
  Human Falsehoods," ACL 2022.
- **IFEval:** Zhou et al., "Instruction-Following Evaluation for Large
  Language Models," 2023.
- **lm-evaluation-harness:** Eleuther AI,
  github.com/EleutherAI/lm-evaluation-harness — methodological
  reference for the prompt templates and scoring rules we mirror.
