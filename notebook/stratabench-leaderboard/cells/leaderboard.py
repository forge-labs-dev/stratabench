# @name Leaderboard table
#
# Pivots the published-results frame into a (model × eval) leaderboard
# table. Empty grid → render the eval bundle with "—" placeholders so a
# visitor still sees what stratabench measures even before any scores
# have been published.

import pandas as pd

# Canonical eval bundle order — matches docs/methodology.md so the
# table reads consistently across the docs site and the notebook.
EVAL_ORDER = [
    "mmlu_redux_2_0_generative_zeroshot",
    "gsm8k_cot_zeroshot",
    "humaneval_instruct_pass_at_1",
    "truthfulqa_mc1_generative_zeroshot",
    "schema_adherence_v1",
    "ifeval_prompt_strict_zeroshot_subset",
]

EVAL_DISPLAY = {
    "mmlu_redux_2_0_generative_zeroshot": "MMLU-redux",
    "gsm8k_cot_zeroshot": "GSM8K",
    "humaneval_instruct_pass_at_1": "HumanEval",
    "truthfulqa_mc1_generative_zeroshot": "TruthfulQA-mc1",
    "schema_adherence_v1": "Schema",
    "ifeval_prompt_strict_zeroshot_subset": "IFEval",
}

if len(results) == 0:
    print("No published results yet — see docs/reproduce.md for how to publish a score.")
    leaderboard = pd.DataFrame(columns=["model_id"] + [EVAL_DISPLAY[e] for e in EVAL_ORDER])
else:
    pivot = results.pivot_table(
        index="model_id",
        columns="eval_name",
        values="score",
        aggfunc="first",
    )
    # Reorder columns to the canonical bundle, fill missing evals.
    for eval_name in EVAL_ORDER:
        if eval_name not in pivot.columns:
            pivot[eval_name] = float("nan")
    pivot = pivot[EVAL_ORDER]
    pivot.columns = [EVAL_DISPLAY[c] for c in pivot.columns]
    pivot = pivot.reset_index()

    # Sort rows by mean score (descending), NaNs last.
    score_cols = [EVAL_DISPLAY[e] for e in EVAL_ORDER]
    pivot["_mean"] = pivot[score_cols].mean(axis=1, skipna=True)
    pivot = pivot.sort_values("_mean", ascending=False, na_position="last").drop(columns=["_mean"])
    leaderboard = pivot.reset_index(drop=True)

# Pretty-print as percentages for the table view.
display_table = leaderboard.copy()
for col in display_table.columns:
    if col == "model_id":
        continue
    display_table[col] = display_table[col].map(
        lambda v: f"{v * 100:5.1f}%" if pd.notna(v) else "—"
    )

print("\nstratabench leaderboard")
print("=" * 80)
print(display_table.to_string(index=False))
print("=" * 80)
print(f"\n{len(results)} scores published across {leaderboard['model_id'].nunique()} model(s)")

leaderboard
