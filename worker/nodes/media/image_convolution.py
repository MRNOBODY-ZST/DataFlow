import io
import json
from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


class ImageConvolutionNode(BaseNode):

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="image_convolution",
            label="图片卷积",
            category="media",
            icon="AdjustmentsHorizontalIcon",
            fields=[
                FieldDef(key="key", label="源文件 Key（无上游时必填）", type="file-picker",
                         placeholder="input/xxx/image.jpg"),
                FieldDef(key="preset", label="预设卷积核", type="select",
                         placeholder="blur",
                         options=["blur", "sharpen", "contour", "detail", "edge_enhance", "emboss", "smooth", "custom"],
                         inline=True),
                FieldDef(key="kernel", label="自定义卷积核（JSON 数组，preset=custom 时生效）", type="textarea",
                         placeholder="[0,-1,0,-1,5,-1,0,-1,0]"),
                FieldDef(key="kernel_size", label="卷积核尺寸", type="select",
                         placeholder="3", options=["3", "5"]),
                FieldDef(key="offset", label="偏移量", type="number",
                         placeholder="0"),
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
        preset = ctx.config.get("preset", "custom")
        fmt = ctx.config.get("format", "JPEG").upper()

        presets = {
            "blur": ImageFilter.BLUR,
            "sharpen": ImageFilter.SHARPEN,
            "contour": ImageFilter.CONTOUR,
            "detail": ImageFilter.DETAIL,
            "edge_enhance": ImageFilter.EDGE_ENHANCE,
            "emboss": ImageFilter.EMBOSS,
            "smooth": ImageFilter.SMOOTH,
        }

        if preset in presets:
            img = img.filter(presets[preset])
        else:
            kernel_str = ctx.config.get("kernel", "")
            size = int(ctx.config.get("kernel_size", 3))
            if kernel_str:
                kernel_data = json.loads(kernel_str) if isinstance(kernel_str, str) else kernel_str
                scale = sum(kernel_data) or 1
                offset = int(ctx.config.get("offset", 0))
                img = img.filter(ImageFilter.Kernel(
                    size=(size, size),
                    kernel=kernel_data,
                    scale=scale,
                    offset=offset,
                ))

        buf = io.BytesIO()
        if img.mode == "RGBA" and fmt == "JPEG":
            img = img.convert("RGB")
        img.save(buf, format=fmt)
        return buf.getvalue()
