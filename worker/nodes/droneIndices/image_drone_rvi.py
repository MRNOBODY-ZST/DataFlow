from typing import Any, List
from . import _drone_base as B

INDEX_NAME = 'rvi'
CALC = B.calc_rvi
REQUIRED = ['NIR', 'Red']


class Operator:
    """计算无人机 rvi 指数。"""


    def execute(self, inputs, ctx):
        from . import _drone_base as B
        _impl = B.make_execute_for_drone(
            'rvi', B.calc_rvi, ['NIR', 'Red'], 'drone_rvi')
        return _impl(self, inputs, ctx)

    def __call__(self, ctx: Any) -> Any:
        bucket = getattr(ctx, "input_bucket", "") or (ctx.config.get("bucket", "") if hasattr(ctx, "config") else "")
        key = getattr(ctx, "input_key", "") or (ctx.config.get("key", "") if hasattr(ctx, "config") else "")
        raw_inputs = getattr(ctx, "inputs", [])
        # 复用 _drone_base 的 run_single_index 但按语义波段识别，此处直接走 _full 入口
        ctx.outputs = B._run_by_semantic(raw_inputs, bucket, key, INDEX_NAME, CALC, REQUIRED, "drone_rvi")
        return ctx

ImageDroneRviNode = Operator
