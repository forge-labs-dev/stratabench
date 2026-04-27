# @name Format prompts (0-shot, generation-based)
#
# Build the prompt strings stratabench actually sends to each model. We
# follow lm-evaluation-harness's MMLU template for the body, but score
# 0-shot and generation-based instead of the canonical 5-shot log-prob.
# Both deviations are necessary for closed-API parity:
#
#   - log-prob scoring needs raw token logits, which Anthropic and Gemini
#     don't expose. Generation-based asks the model to output a single
#     letter and parses the first valid one. lm-eval has matching
#     `*_generative` task variants that we mirror.
#   - 5-shot wants a separate dev split for examples; MMLU-redux only
#     ships a cleaned test split, and pulling from the original MMLU dev
#     muddies the dataset citation. 0-shot keeps the methodology one
#     file shorter and is what newer leaderboards (Open LLM v2) use.
#
# Citation comment for the audit trail:
#   lm-eval task reference: lm_eval/tasks/mmlu/_generative/_default_template_yaml
#
# v1.1 will add the 5-shot variant alongside this for the open-source
# models that support log-prob.

LETTERS = ["A", "B", "C", "D"]

PROMPT_TEMPLATE = """The following is a multiple choice question about {subject_name}. Answer with a single letter (A, B, C, or D), nothing else.

{question}
A. {a}
B. {b}
C. {c}
D. {d}

Answer:"""


def _humanize_subject(subject: str) -> str:
    """Turn ``high_school_us_history`` into ``high school us history``.

    Subject identifiers are snake_case in the dataset; the prompt reads
    naturally with spaces. Match lm-eval's _default_template_yaml.
    """
    return subject.replace("_", " ")


def format_prompt(row) -> str:
    choices = list(row["choices"])
    if len(choices) != 4:
        raise ValueError(f"Expected 4 choices, got {len(choices)} for {row['subject']}/{row['idx']}")
    return PROMPT_TEMPLATE.format(
        subject_name=_humanize_subject(row["subject"]),
        question=row["question"].strip(),
        a=choices[0],
        b=choices[1],
        c=choices[2],
        d=choices[3],
    )


prompts = mmlu_questions.copy()
prompts["prompt"] = prompts.apply(format_prompt, axis=1)
prompts["gold_letter"] = prompts["answer"].map(lambda i: LETTERS[int(i)])

print(f"prompts: {len(prompts)} formatted")
print("\nfirst prompt preview:")
print(prompts.iloc[0]["prompt"])
