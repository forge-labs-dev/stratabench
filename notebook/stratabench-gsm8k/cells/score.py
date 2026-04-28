# @name Score (numeric exact-match)
#
# Two-stage answer extraction:
#
#   1. Prefer the canonical ``#### N`` form the prompt asks for. If the
#      model emitted it, we trust it.
#   2. Fall back to the last number in the response. Models often write
#      "the answer is 42." or trail off without the marker — last-number
#      matches the lm-eval gsm8k_cot scorer's regex behavior and rescues
#      most of those cases.
#
# We compare numerically (not as strings) so "42" / "42.0" / "42,000"
# normalize correctly. Strings that won't parse score wrong.
#
# The output is an EvalResult artifact whose provenance hash is the
# audit identifier for the entire chain (dataset → prompts → inference
# → scoring).

import re
from decimal import Decimal, InvalidOperation

_HASHED_RE = re.compile(r"####\s*(-?\d+(?:\.\d+)?)")
_NUMBER_RE = re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?")


def parse_answer(raw: str) -> str | None:
    """Extract the model's final numeric answer from its response."""
    m = _HASHED_RE.search(raw)
    if m:
        return m.group(1)
    matches = _NUMBER_RE.findall(raw)
    return matches[-1] if matches else None


def numeric_equal(a: str | None, b: str | None) -> bool:
    if a is None or b is None:
        return False
    try:
        return Decimal(a.replace(",", "")) == Decimal(b.replace(",", ""))
    except (InvalidOperation, AttributeError):
        return False


scored = inference.merge(
    prompts[["idx", "gold"]],
    on="idx",
    how="left",
    validate="one_to_one",
)
scored["parsed"] = scored["raw_response"].map(parse_answer)
scored["correct"] = [
    numeric_equal(p, g) for p, g in zip(scored["parsed"], scored["gold"])
]

micro_score = float(scored["correct"].mean())
parse_failure_rate = float(scored["parsed"].isna().mean())

from stratabench import EvalResult

gsm8k_score = EvalResult(
    eval_name="gsm8k_cot_zeroshot",
    model_id=spec.id,
    score=micro_score,
    n=len(scored),
    details={
        "parse_failure_rate": parse_failure_rate,
        "n_correct": int(scored["correct"].sum()),
    },
)

print(f"\ngsm8k_cot_zeroshot: {micro_score:.4f}  (parse_fail: {parse_failure_rate:.2%})")
print(f"model: {spec.id}")
print(f"n: {len(scored)} problems, {int(scored['correct'].sum())} correct")
gsm8k_score
