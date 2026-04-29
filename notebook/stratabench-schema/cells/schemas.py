# @name Schema bank (literal-constant module cell)
#
# 20 hand-curated JSON Schemas spanning four complexity buckets:
#
#   trivial   — flat 2–3-field objects; the floor any model should clear.
#   moderate  — common app shapes (nested objects, arrays, enums, bools).
#   complex   — nested objects with required fields, constrained types,
#               arrays-of-objects.
#   edge      — adversarial cases (strict enums, format validators,
#               additionalProperties: false enforcement).
#
# Each entry pairs a schema with an instruction prompt that asks the
# model to generate a *concrete instance* matching the schema. Scoring
# is binary (jsonschema-validates or it doesn't); the methodology
# disclosure is "we asked in plain prose, no provider response_format
# scaffolding — this measures the model's intrinsic ability to produce
# spec-conforming JSON, not the model + provider's strict-mode shim."
#
# Adding schemas: append to SCHEMA_BANK with a unique ``id``. Keep
# ``schema`` purely declarative (jsonschema dict) and ``instruction``
# concrete enough that a successful response is well-defined.

SCHEMA_BANK: list[dict] = [
    # ------------------------------------------------------------------
    # Trivial bucket — flat objects, primitive fields
    # ------------------------------------------------------------------
    {
        "id": "trivial_user",
        "complexity": "trivial",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name", "age"],
        },
        "instruction": "Generate a JSON object describing a user named Alice who is 30 years old.",
    },
    {
        "id": "trivial_point_2d",
        "complexity": "trivial",
        "schema": {
            "type": "object",
            "properties": {
                "x": {"type": "number"},
                "y": {"type": "number"},
            },
            "required": ["x", "y"],
        },
        "instruction": "Generate a JSON object describing a 2D point at coordinates (3.5, -2.0).",
    },
    {
        "id": "trivial_yes_no",
        "complexity": "trivial",
        "schema": {
            "type": "object",
            "properties": {"answer": {"type": "string", "enum": ["yes", "no"]}},
            "required": ["answer"],
        },
        "instruction": "Is the sky blue? Respond as JSON with an 'answer' field of 'yes' or 'no'.",
    },
    {
        "id": "trivial_greeting",
        "complexity": "trivial",
        "schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "language": {"type": "string"},
            },
            "required": ["message", "language"],
        },
        "instruction": "Generate a JSON greeting object: a friendly hello message in French.",
    },
    {
        "id": "trivial_counter",
        "complexity": "trivial",
        "schema": {
            "type": "object",
            "properties": {"count": {"type": "integer", "minimum": 0}},
            "required": ["count"],
        },
        "instruction": "Generate a JSON object with a 'count' field set to 42.",
    },
    # ------------------------------------------------------------------
    # Moderate bucket — common app shapes
    # ------------------------------------------------------------------
    {
        "id": "moderate_address",
        "complexity": "moderate",
        "schema": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"},
                "state": {"type": "string"},
                "zip": {"type": "string"},
            },
            "required": ["street", "city", "state", "zip"],
        },
        "instruction": "Generate a JSON address for the White House (1600 Pennsylvania Avenue NW, Washington, DC 20500).",
    },
    {
        "id": "moderate_todo_item",
        "complexity": "moderate",
        "schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "completed": {"type": "boolean"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
            },
            "required": ["title", "completed", "priority"],
        },
        "instruction": "Generate a JSON todo-list item: 'Buy groceries', not yet completed, medium priority.",
    },
    {
        "id": "moderate_product",
        "complexity": "moderate",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "price": {"type": "number", "minimum": 0},
                "in_stock": {"type": "boolean"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["name", "price", "in_stock", "tags"],
        },
        "instruction": "Generate JSON for a product: 'USB-C Cable', $12.99, in stock, tagged with 'electronics' and 'accessories'.",
    },
    {
        "id": "moderate_user_with_address",
        "complexity": "moderate",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                    },
                    "required": ["street", "city"],
                },
            },
            "required": ["name", "address"],
        },
        "instruction": "Generate JSON for a user named Bob who lives at 742 Evergreen Terrace, Springfield.",
    },
    {
        "id": "moderate_weather",
        "complexity": "moderate",
        "schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "temp_f": {"type": "number"},
                "conditions": {
                    "type": "string",
                    "enum": ["sunny", "cloudy", "rainy", "snowy", "foggy"],
                },
                "humidity": {"type": "integer", "minimum": 0, "maximum": 100},
            },
            "required": ["location", "temp_f", "conditions", "humidity"],
        },
        "instruction": "Generate JSON describing today's weather in San Francisco: 62°F, foggy, 78% humidity.",
    },
    {
        "id": "moderate_event",
        "complexity": "moderate",
        "schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "start": {"type": "string", "format": "date-time"},
                "attendees": {"type": "array", "items": {"type": "string"}},
                "recurring": {"type": "boolean"},
            },
            "required": ["title", "start", "attendees", "recurring"],
        },
        "instruction": "Generate JSON for a calendar event: 'Q1 Planning' on 2026-01-15 at 14:00 UTC, attendees Alice and Bob, not recurring.",
    },
    # ------------------------------------------------------------------
    # Complex bucket — nested + constrained
    # ------------------------------------------------------------------
    {
        "id": "complex_recipe",
        "complexity": "complex",
        "schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "servings": {"type": "integer", "minimum": 1},
                "ingredients": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "quantity": {"type": "number"},
                            "unit": {
                                "type": "string",
                                "enum": ["g", "kg", "ml", "l", "tsp", "tbsp", "cup", "piece"],
                            },
                        },
                        "required": ["name", "quantity", "unit"],
                    },
                },
                "steps": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title", "servings", "ingredients", "steps"],
        },
        "instruction": "Generate JSON for a simple pancake recipe: title, 4 servings, ingredient list with units from the enum, and at least three steps.",
    },
    {
        "id": "complex_blog_post",
        "complexity": "complex",
        "schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "body": {"type": "string"},
                "author": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                    },
                    "required": ["name", "email"],
                },
                "tags": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                "published_at": {"type": "string", "format": "date-time"},
            },
            "required": ["title", "body", "author", "tags", "published_at"],
        },
        "instruction": "Generate JSON for a short blog post titled 'Hello World' by Jane Doe (jane@example.com), published 2026-04-01, with at least one tag.",
    },
    {
        "id": "complex_tool_call",
        "complexity": "complex",
        "schema": {
            "type": "object",
            "properties": {
                "function": {"type": "string"},
                "arguments": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                    },
                    "required": ["query"],
                },
            },
            "required": ["function", "arguments"],
        },
        "instruction": "Generate a JSON tool call to the function 'search_documents' with the query 'climate change' and a limit of 10.",
    },
    {
        "id": "complex_analytics_event",
        "complexity": "complex",
        "schema": {
            "type": "object",
            "properties": {
                "event_name": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "anonymous": {"type": "boolean"},
                    },
                    "required": ["id", "anonymous"],
                },
                "properties": {"type": "object"},
            },
            "required": ["event_name", "timestamp", "user", "properties"],
        },
        "instruction": "Generate a JSON analytics event for 'page_view' at 2026-04-27T10:00:00Z by anonymous user 'anon_1234' with properties including a 'url' field.",
    },
    {
        "id": "complex_order_summary",
        "complexity": "complex",
        "schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "items": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "sku": {"type": "string"},
                            "quantity": {"type": "integer", "minimum": 1},
                            "unit_price": {"type": "number", "minimum": 0},
                        },
                        "required": ["sku", "quantity", "unit_price"],
                    },
                },
                "totals": {
                    "type": "object",
                    "properties": {
                        "subtotal": {"type": "number"},
                        "tax": {"type": "number"},
                        "total": {"type": "number"},
                    },
                    "required": ["subtotal", "tax", "total"],
                },
            },
            "required": ["order_id", "items", "totals"],
        },
        "instruction": "Generate JSON for an order: order_id 'ORD-001', two items (SKU 'BOOK-A' qty 2 at $15, SKU 'PEN-B' qty 5 at $2), totals (subtotal $40, tax $3.30, total $43.30).",
    },
    {
        "id": "complex_job_application",
        "complexity": "complex",
        "schema": {
            "type": "object",
            "properties": {
                "applicant": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "phone": {"type": "string"},
                    },
                    "required": ["name", "email"],
                },
                "position": {"type": "string"},
                "experience_years": {"type": "integer", "minimum": 0},
                "skills": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            },
            "required": ["applicant", "position", "experience_years", "skills"],
        },
        "instruction": "Generate JSON for a job application: Carol Smith (carol@example.com), applying for 'Senior Engineer' with 8 years experience and skills in Python, Go, and PostgreSQL.",
    },
    # ------------------------------------------------------------------
    # Edge bucket — adversarial / strict
    # ------------------------------------------------------------------
    {
        "id": "edge_strict_enum",
        "complexity": "edge",
        "schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "approved", "rejected", "withdrawn", "expired"],
                }
            },
            "required": ["status"],
        },
        "instruction": "Generate a JSON object with a status that means the request is no longer being considered (use one of: pending, approved, rejected, withdrawn, expired).",
    },
    {
        "id": "edge_format_validators",
        "complexity": "edge",
        "schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "homepage": {"type": "string", "format": "uri"},
                "born_at": {"type": "string", "format": "date-time"},
            },
            "required": ["email", "homepage", "born_at"],
        },
        "instruction": "Generate JSON with email 'sam@example.org', homepage 'https://sam.example.org/', and born_at '1992-03-14T08:00:00Z'.",
    },
    {
        "id": "edge_additional_properties_false",
        "complexity": "edge",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "integer"},
            },
            "required": ["name", "value"],
            "additionalProperties": False,
        },
        "instruction": "Generate JSON with exactly two fields: name='example' and value=7. Do not include any other fields.",
    },
]
