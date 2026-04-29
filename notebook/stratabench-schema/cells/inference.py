# @name Run inference (gpt-4o-mini)
# @timeout 1800
#
# Iterate the prompts and call the model. Same synchronous pattern as the
# other evals. The prompt asks for a fenced ```json``` block; the score
# cell extracts that and validates against the schema.

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
            "id": row["id"],
            "complexity": row["complexity"],
            "raw_response": response.content,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
        }
    )
    if (i + 1) % 5 == 0:
        elapsed = time.time() - start
        print(f"  {i + 1}/{len(prompts)} ({elapsed:.0f}s)")

inference = pd.DataFrame(records)
total_tokens = inference["input_tokens"].sum() + inference["output_tokens"].sum()
print(f"\ninference: {len(inference)} responses in {time.time() - start:.0f}s, {total_tokens} tokens")
inference.head()
