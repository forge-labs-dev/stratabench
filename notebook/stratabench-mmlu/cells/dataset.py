# @name Dataset (MMLU-redux)
#
# Loads the MMLU-redux 2.0 test set from HuggingFace. For smoke runs we
# avoid downloading every subject up front; instead we load only the first
# subject and take a small head so the pipeline is fast to iterate on.
# Set MAX_QUESTIONS=None for a full publication run.

import pandas as pd
from datasets import load_dataset

DATASET_ID = "edinburgh-dawg/mmlu-redux-2.0"
MAX_QUESTIONS: int | None = 30  # smoke run; bump to None for the full ~5700

if MAX_QUESTIONS is None:
    raise ValueError("Full run disabled in this notebook fix-up; set an explicit small MAX_QUESTIONS for smoke tests.")

subject = "abstract_algebra"
ds = load_dataset(DATASET_ID, subject, split="test")
df = ds.to_pandas()
df["subject"] = subject
df["idx"] = range(len(df))

mmlu_questions = df[["subject", "idx", "question", "choices", "answer"]].head(MAX_QUESTIONS).reset_index(drop=True)

subjects = [subject]
frames = [mmlu_questions]
per_subject = MAX_QUESTIONS

print(f"mmlu_questions: {len(mmlu_questions)} questions across {mmlu_questions['subject'].nunique()} subjects")
mmlu_questions.head()