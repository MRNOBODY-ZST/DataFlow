from typing import Any, List
from . import _drone_base as B

INDEX_NAME = 'ngrdi'
CALC = B.calc_ngrdi
REQUIRED = ['Green', 'Red']


class Operator:
    """计算无人机 ngrdi 指数。"""


    def execute(self, inputs, ctx):
        from . import _drone_base as B
        _impl = B.make_execute_for_drone(
            'ngrdi', B.calc_ngrdi, ['Green','Red'], 'drone_ngrdi')
        return _impl(self, inputs, ctx)

    def __call__(self, ctx: Any) -> Any:
        bucket = getattr(ctx, "input_bucket", "") or (ctx.config.get("bucket", "") if hasattr(ctx, "config") else "")
        key = getattr(ctx, "input_key", "") or (ctx.config.get("key", "") if hasattr(ctx, "config") else "")
        raw_inputs = getattr(ctx, "inputs", [])
        ctx.outputs = B._run_by_semantic(raw_inputs, bucket, key, INDEX_NAME, CALC, REQUIRED, "drone_ngrdi")
        return ctx

ImageDroneNgrdiNode = Operator
