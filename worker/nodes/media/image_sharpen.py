import io
from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


class ImageSharpenNode(BaseNode):

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="image_sharpen",
            label="图片锐化",
            category="media",
            icon="SparklesIcon",
            fields=[
                FieldDef(key="key", label="源文件 Key（无上游时必填）", type="file-picker",
                         placeholder="input/xxx/image.jpg"),
                FieldDef(key="method", label="锐化方法", type="select",
                         placeholder="unsharp_mask", required=True,
                         options=["unsharp_mask", "sharpen_filter", "detail"], inline=True),
                FieldDef(key="radius", label="USM 半径", type="number",
                         placeholder="2", inline=True),
                FieldDef(key="percent", label="USM 强度 (%)", type="number",
                         placeholder="150", inline=True),
                FieldDef(key="threshold", label="USM 阈值", type="number",
                         placeholder="3", inline=True),
                FieldDef(key="factor", label="额外锐化因子（1.0=不变）", type="number",
                         placeholder="1.0"),
                FieldDef(key="format", label="输出格式", type="select",
                         placeholder="JPEG", options=["JPEG", "PNG", "WEBP"], inline=True),
            ],
        )

    def execute(self, inputs: list, ctx: NodeContext):
        from PIL import Image, ImageFilter, ImageEnhance

        raw = inputs[0] if inputs else None
        if raw is None:
            key = ctx.config.get("key") or ctx.config.get("input_key")
            response = ctx.minio_client.get_object(ctx.input_bucket, key)
            try:
                raw = response.read()
            finally:
                response.close()
                response.release_conn()

        img = Image.open(io.BytesIO(raw))
        method = ctx.config.get("method", "unsharp_mask")
        fmt = ctx.config.get("format", "JPEG").upper()

        if method == "sharpen_filter":
            img = img.filter(ImageFilter.SHARPEN)
        elif method == "detail":
            img = img.filter(ImageFilter.DETAIL)
        else:
            radius = float(ctx.config.get("radius", 2))
            percent = int(ctx.config.get("percent", 150))
            threshold = int(ctx.config.get("threshold", 3))
            img = img.filter(ImageFilter.UnsharpMask(
                radius=radius,
                percent=percent,
                threshold=threshold,
            ))

        factor = float(ctx.config.get("factor", 1.0))
        if factor != 1.0:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(factor)

        buf = io.BytesIO()
        if img.mode == "RGBA" and fmt == "JPEG":
            img = img.convert("RGB")
        img.save(buf, format=fmt)
        return buf.getvalue()
