# @name Format prompts (0-shot CoT)
#
# 0-shot chain-of-thought template: ask the model to reason step by step
# and end with the canonical "#### N" suffix that GSM8K uses for the
# gold answer. The matching scorer below extracts the number after ####
# (or, as a fallback, the last number anywhere in the response).
#
# Citation comment for the audit trail:
#   lm-eval task reference: lm_eval/tasks/gsm8k/gsm8k_cot_zeroshot.yaml
#   We deviate by not interleaving few-shot examples — modern leaderboards
#   (Open LLM v2, MMLU-Pro era) report 0-shot CoT as the primary number
#   for instruction-tuned models, and the prompt contract is simpler.

PROMPT_TEMPLATE = """Solve this math problem. Reason step by step, then give your final numeric answer on its own line in the form:

#### N

where N is just the final number, no units, no commas.

Problem: {question}

Solution:"""


def format_prompt(row) -> str:
    return PROMPT_TEMPLATE.format(question=row["question"].strip())


prompts = gsm8k_questions.copy()
prompts["prompt"] = prompts.apply(format_prompt, axis=1)

print(f"prompts: {len(prompts)} formatted")
print("\nfirst prompt preview:")
print(prompts.iloc[0]["prompt"])
