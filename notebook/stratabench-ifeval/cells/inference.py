# @name Run inference (gpt-4o-mini)
# @timeout 3600
#
# IFEval prompts are direct instructions — no extra wrapping needed.
# We send the prompt verbatim and score the raw response. Token caps
# matter here: some prompts ask for "at least 500 words," so the
# default 1024 max_tokens in the registry can clip valid responses.
# Bumped to 2048 locally for this cell.

import time
from dataclasses import replace

import pandas as pd

from stratabench import REGISTRY, chat_completion

MODEL_ID = "gpt-4o-mini"
spec = replace(REGISTRY[MODEL_ID], max_tokens=2048)

records = []
start = time.time()
# Score every prompt — including uncovered ones — so the cache covers
# the full dataset. The score cell decides which to count.
for i, row in ifeval_prompts.iterrows():
    response = chat_completion(spec, user=row["prompt"])
    records.append(
        {
            "idx": int(row["idx"]),
            "key": int(row["key"]),
            "raw_response": response.content,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
        }
    )
    if (i + 1) % 10 == 0:
        elapsed = time.time() - start
        print(f"  {i + 1}/{len(ifeval_prompts)} ({elapsed:.0f}s)")

inference = pd.DataFrame(records)
total_tokens = inference["input_tokens"].sum() + inference["output_tokens"].sum()
print(f"\ninference: {len(inference)} responses in {time.time() - start:.0f}s, {total_tokens} tokens")
inference.head()
