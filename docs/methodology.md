# stratabench methodology

This document will describe the v1 eval bundle, what is held constant
across runs, what is allowed to drift, and how to verify a third-party
reproduction.

## v1 eval bundle (planned)

| Eval | Source | Type | What it measures |
|------|--------|------|-------------------|
| MMLU-redux | TIGER-Lab | Multiple choice | World knowledge |
| GSM8K | OpenAI | Generative + exact-match | Grade-school math |
| HumanEval | OpenAI | Code generation, unit-tested | Function synthesis |
| IFEval | Google | Generative + rule-checked | Instruction following |
| TruthfulQA-mc | Lin et al. | Multiple choice | Factuality |
| Schema adherence | This repo | Generative + JSON Schema | Structured output reliability |

## Reproduction protocol

Coming with v1 ship.
