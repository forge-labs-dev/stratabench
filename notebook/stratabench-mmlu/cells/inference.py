# @name Run inference (gpt-4o-mini)
# @timeout 600
#
# Iterate the formatted prompts and call the model. One call per question,
# synchronous for v1 — concurrency adds complexity (rate limits, retries,
# ordering) that doesn't matter at the smoke-run scale (~30 calls). The
# full publication run (~5700 questions) will need batching; that lands
# in v1.1 once the spec is locked.
#
# Provenance: every input that affects the result is hashed by Strata's
# cell. That means changing MODEL_ID below produces a fresh artifact and
# fresh score, the prompts cell's source is part of the input hash, and
# no rerun shortcut can pass off old numbers as new ones.

import time

from stratabench import REGISTRY, chat_completion

MODEL_ID = "gpt-4o-mini"
spec = REGISTRY[MODEL_ID]

records = []
start = time.time()
for i, row in prompts.iterrows():
    response = chat_completion(spec, user=row["prompt"])
    records.append(
        {
            "subject": row["subject"],
            "idx": int(row["idx"]),
            "raw_response": response.content,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
        }
    )
    if (i + 1) % 10 == 0:
        elapsed = time.time() - start
        print(f"  {i + 1}/{len(prompts)} ({elapsed:.0f}s)")

import pandas as pd

inference = pd.DataFrame(records)
total_tokens = inference["input_tokens"].sum() + inference["output_tokens"].sum()
print(f"\ninference: {len(inference)} responses in {time.time() - start:.0f}s, {total_tokens} tokens")
inference.head()
