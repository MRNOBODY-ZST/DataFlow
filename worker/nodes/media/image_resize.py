import io
from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


class ImageResizeNode(BaseNode):
    """Resize an image to target width/height, preserving aspect ratio if only one is given.

    Config:
        width: int  (optional)
        height: int (optional)
        format: str — output format, default "JPEG"
    """

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="image_resize",
            label="图片缩放",
            category="media",
            icon="PhotoIcon",
            fields=[
                FieldDef(key="key", label="源文件 Key（无上游时必填）", type="file-picker",
                         placeholder="input/xxx/image.jpg"),
                FieldDef(key="width", label="宽度 (px)", type="number",
                         placeholder="800", inline=True),
                FieldDef(key="height", label="高度 (px)", type="number",
                         placeholder="600", inline=True),
                FieldDef(key="format", label="输出格式", type="select",
                         placeholder="JPEG", options=["JPEG", "PNG", "WEBP"], inline=True),
            ],
        )

    def execute(self, inputs: list, ctx: NodeContext):
        from PIL import Image
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
        width = ctx.config.get("width")
        height = ctx.config.get("height")
        fmt = ctx.config.get("format", "JPEG").upper()

        if width and height:
            img = img.resize((int(width), int(height)), Image.LANCZOS)
        elif width:
            ratio = int(width) / img.width
            img = img.resize((int(width), int(img.height * ratio)), Image.LANCZOS)
        elif height:
            ratio = int(height) / img.height
            img = img.resize((int(img.width * ratio), int(height)), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format=fmt)
        return buf.getvalue()
