# stratabench

**Reproducible, content-addressed LLM evaluations with auditable provenance.**

Every benchmark score this harness produces is paired with a provenance
hash covering the eval dataset version, prompt template, decoding
configuration, model identifier, and harness code. Same inputs + same
harness = same hash. Match the hash and you've reproduced the
methodology — even if the numbers themselves drift slightly because of
provider non-determinism.

stratabench is built on [Strata](https://forge-labs-dev.github.io/strata/).
Each benchmark lives in its own Strata notebook; reading the cells is
reading the spec. No `import lm_eval` — the methodology is in your face.

## v1 eval bundle

| Eval | Notebook | Type | What it measures |
|------|----------|------|-------------------|
| MMLU-redux | `notebook/stratabench-mmlu/` | Multiple choice | World knowledge |
| GSM8K | `notebook/stratabench-gsm8k/` | Generative + exact-match | Grade-school math |
| HumanEval | `notebook/stratabench-humaneval/` | Code, unit-tested | Function synthesis |
| TruthfulQA-mc1 | `notebook/stratabench-truthfulqa/` | Multiple choice | Factuality |
| Schema adherence | `notebook/stratabench-schema/` | Generative + jsonschema | Structured output |
| IFEval | `notebook/stratabench-ifeval/` | Generative + rule-checked | Instruction following |
| Leaderboard | `notebook/stratabench-leaderboard/` | (read-only) | Joins published scores |

## Quickstart

```bash
git clone https://github.com/forge-labs-dev/stratabench.git
cd stratabench

# Point a Strata server at the notebook directory and open one of the
# eval notebooks in the UI.
STRATA_NOTEBOOK_STORAGE_DIR=$(pwd)/notebook strata-server
```

Then in the Strata UI:

1. Click **Open Existing**, pick `stratabench-mmlu` (or any eval).
2. Set your provider key in the Runtime panel (e.g. `OPENAI_API_KEY`).
3. Hit **Run All**. The score cell prints the headline number and the
   provenance hash that anchors the entire methodology chain.

For full setup, see
[Reproducing results](docs/reproduce.md).

## Documentation

- [**Methodology**](docs/methodology.md) — full spec for each eval, including
  deviations from canonical lm-eval and the limitations of v1.
- [**Reproducing results**](docs/reproduce.md) — step-by-step.
- [**Results format**](docs/results-format.md) — JSON schema for
  published scores, contributor flow.
- [Live docs](https://forge-labs-dev.github.io/stratabench/) — same
  content, rendered.

## Repo layout

```
stratabench/
├── src/stratabench/        # ModelSpec, REGISTRY, chat_completion, EvalResult,
│                           # publish_score — the plumbing every eval reuses
├── notebook/
│   ├── stratabench-mmlu/        # one eval per directory
│   ├── stratabench-gsm8k/
│   ├── stratabench-humaneval/
│   ├── stratabench-truthfulqa/
│   ├── stratabench-schema/
│   ├── stratabench-ifeval/
│   └── stratabench-leaderboard/ # joins published scores into a table
├── results/                # published score JSONs land here
└── docs/                   # methodology + reproduction + format spec
```

## Status

Pre-v1.0. Eval bundle is feature-complete. Eleven models in the
registry across OpenAI, Anthropic, Google, Together, and Mistral.
First publication run lands as JSON files in `results/`.

## License

MIT. See [LICENSE](LICENSE).
