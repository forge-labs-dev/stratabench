# @name Run inference (gpt-4o-mini)
# @timeout 3600
#
# Iterate the formatted prompts and call the model. GSM8K responses are
# long (chain-of-thought reasoning before the final ####) so per-question
# latency is higher than MMLU. The 1024-token max_tokens in the registry
# is generally enough; problems that hit the cap fall back to the
# scorer's last-number-in-response rule and may score wrong.

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
