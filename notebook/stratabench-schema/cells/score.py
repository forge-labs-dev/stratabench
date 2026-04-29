# @name Score (jsonschema validation)
#
# For each response: (1) extract the JSON from the fenced code block,
# (2) parse it, (3) validate it against the schema with ``jsonschema``
# in the strictest applicable mode (formatChecker enabled). Three
# distinct failure modes are tracked separately so the report tells the
# user *why* a model lost points:
#
#   parse_failed     The response wasn't extractable JSON at all.
#   schema_invalid   JSON parsed but didn't match the schema.
#   ok               JSON parsed and validated cleanly.
#
# Score is the fraction of (ok) results. Macro-average across complexity
# buckets so a model that aces the trivial bucket but fails the edge one
# can't hide behind a flat micro-average.

import json
import re

import jsonschema
import pandas as pd
from jsonschema import FormatChecker

_CODE_BLOCK_RE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL)
_FORMAT_CHECKER = FormatChecker()


def extract_json(raw: str) -> dict | list | None:
    """Pull the first fenced JSON block, or treat the whole response as
    JSON if no fence is present. Returns None if neither parses."""
    candidates: list[str] = []
    m = _CODE_BLOCK_RE.search(raw)
    if m:
        candidates.append(m.group(1))
    candidates.append(raw)
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            continue
    return None


def validate(value, schema: dict) -> tuple[str, str]:
    """Return ``(status, message)``. Status is 'ok' / 'schema_invalid'."""
    try:
        jsonschema.validate(instance=value, schema=schema, format_checker=_FORMAT_CHECKER)
    except jsonschema.exceptions.ValidationError as exc:
        return "schema_invalid", f"{list(exc.absolute_path)}: {exc.message}"
    return "ok", ""


# Re-attach the schema dicts to the inference rows so we don't have to
# round-trip them through prompts.
schema_lookup = {row["id"]: row["schema"] for _, row in prompts.iterrows()}

results = []
for _, row in inference.iterrows():
    parsed = extract_json(row["raw_response"])
    if parsed is None:
        results.append({**row.to_dict(), "status": "parse_failed", "message": ""})
        continue
    status, message = validate(parsed, schema_lookup[row["id"]])
    results.append({**row.to_dict(), "status": status, "message": message})

scored = pd.DataFrame(results)
scored["passed"] = scored["status"] == "ok"

micro_score = float(scored["passed"].mean())
per_bucket = scored.groupby("complexity")["passed"].mean()
macro_score = float(per_bucket.mean())
status_counts = scored["status"].value_counts().to_dict()

from stratabench import EvalResult

schema_score = EvalResult(
    eval_name="schema_adherence_v1",
    model_id=spec.id,
    score=macro_score,
    n=len(scored),
    details={
        "micro_score": micro_score,
        "per_bucket": per_bucket.round(4).to_dict(),
        "status_counts": status_counts,
    },
)

print(f"\nschema_adherence (macro): {macro_score:.4f}  (micro: {micro_score:.4f})")
print(f"model: {spec.id}")
print(f"n: {len(scored)} schemas")
print(f"per-bucket: {per_bucket.round(4).to_dict()}")
print(f"status: {status_counts}")
schema_score
