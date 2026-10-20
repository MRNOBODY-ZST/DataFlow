from typing import Any
from ._s2_base import run_single_index, calc_ndsi

INDEX_NAME = 'ndsi'


class Operator:
    """计算 Sentinel-2 NDSI 指数 (Green-SWIR2)。"""

    def execute(self, inputs, ctx):
        from ._s2_base import make_execute_for_s2
        _impl = make_execute_for_s2('ndsi')
        return _impl(self, inputs, ctx)

    def __call__(self, ctx: Any) -> Any:
        bucket = getattr(ctx, "input_bucket", ctx.config.get("bucket", ""))
        key = getattr(ctx, "input_key", ctx.config.get("key", ""))
        ctx.source_key = key
        raw_inputs = getattr(ctx, "inputs", [])
        ctx.outputs = run_single_index(INDEX_NAME, raw_inputs, ctx)
        return ctx

ImageS2NdsiNode = Operator
