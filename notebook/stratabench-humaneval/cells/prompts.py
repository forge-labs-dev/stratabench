# @name Format prompts (instruction-tuned chat shape)
#
# HumanEval's raw "prompt" field is a function signature + docstring
# meant to be completed by a base completion model. Modern chat-tuned
# models do better when wrapped in an instruction. We follow the
# conventional approach used by the lm-eval `humaneval_instruct` task:
#
#   - Tell the model to produce *only* the function body (or full
#     implementation), inside a fenced code block.
#   - Include the signature + docstring as the spec.
#
# Citation comment for the audit trail:
#   lm-eval task reference: lm_eval/tasks/humaneval/humaneval_instruct.yaml
#
# The scoring cell extracts the first ```python ... ``` block from the
# response, prepends the original signature so the entry_point is always
# bound, then runs the dataset's test code against it.

PROMPT_TEMPLATE = """Complete the following Python function. Reply with only the implementation, wrapped in a single ```python``` code block. Do not include explanations.

```python
{prompt}```"""


def format_prompt(row) -> str:
    return PROMPT_TEMPLATE.format(prompt=row["prompt"])


prompts = humaneval_problems.copy()
prompts["formatted_prompt"] = prompts.apply(format_prompt, axis=1)

print(f"prompts: {len(prompts)} formatted")
print("\nfirst prompt preview:")
print(prompts.iloc[0]["formatted_prompt"])
