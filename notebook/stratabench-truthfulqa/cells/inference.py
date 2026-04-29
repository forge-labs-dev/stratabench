# @name Run inference (gpt-4o-mini)
# @timeout 3600
#
# Iterate the formatted prompts and call the model. Same synchronous loop
# pattern as MMLU and GSM8K — concurrency lands in v1.1 once the spec is
# locked.

import time

import pandas as pd

from stratabench import REGISTRY, chat_completion

MODEL_ID = "gpt-4o-mini"
spec = REGISTRY[MODEL_ID]

records = []
start = time.time()
for i, row in prompts.iterrows():
    response = chat_completion(spec, user=row["prompt"])
    records.append(
        {
            "idx": int(row["idx"]),
            "raw_response": response.content,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
        }
    )
    if (i + 1) % 10 == 0:
        elapsed = time.time() - start
        print(f"  {i + 1}/{len(prompts)} ({elapsed:.0f}s)")

inference = pd.DataFrame(records)
total_tokens = inference["input_tokens"].sum() + inference["output_tokens"].sum()
print(f"\ninference: {len(inference)} responses in {time.time() - start:.0f}s, {total_tokens} tokens")
inference.head()
