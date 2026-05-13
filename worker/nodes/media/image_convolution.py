import io
import json
from nodes.base import BaseNode, NodeContext


class ImageConvolutionNode(BaseNode):

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
