import io
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import resolve_media_bytes


class ImagePoolingNode(BaseNode):

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            from PIL import Image
            import numpy as np

            raw = resolve_media_bytes(inputs, ctx, "image_pooling")
            img = Image.open(io.BytesIO(raw))

            method = ctx.config.get("method", "max")
            pool_size = int(ctx.config.get("pool_size", 2))
            stride = int(ctx.config.get("stride", pool_size))
            fmt = ctx.config.get("format", "JPEG").upper()

            arr = np.array(img)
            is_color = arr.ndim == 3
            if not is_color:
                arr = arr[:, :, np.newaxis]

            h, w, c = arr.shape
            out_h = (h - pool_size) // stride + 1
            out_w = (w - pool_size) // stride + 1
            out = np.zeros((out_h, out_w, c), dtype=arr.dtype)

            pool_fn = np.max if method == "max" else np.mean

            for i in range(out_h):
                for j in range(out_w):
                    patch = arr[i * stride:i * stride + pool_size,
                                j * stride:j * stride + pool_size, :]
                    out[i, j, :] = pool_fn(patch, axis=(0, 1))

            if not is_color:
                out = out[:, :, 0]

            result = Image.fromarray(out.astype(np.uint8))
            buf = io.BytesIO()
            if result.mode == "RGBA" and fmt == "JPEG":
                result = result.convert("RGB")
            result.save(buf, format=fmt)
            return buf.getvalue()
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"图像池化: {e}")
