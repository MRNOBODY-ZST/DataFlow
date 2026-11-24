"""Single-image CPU adapter for the separately delivered UAV RGB classifier."""
from pathlib import Path
from tempfile import TemporaryDirectory

from nodes.media.uav_runtime import infer, stage_tiff
from nodes.base import BaseNode, FieldDef, NodeContext, NodeSchema


class UavRgbNode(BaseNode):
    @classmethod
    def schema(cls):
        return NodeSchema("uav_rgb", "无人机 RGB 地物分类", "media", "PhotoIcon", [
            FieldDef("key", "RGB GeoTIFF", type="file-picker",
                     placeholder="留空则使用原文件名", inline=True),
        ])

    def execute(self, inputs: list, ctx: NodeContext) -> bytes:
        key = ctx.config.get("key")
        if inputs:
            if len(inputs) != 1 or not isinstance(inputs[0], (bytes, bytearray)):
                raise ValueError("无人机 RGB 地物分类只接受一张 TIFF 影像")
        elif not key or key.endswith("/"):
            raise ValueError("请选择一个 RGB GeoTIFF 文件或连接一个影像上游")

        with TemporaryDirectory(prefix="uav_rgb_") as temp:
            src = Path(temp) / "input.tif"
            stage_tiff(src, ctx, key=key, data=inputs[0] if inputs else None)
            return infer("rgb", src.parent, ["--input", str(src)])
