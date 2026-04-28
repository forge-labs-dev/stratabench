# @name Score (sandboxed pytest-style execution)
# @timeout 1200
#
# This is the only cell in stratabench that runs untrusted code, so it
# matters how we sandbox. Each (response, test) pair goes into its own
# subprocess with a wall-clock cap; the subprocess imports nothing from
# the parent, prints PASS or FAIL to stdout, and exits. Infinite loops
# in a model response or import-time crashes can't take out the cell
# harness — they just fail their own task.
#
# Score is HumanEval's standard pass@1: fraction of tasks where the
# single sampled completion passes the dataset's tests. We don't sample
# multiple completions for v1 (no pass@k), the model decoding is
# temperature 0 in the registry so sampling would be redundant anyway.
#
# Citation comment for the audit trail:
#   lm-eval task reference: lm_eval/tasks/humaneval/humaneval_instruct.yaml
#   Sandboxing matches the openai/human-eval reference impl: a fresh
#   subprocess per task, no resource limits beyond a wall-clock timeout.

import re
import subprocess
import sys
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed

PER_TASK_TIMEOUT_SECONDS = 10.0
PARALLEL_WORKERS = 4

# Capture the FIRST fenced python block. Models occasionally emit several
# (e.g. one for examples, one for the answer); the first is conventionally
# the answer. Falls back to the entire response if no fence is found —
# accepts the case where the model produced bare code without markup.
_CODE_BLOCK_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)


def extract_code(raw: str) -> str:
    m = _CODE_BLOCK_RE.search(raw)
    return m.group(1) if m else raw


def run_one(prompt: str, model_code: str, test: str, entry_point: str) -> tuple[bool, str]:
    """Execute the candidate solution against the task's tests in a subprocess.

    Returns (passed, message). ``message`` is empty on success and the
    captured stderr/stdout on failure for debugging.
    """
    program = textwrap.dedent(
        f"""\
        import sys
        # ``prompt`` already contains the function signature; the model's
        # response should contain the body. Concatenating is the canonical
        # HumanEval pattern: prompt + completion = a runnable module.
        {prompt}{model_code}

        {test}

        try:
            check({entry_point})
            print("PASS")
            sys.exit(0)
        except Exception as exc:
            print(f"FAIL: {{type(exc).__name__}}: {{exc}}")
            sys.exit(1)
        """
    )
    try:
        result = subprocess.run(
            [sys.executable, "-c", program],
            capture_output=True,
            text=True,
            timeout=PER_TASK_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return False, "timeout"

    if result.returncode == 0 and result.stdout.strip().endswith("PASS"):
        return True, ""
    msg = (result.stdout + "\n" + result.stderr).strip()[:500]
    return False, msg or f"exit {result.returncode}"


# Run tasks in parallel — subprocess overhead dominates per-task latency,
# so a small thread pool is enough to bring 164 tasks down to a couple
# of minutes total.
scored_records = []
joined = inference.merge(
    prompts[["task_id", "idx", "prompt", "test", "entry_point"]],
    on=["task_id", "idx"],
    how="left",
    validate="one_to_one",
)

with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
    futures = {}
    for _, row in joined.iterrows():
        model_code = extract_code(row["raw_response"])
        future = executor.submit(
            run_one,
            row["prompt"],
            model_code,
            row["test"],
            row["entry_point"],
        )
        futures[future] = row
    for i, future in enumerate(as_completed(futures), start=1):
        row = futures[future]
        passed, message = future.result()
        scored_records.append(
            {
                "task_id": row["task_id"],
                "idx": int(row["idx"]),
                "passed": passed,
                "message": message,
            }
        )
        if i % 10 == 0:
            print(f"  scored {i}/{len(futures)}")

import pandas as pd

scored = pd.DataFrame(scored_records)
pass_at_1 = float(scored["passed"].mean())
n_pass = int(scored["passed"].sum())
fail_messages = scored.loc[~scored["passed"], "message"].value_counts().head(5).to_dict()

from stratabench import EvalResult

humaneval_score = EvalResult(
    eval_name="humaneval_instruct_pass_at_1",
    model_id=spec.id,
    score=pass_at_1,
    n=len(scored),
    details={
        "n_pass": n_pass,
        "top_failure_modes": fail_messages,
    },
)

print(f"\nhumaneval pass@1: {pass_at_1:.4f}  ({n_pass}/{len(scored)} tasks passed)")
print(f"model: {spec.id}")
if fail_messages:
    print("\ntop failure modes (truncated):")
    for msg, count in list(fail_messages.items())[:3]:
        print(f"  [{count}] {msg[:120]}")
humaneval_score
