# @name Score (strict prompt-level pass)
#
# IFEval has two scoring tiers: prompt-level strict (all instructions in
# a prompt must pass) and instruction-level loose (per-instruction
# pass). We report prompt-level strict for v1 — it's the harder, more
# meaningful number and matches the headline metric in the IFEval paper.
#
# Coverage rule: only score prompts whose every instruction_id is in
# our RULES registry (see dataset cell). Uncovered prompts are excluded
# from the score and counted separately. The coverage percentage is
# reported alongside the score so a reader sees how representative the
# number is.

import pandas as pd

joined = inference.merge(
    ifeval_prompts[["idx", "instruction_id_list", "kwargs", "covered"]],
    on="idx",
    how="left",
    validate="one_to_one",
)


def score_one(row) -> dict:
    if not row["covered"]:
        return {"status": "skipped", "passed": None, "n_passed": None, "n_total": None}
    response = row["raw_response"]
    ids = list(row["instruction_id_list"])
    kwargs_list = list(row["kwargs"])
    if len(ids) != len(kwargs_list):
        return {
            "status": "malformed",
            "passed": None,
            "n_passed": None,
            "n_total": len(ids),
        }
    n_passed = 0
    for rid, kw in zip(ids, kwargs_list):
        # The dataset packs kwargs as a dict possibly containing other
        # rules' arguments alongside ours; the rule itself only reads
        # what it needs.
        try:
            ok = RULES[rid](response, kw or {})
        except Exception:
            ok = False
        if ok:
            n_passed += 1
    return {
        "status": "scored",
        "passed": n_passed == len(ids),
        "n_passed": n_passed,
        "n_total": len(ids),
    }


score_rows = joined.apply(lambda row: pd.Series(score_one(row)), axis=1)
scored = pd.concat([joined.reset_index(drop=True), score_rows.reset_index(drop=True)], axis=1)

n_total = len(scored)
n_scored = int((scored["status"] == "scored").sum())
n_skipped = int((scored["status"] == "skipped").sum())
n_malformed = int((scored["status"] == "malformed").sum())

scored_only = scored[scored["status"] == "scored"]
prompt_strict = float(scored_only["passed"].mean()) if len(scored_only) else 0.0
instruction_micro = (
    float(scored_only["n_passed"].sum() / scored_only["n_total"].sum())
    if scored_only["n_total"].sum()
    else 0.0
)

from stratabench import EvalResult

ifeval_score = EvalResult(
    eval_name="ifeval_prompt_strict_zeroshot_subset",
    model_id=spec.id,
    score=prompt_strict,
    n=n_scored,
    details={
        "instruction_micro": instruction_micro,
        "coverage_fraction": n_scored / n_total if n_total else 0.0,
        "n_total_dataset": n_total,
        "n_scored": n_scored,
        "n_skipped_uncovered": n_skipped,
        "n_malformed": n_malformed,
        "supported_rules": sorted(RULES.keys()),
    },
)

print(f"\nifeval (prompt-strict, covered subset): {prompt_strict:.4f}")
print(f"  instruction-micro on covered subset: {instruction_micro:.4f}")
print(f"  coverage: {n_scored}/{n_total} prompts ({n_scored / n_total:.1%}) — {n_skipped} skipped")
print(f"  model: {spec.id}")
ifeval_score
