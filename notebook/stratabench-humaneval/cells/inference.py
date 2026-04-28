# @name Run inference (gpt-4o-mini)
# @timeout 3600
#
# HumanEval responses are typically short — one fenced code block —
# but max_tokens needs to be generous because problems with longer
# canonical solutions (e.g. dynamic programming, parsing) can run a
# few hundred tokens. The 1024 default in the registry is enough for
# the entire HumanEval set.

import time

import pandas as pd

from stratabench import REGISTRY, chat_completion

MODEL_ID = "gpt-4o-mini"
spec = REGISTRY[MODEL_ID]

records = []
start = time.time()
for i, row in prompts.iterrows():
    response = chat_completion(spec, user=row["formatted_prompt"])
    records.append(
        {
            "task_id": row["task_id"],
            "idx": int(row["idx"]),
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
