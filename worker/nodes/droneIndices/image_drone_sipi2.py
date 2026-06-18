from typing import Any, List
from . import _drone_base as B

INDEX_NAME = 'sipi2'
CALC = B.calc_sipi2
REQUIRED = ['NIR', 'Green', 'Red']


class Operator:
    """计算无人机 sipi2 指数。"""


    def execute(self, inputs, ctx):
        from . import _drone_base as B
        _impl = B.make_execute_for_drone(
            'sipi2', B.calc_sipi2, ['NIR', 'Green', 'Red'], 'drone_sipi2')
        return _impl(self, inputs, ctx)

    def __call__(self, ctx: Any) -> Any:
        bucket = getattr(ctx, "input_bucket", "") or (ctx.config.get("bucket", "") if hasattr(ctx, "config") else "")
        key = getattr(ctx, "input_key", "") or (ctx.config.get("key", "") if hasattr(ctx, "config") else "")
        raw_inputs = getattr(ctx, "inputs", [])
        # 复用 _drone_base 的 run_single_index 但按语义波段识别，此处直接走 _full 入口
        ctx.outputs = B._run_by_semantic(raw_inputs, bucket, key, INDEX_NAME, CALC, REQUIRED, "drone_sipi2")
        return ctx

ImageDroneSipi2Node = Operator
