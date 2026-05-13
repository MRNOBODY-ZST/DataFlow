import io
from nodes.base import BaseNode, NodeContext


class ImageGaussianBlurNode(BaseNode):

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
