import io
import json
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import resolve_media_bytes


class ImageConvolutionNode(BaseNode):

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            from PIL import Image, ImageFilter

            raw = resolve_media_bytes(inputs, ctx, "image_convolution")
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
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"图像卷积: {e}")
