import io
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import resolve_media_bytes


class ImageGaussianBlurNode(BaseNode):

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            from PIL import Image, ImageFilter

            raw = resolve_media_bytes(inputs, ctx, "image_gaussian_blur")
            img = Image.open(io.BytesIO(raw))

            radius = float(ctx.config.get("radius", 2))
            fmt = ctx.config.get("format", "JPEG").upper()

            img = img.filter(ImageFilter.GaussianBlur(radius=radius))

            buf = io.BytesIO()
            if img.mode == "RGBA" and fmt == "JPEG":
                img = img.convert("RGB")
            img.save(buf, format=fmt)
            return buf.getvalue()
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"图像高斯模糊: {e}")
