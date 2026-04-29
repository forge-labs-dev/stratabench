# @name Format prompts
#
# We embed the schema directly in the prompt body. The methodology is
# deliberate: we test the model's *intrinsic* ability to produce
# spec-conforming JSON from a schema description, NOT the provider's
# strict-mode shim. Using ``response_format=json_schema`` would make
# every score effectively 100% (the API enforces it server-side) and
# defeat the eval.
#
# Citation comment for the audit trail:
#   This is a stratabench-original eval — no canonical lm-eval reference.
#   The methodology design is documented in docs/methodology.md.

import json

import pandas as pd

PROMPT_TEMPLATE = """{instruction}

The response must be valid JSON conforming to this JSON Schema:

```json
{schema}
```

Reply with ONLY the JSON object, wrapped in a single ```json``` code block. Do not include explanations."""


def format_prompt(row) -> str:
    return PROMPT_TEMPLATE.format(
        instruction=row["instruction"],
        schema=json.dumps(row["schema"], indent=2),
    )


prompts = pd.DataFrame(SCHEMA_BANK)
prompts["prompt"] = prompts.apply(format_prompt, axis=1)

print(f"prompts: {len(prompts)} schemas across {prompts['complexity'].nunique()} complexity buckets")
print(f"  bucket counts: {prompts['complexity'].value_counts().to_dict()}")
print("\nfirst prompt preview:")
print(prompts.iloc[0]["prompt"])
