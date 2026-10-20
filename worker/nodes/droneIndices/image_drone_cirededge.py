from typing import Any, List
from . import _drone_base as B

INDEX_NAME = 'cirededge'
CALC = B.calc_cirededge
REQUIRED = ['NIR', 'RedEdge']


class Operator:
    """计算无人机 cirededge 指数 (NIR / RedEdge - 1)。"""


    def execute(self, inputs, ctx):
        from . import _drone_base as B
        _impl = B.make_execute_for_drone(
            'cirededge', B.calc_cirededge, ['NIR', 'RedEdge'], 'drone_cirededge')
        return _impl(self, inputs, ctx)

    def __call__(self, ctx: Any) -> Any:
        bucket = getattr(ctx, "input_bucket", "") or (ctx.config.get("bucket", "") if hasattr(ctx, "config") else "")
        key = getattr(ctx, "input_key", "") or (ctx.config.get("key", "") if hasattr(ctx, "config") else "")
        raw_inputs = getattr(ctx, "inputs", [])
        # 复用 _drone_base 的 run_single_index 但按语义波段识别，此处直接走 _full 入口
        ctx.outputs = B._run_by_semantic(raw_inputs, bucket, key, INDEX_NAME, CALC, REQUIRED, "drone_cirededge")
        return ctx

ImageDroneCirededgeNode = Operator
