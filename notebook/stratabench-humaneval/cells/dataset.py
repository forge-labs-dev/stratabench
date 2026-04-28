# @name Dataset (HumanEval)
#
# Loads OpenAI's HumanEval — 164 hand-written Python programming problems
# where each task ships with a function signature, a docstring, a
# canonical solution, and a set of unit tests that the model's
# implementation must pass.
#
# Source spec (cited as part of the methodology):
#   - Dataset: openai/openai_humaneval
#   - Reference: https://huggingface.co/datasets/openai/openai_humaneval
#   - Paper: arXiv:2107.03374 ("Evaluating Large Language Models Trained on Code")
#
# Each row carries:
#   - prompt: the function signature + docstring the model completes
#   - canonical_solution: reference implementation (we don't use it
#     for scoring; it's there for sanity)
#   - test: unit-test code the model's solution must pass
#   - entry_point: the function name to call
#
# MAX_PROBLEMS gates the smoke run; bump to None for the full 164.

import pandas as pd
from datasets import load_dataset

DATASET_ID = "openai/openai_humaneval"
MAX_PROBLEMS: int | None = 10  # smoke run; bump to None for the full 164

ds = load_dataset(DATASET_ID, split="test")
df = ds.to_pandas()
df["idx"] = range(len(df))

humaneval_problems = df[
    ["task_id", "idx", "prompt", "canonical_solution", "test", "entry_point"]
]

if MAX_PROBLEMS is not None:
    humaneval_problems = humaneval_problems.head(MAX_PROBLEMS).reset_index(drop=True)

print(f"humaneval_problems: {len(humaneval_problems)} problems loaded from {DATASET_ID}")
humaneval_problems[["task_id", "entry_point"]].head()
