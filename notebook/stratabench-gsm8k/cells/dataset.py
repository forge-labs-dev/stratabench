# @name Dataset (GSM8K)
#
# Loads the GSM8K test split from HuggingFace. GSM8K is OpenAI's
# grade-school math word-problem benchmark — 1319 problems where the
# answer is a single integer reached through multi-step arithmetic
# reasoning.
#
# Source spec (cited as part of the methodology):
#   - Dataset: openai/gsm8k (config "main")
#   - Reference: https://huggingface.co/datasets/openai/gsm8k
#   - Paper: arXiv:2110.14168
#
# The HuggingFace ``answer`` field is the full chain-of-thought reasoning
# followed by ``#### N`` where N is the gold integer. We extract that N
# at load time so downstream scoring is a clean numeric comparison.
#
# MAX_QUESTIONS gates the smoke run; bump to None for a full publication
# run (~$0.10 of gpt-4o-mini, ~5 minutes synchronous).

import re

import pandas as pd
from datasets import load_dataset

DATASET_ID = "openai/gsm8k"
MAX_QUESTIONS: int | None = 30  # smoke run; bump to None for the full 1319

ds = load_dataset(DATASET_ID, "main", split="test")
df = ds.to_pandas()


_GOLD_RE = re.compile(r"####\s*(-?\d+(?:\.\d+)?)")


def extract_gold(answer: str) -> str | None:
    """Pull the integer that follows ``#### `` in the answer field."""
    m = _GOLD_RE.search(answer)
    return m.group(1) if m else None


df["gold"] = df["answer"].map(extract_gold)
missing = df["gold"].isna().sum()
if missing:
    raise RuntimeError(f"GSM8K dataset has {missing} answers missing the '####' marker")

df["idx"] = range(len(df))
gsm8k_questions = df[["idx", "question", "answer", "gold"]]

if MAX_QUESTIONS is not None:
    gsm8k_questions = gsm8k_questions.head(MAX_QUESTIONS).reset_index(drop=True)

print(f"gsm8k_questions: {len(gsm8k_questions)} problems loaded from {DATASET_ID}/main/test")
gsm8k_questions.head()
