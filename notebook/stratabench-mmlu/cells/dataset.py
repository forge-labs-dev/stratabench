# @name Dataset (MMLU-redux)
#
# Loads the MMLU-redux 2.0 test set from HuggingFace. MMLU-redux is the
# Edinburgh DAWG group's manual cleaning of the original Hendrycks MMLU,
# correcting label errors and removing genuinely-broken questions.
#
# Source spec (cited as part of the methodology):
#   - Dataset: edinburgh-dawg/mmlu-redux-2.0
#   - Reference: https://huggingface.co/datasets/edinburgh-dawg/mmlu-redux-2.0
#   - Paper: arXiv:2406.04127
#
# We load *all* subjects and concatenate into a single DataFrame keyed by
# (subject, idx). Iteration is deterministic via sorted-subjects then
# arrival order within each subject — the same order a reproducer's run
# will see, which matters because Strata's cell hash includes input
# bytes.
#
# MAX_QUESTIONS gates the smoke run: keep small while iterating on the
# pipeline, set to None for the publication run. Changing this re-stamps
# every downstream artifact (correctly).

import pandas as pd
from datasets import get_dataset_config_names, load_dataset

DATASET_ID = "edinburgh-dawg/mmlu-redux-2.0"
MAX_QUESTIONS: int | None = 30  # smoke run; bump to None for the full ~5700

subjects = sorted(get_dataset_config_names(DATASET_ID))
print(f"loaded subject list: {len(subjects)} subjects from {DATASET_ID}")

frames: list[pd.DataFrame] = []
for subject in subjects:
    ds = load_dataset(DATASET_ID, subject, split="test")
    df = ds.to_pandas()
    df["subject"] = subject
    df["idx"] = range(len(df))
    frames.append(df)

mmlu_questions = pd.concat(frames, ignore_index=True)

# Stable column subset — extra columns the dataset ships (error_type, etc.)
# can drift between dataset versions; we don't want those edits to
# invalidate our hashes when they aren't actually part of the question.
mmlu_questions = mmlu_questions[["subject", "idx", "question", "choices", "answer"]]

if MAX_QUESTIONS is not None:
    # Stratified head: take up to ceil(MAX/N) per subject so we cover the
    # universe instead of biasing toward the alphabetically-first ones.
    per_subject = max(1, MAX_QUESTIONS // len(subjects))
    mmlu_questions = (
        mmlu_questions.groupby("subject", group_keys=False)
        .head(per_subject)
        .head(MAX_QUESTIONS)
        .reset_index(drop=True)
    )

print(f"mmlu_questions: {len(mmlu_questions)} questions across {mmlu_questions['subject'].nunique()} subjects")
mmlu_questions.head()
