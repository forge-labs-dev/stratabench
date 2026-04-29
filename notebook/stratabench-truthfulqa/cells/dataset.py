# @name Dataset (TruthfulQA-mc, mc1)
#
# TruthfulQA tests whether models reproduce common falsehoods when asked
# adversarial questions. The ``multiple_choice`` config has two scoring
# variants: mc1 (exactly one correct answer per question, 2–13 options)
# and mc2 (multiple correct answers, scored by total correct-mass). We
# follow lm-eval's ``truthfulqa_mc1`` for v1 — single ground-truth makes
# the prompt and scorer cleaner.
#
# Source spec (cited as part of the methodology):
#   - Dataset: truthfulqa/truthful_qa (config "multiple_choice")
#   - Reference: https://huggingface.co/datasets/truthfulqa/truthful_qa
#   - Paper: arXiv:2109.07958
#
# MAX_QUESTIONS gates the smoke run; the full mc1 split is 817 questions.

import pandas as pd
from datasets import load_dataset

DATASET_ID = "truthfulqa/truthful_qa"
MAX_QUESTIONS: int | None = 30  # smoke run; bump to None for full 817

ds = load_dataset(DATASET_ID, "multiple_choice", split="validation")
df = ds.to_pandas()
df["idx"] = range(len(df))

# mc1_targets is a dict-of-arrays per HF spec; we expose the choices and
# the gold index so prompts.py and score.py don't need to re-parse.
def _gold_index(row) -> int:
    labels = list(row["mc1_targets"]["labels"])
    if labels.count(1) != 1:
        raise ValueError(f"mc1 row {row['idx']} has {labels.count(1)} correct labels (expected 1)")
    return labels.index(1)


def _choices(row) -> list[str]:
    return list(row["mc1_targets"]["choices"])


df["choices"] = df.apply(_choices, axis=1)
df["gold_index"] = df.apply(_gold_index, axis=1)
df["n_choices"] = df["choices"].map(len)

truthfulqa_questions = df[["idx", "question", "choices", "gold_index", "n_choices"]]
if MAX_QUESTIONS is not None:
    truthfulqa_questions = truthfulqa_questions.head(MAX_QUESTIONS).reset_index(drop=True)

print(f"truthfulqa_questions: {len(truthfulqa_questions)} mc1 items loaded from {DATASET_ID}")
print(f"  choice-count distribution: {truthfulqa_questions['n_choices'].value_counts().to_dict()}")
truthfulqa_questions.head()
