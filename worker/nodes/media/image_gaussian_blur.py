import io
from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


class ImageGaussianBlurNode(BaseNode):

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="image_gaussian_blur",
            label="高斯模糊",
            category="media",
            icon="EyeDropperIcon",
            fields=[
                FieldDef(key="key", label="源文件 Key（无上游时必填）", type="file-picker",
                         placeholder="input/xxx/image.jpg"),
                FieldDef(key="radius", label="模糊半径", type="number",
                         placeholder="2", required=True, inline=True),
                FieldDef(key="format", label="输出格式", type="select",
                         placeholder="JPEG", options=["JPEG", "PNG", "WEBP"], inline=True),
            ],
        )

    def execute(self, inputs: list, ctx: NodeContext):
        from PIL import Image, ImageFilter

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
        radius = float(ctx.config.get("radius", 2))
        fmt = ctx.config.get("format", "JPEG").upper()

        img = img.filter(ImageFilter.GaussianBlur(radius=radius))

        buf = io.BytesIO()
        if img.mode == "RGBA" and fmt == "JPEG":
            img = img.convert("RGB")
        img.save(buf, format=fmt)
        return buf.getvalue()
