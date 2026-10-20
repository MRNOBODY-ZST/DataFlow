from typing import Any, List
from . import _drone_base as B

INDEX_NAME = 'ciredge'
CALC = B.calc_cirededge
REQUIRED = ['NIR', 'RedEdge']


class Operator:
    """计算无人机 CIREdge 指数 (NIR / RedEdge - 1)。"""


    def execute(self, inputs, ctx):
        from . import _drone_base as B
        _impl = B.make_execute_for_drone(
            'ciredge', B.calc_cirededge, ['NIR','RedEdge'], 'drone_ciredge')
        return _impl(self, inputs, ctx)

    def __call__(self, ctx: Any) -> Any:
        bucket = getattr(ctx, "input_bucket", "") or (ctx.config.get("bucket", "") if hasattr(ctx, "config") else "")
        key = getattr(ctx, "input_key", "") or (ctx.config.get("key", "") if hasattr(ctx, "config") else "")
        raw_inputs = getattr(ctx, "inputs", [])
        ctx.outputs = B._run_by_semantic(raw_inputs, bucket, key, INDEX_NAME, CALC, REQUIRED, "drone_ciredge")
        return ctx

ImageDroneCiredgeNode = Operator
