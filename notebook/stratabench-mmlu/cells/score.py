# @name Score (exact-letter match)
#
# Parse each model response for a single A/B/C/D answer letter and compare
# against the gold answer. The model is asked to emit only a letter, but
# in practice it sometimes wraps it ("The answer is A.", "A) ...", "A\n").
# Scoring rule:
#
#   1. Strip whitespace.
#   2. If the first non-whitespace character is a valid letter, that's
#      the answer.
#   3. Otherwise scan for the first standalone letter token (e.g. "A.",
#      "A)", "A:", "**A**"). This matches lm-eval's `*_generative`
#      letter-extraction logic.
#   4. If no valid letter is found, the question is scored *wrong*.
#      We don't retry — silent letter-extraction failures should hurt
#      the score, that's the point of strict scoring.
#
# The output is a single EvalResult artifact. Its provenance hash is the
# audit identifier — match the hash and you've matched the entire chain
# (dataset → prompts → inference → scoring).

import re

import pandas as pd

VALID_LETTERS = {"A", "B", "C", "D"}
_LETTER_TOKEN_RE = re.compile(r"\b([ABCD])\b")


def parse_letter(raw: str) -> str | None:
    s = raw.strip()
    if not s:
        return None
    head = s[0]
    if head in VALID_LETTERS:
        return head
    m = _LETTER_TOKEN_RE.search(s)
    return m.group(1) if m else None


scored = inference.merge(
    prompts[["subject", "idx", "gold_letter"]],
    on=["subject", "idx"],
    how="left",
    validate="one_to_one",
)
scored["parsed_letter"] = scored["raw_response"].map(parse_letter)
scored["correct"] = scored["parsed_letter"] == scored["gold_letter"]

# Macro-average across subjects (each subject contributes equally,
# regardless of how many questions it has). lm-eval reports macro for
# MMLU; we match.
per_subject = scored.groupby("subject")["correct"].mean()
macro_score = float(per_subject.mean())
micro_score = float(scored["correct"].mean())
parse_failure_rate = float(scored["parsed_letter"].isna().mean())

from stratabench import EvalResult

mmlu_redux_score = EvalResult(
    eval_name="mmlu_redux_2_0_generative_zeroshot",
    model_id=spec.id,
    score=macro_score,
    n=len(scored),
    details={
        "micro_score": micro_score,
        "parse_failure_rate": parse_failure_rate,
        "per_subject": per_subject.round(4).to_dict(),
    },
)

print(f"\nmmlu_redux_2_0 (macro): {macro_score:.4f}  (micro: {micro_score:.4f}, parse_fail: {parse_failure_rate:.2%})")
print(f"model: {spec.id}")
print(f"n: {len(scored)} questions across {scored['subject'].nunique()} subjects")
mmlu_redux_score
