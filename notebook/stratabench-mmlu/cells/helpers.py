# @name Helpers
# Module cell — surfaces the stratabench library types into the notebook
# namespace. Downstream eval cells use ``ModelSpec``, ``REGISTRY``, and
# ``EvalResult`` directly; keeping this cell tiny means the
# methodology-specific code in downstream cells is the only thing a
# reproducer reads.

from stratabench import REGISTRY, EvalResult, ModelSpec

__all__ = ["REGISTRY", "EvalResult", "ModelSpec"]
