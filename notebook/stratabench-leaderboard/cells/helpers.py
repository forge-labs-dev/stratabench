# @name Helpers
# Module cell — surfaces stratabench library types into the notebook
# namespace. The leaderboard notebook is read-only over the published
# results, so it doesn't need the chat_completion plumbing.

from stratabench import REGISTRY, EvalResult

__all__ = ["REGISTRY", "EvalResult"]
