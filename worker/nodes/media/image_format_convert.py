import io
from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


class ImageFormatConvertNode(BaseNode):
    """Resize an image to target width/height, preserving aspect ratio if only one is given.

    Config:
        width: int  (optional)
        height: int (optional)
        format: str — output format, default "JPEG"
    """

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="image_format_convert",
            label="图片格式转换",
            category="media",
            icon="ArrowPathIcon",
            fields=[
                FieldDef(key="key", label="源文件 Key（无上游时必填）", type="file-picker",
                         placeholder="input/xxx/image.jpg"),
                FieldDef(key="format", label="目标格式", type="select",
                         placeholder="PNG", required=True,
                         options=["JPEG", "PNG", "WEBP", "BMP", "TIFF"], inline=True),
            ],
        )

    def execute(self, inputs: list, ctx: NodeContext):
        from PIL import Image
        raw = inputs[0] if inputs else None
        if raw is None:
            raise ValueError("ImageFormatConvertNode requires image data as input")
        target_format = ctx.config.get("format", "PNG").upper()
        img = Image.open(io.BytesIO(raw))

        if target_format in ("JPEG", "JPG"):
            if img.mode in ("RGBA", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "LA":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode == "P":
                img = img.convert("RGB")
            elif img.mode not in ("RGB", "L"):
                img = img.convert("RGB")

        buf = io.BytesIO()
        img.save(buf, format=target_format)
        return buf.getvalue()
