"""Wetland land-cover classification from one five-file scene or one multiband TIFF."""
from pathlib import Path
from tempfile import TemporaryDirectory

from minio.error import S3Error
from nodes.base import BaseNode, FieldDef, NodeSchema
from nodes.media.uav_runtime import infer, stage_tiff


BANDS = {"rgb": "RGB 底图", "g": "绿光（G）", "red": "红光（RED）", "re": "红边（RE）", "nir": "近红外（NIR）"}
MANUAL = "按角色选择五张图"


def manual_files(config):
    result = {}
    for band, label in BANDS.items():
        key = config.get("band_" + band)
        if not isinstance(key, str) or not key.lower().endswith((".tif", ".tiff")):
            raise ValueError(f"请为{label}选择一张 TIFF")
        if key in result.values():
            raise ValueError(f"{label}与其他角色不能使用同一个文件")
        result[band] = key
    return result


class UavMultispectralNode(BaseNode):
    @classmethod
    def schema(cls):
        return NodeSchema("uav_multispectral", "无人机多光谱地物分类", "media", "PhotoIcon", [
            FieldDef("input_type", "输入方式", type="select", options=[MANUAL, "raw7", "rgb-vi10"]),
            *[FieldDef("band_" + band, label, type="file-picker", widget="tiff-role", inline=True)
              for band, label in BANDS.items()],
            FieldDef("key", "合并的多波段 TIFF（或连接上游）", type="file-picker", inline=True),
        ])

    def execute(self, inputs, ctx):
        key = ctx.config.get("key") or ""
        mode = ctx.config.get("input_type") or ("auto" if key or inputs else MANUAL)
        if mode == MANUAL or (not ctx.config.get("input_type") and any("band_" + b in ctx.config for b in BANDS)):
            if inputs:
                raise ValueError("五角色模式直接读取已选文件；请移除上游，或改用合并 TIFF 模式")
            files = manual_files(ctx.config)
            with TemporaryDirectory(prefix="uav_ms_") as temp:
                root = Path(temp)
                for band, obj in files.items():
                    try:
                        stage_tiff(root / f"scene_{band}.tif", ctx, key=obj)
                    except S3Error as exc:
                        if exc.code != "NoSuchKey":
                            raise
                        raise ValueError(f"{BANDS[band]}所选文件不存在：{obj}") from exc
                return infer("multispectral", root, ["--scene", "scene", "--input-dir", temp])
        if mode not in ("auto", "raw7", "rgb-vi10"):
            raise ValueError("未知多光谱输入格式")
        if inputs and (len(inputs) != 1 or not isinstance(inputs[0], (bytes, bytearray))):
            raise ValueError("上游须提供一张已对齐的多波段 TIFF")
        if not inputs and (not key or key.endswith("/")):
            raise ValueError("请选择场景的 _rgb.tif、合并的多波段 TIFF，或连接一个多波段 TIFF 上游")
        with TemporaryDirectory(prefix="uav_ms_") as temp:
            root = Path(temp)
            if not inputs and mode == "auto" and key.endswith("_rgb.tif"):
                # Only use the already user-scoped key for object names; local filenames are fixed.
                stem = key[:-len("_rgb.tif")]
                for band in ("rgb", "g", "red", "re", "nir"):
                    obj = f"{stem}_{band}.tif"
                    try:
                        stage_tiff(root / f"scene_{band}.tif", ctx, key=obj)
                    except S3Error as exc:
                        if exc.code != "NoSuchKey":
                            raise
                        raise ValueError(f"多光谱场景缺少文件：{obj.rsplit('/', 1)[-1]}") from exc
                args = ["--scene", "scene", "--input-dir", temp]
            else:
                src = root / "input.tif"
                stage_tiff(src, ctx, key=key, data=inputs[0] if inputs else None)
                args = ["--input", str(src), "--input-type", "raw7" if mode == "auto" else mode]
            return infer("multispectral", root, args)
