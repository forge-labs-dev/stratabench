"""stratabench — reproducible, content-addressed LLM evaluation on Strata.

This package is the *plumbing* — model registry, HTTP clients, the result
dataclass — that every eval notebook reuses. The actual *methodology* of
each eval (prompt formatting, scoring rules, dataset selection) lives in
the notebook cells themselves so a reproducer can open one notebook and
read the entire spec without chasing imports.
"""

from __future__ import annotations

from stratabench.models import REGISTRY, ModelSpec
from stratabench.result import EvalResult

__all__ = ["REGISTRY", "EvalResult", "ModelSpec"]
__version__ = "0.1.0"
