import io
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import resolve_media_bytes


class ImageEdgeDetectNode(BaseNode):

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            from PIL import Image, ImageFilter

            raw = resolve_media_bytes(inputs, ctx, "image_edge_detect")
            img = Image.open(io.BytesIO(raw))

            method = ctx.config.get("method", "find_edges")
            fmt = ctx.config.get("format", "JPEG").upper()

            methods = {
                "find_edges": ImageFilter.FIND_EDGES,
                "contour": ImageFilter.CONTOUR,
                "edge_enhance": ImageFilter.EDGE_ENHANCE,
                "edge_enhance_more": ImageFilter.EDGE_ENHANCE_MORE,
            }

            if method == "sobel":
                gray = img.convert("L")
                sobel_x = ImageFilter.Kernel(
                    size=(3, 3), kernel=[-1, 0, 1, -2, 0, 2, -1, 0, 1],
                    scale=1, offset=128,
                )
                sobel_y = ImageFilter.Kernel(
                    size=(3, 3), kernel=[-1, -2, -1, 0, 0, 0, 1, 2, 1],
                    scale=1, offset=128,
                )
                import numpy as np
                gx = np.array(gray.filter(sobel_x), dtype=np.float32) - 128
                gy = np.array(gray.filter(sobel_y), dtype=np.float32) - 128
                magnitude = np.sqrt(gx ** 2 + gy ** 2)
                magnitude = np.clip(magnitude, 0, 255).astype(np.uint8)
                img = Image.fromarray(magnitude, mode="L")
            elif method in methods:
                img = img.filter(methods[method])
            else:
                img = img.filter(ImageFilter.FIND_EDGES)

            buf = io.BytesIO()
            if img.mode == "RGBA" and fmt == "JPEG":
                img = img.convert("RGB")
            img.save(buf, format=fmt)
            return buf.getvalue()
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"图像边缘检测: {e}")
