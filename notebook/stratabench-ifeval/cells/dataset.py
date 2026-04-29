# @name Dataset (IFEval)
#
# Loads Google's IFEval — instruction-following benchmark where each
# prompt encodes one or more "instructions" (rule-based constraints) the
# response must satisfy. Examples: "respond in fewer than 100 words",
# "include the keyword 'sunset' at least three times", "wrap your answer
# in <<...>>", etc.
#
# Source spec (cited as part of the methodology):
#   - Dataset: google/IFEval
#   - Reference: https://huggingface.co/datasets/google/IFEval
#   - Paper: arXiv:2311.07911
#
# Each row carries:
#   - prompt: the instruction sent to the model
#   - instruction_id_list: list of rule names the response must satisfy
#   - kwargs: list of dicts (one per id) with the rule's arguments
#
# Coverage: stratabench v1 implements 18 of IFEval's ~25 rule types
# (see rules.py). Prompts that require any uncovered rule are *skipped*
# at score time — not penalized — and the coverage % is reported.
#
# MAX_PROMPTS gates the smoke run; the full IFEval set is 541 prompts.

import pandas as pd
from datasets import load_dataset

DATASET_ID = "google/IFEval"
MAX_PROMPTS: int | None = 30  # smoke run; bump to None for the full 541

ds = load_dataset(DATASET_ID, split="train")
df = ds.to_pandas()
df["idx"] = range(len(df))

# Determine coverage per row: which prompts can stratabench score given
# the rule set in rules.py? "covered" = every rule the prompt needs is
# in our RULES registry.
covered_ids = set(RULES.keys())


def _is_covered(row) -> bool:
    return all(rid in covered_ids for rid in row["instruction_id_list"])


df["covered"] = df.apply(_is_covered, axis=1)
ifeval_prompts = df[["idx", "key", "prompt", "instruction_id_list", "kwargs", "covered"]]

if MAX_PROMPTS is not None:
    ifeval_prompts = ifeval_prompts.head(MAX_PROMPTS).reset_index(drop=True)

n_total = len(ifeval_prompts)
n_covered = int(ifeval_prompts["covered"].sum())
print(f"ifeval_prompts: {n_total} prompts loaded from {DATASET_ID}")
print(f"  covered (all rules implemented): {n_covered} ({n_covered / n_total:.1%})")
print(f"  skipped (uncovered rule): {n_total - n_covered}")
ifeval_prompts.head()
