import io
from nodes.base import BaseNode, NodeContext


class ImageThresholdNode(BaseNode):

    def execute(self, inputs: list, ctx: NodeContext):
        from PIL import Image
        import numpy as np

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
        method = ctx.config.get("method", "binary")
        threshold_val = int(ctx.config.get("threshold", 128))
        fmt = ctx.config.get("format", "PNG").upper()

        gray = img.convert("L")

        if method == "otsu":
            arr = np.array(gray)
            hist, _ = np.histogram(arr.ravel(), bins=256, range=(0, 256))
            total = arr.size
            sum_all = np.sum(np.arange(256) * hist)
            sum_bg = 0.0
            weight_bg = 0
            max_var = 0.0
            best_thresh = 0
            for t in range(256):
                weight_bg += hist[t]
                if weight_bg == 0:
                    continue
                weight_fg = total - weight_bg
                if weight_fg == 0:
                    break
                sum_bg += t * hist[t]
                mean_bg = sum_bg / weight_bg
                mean_fg = (sum_all - sum_bg) / weight_fg
                var = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2
                if var > max_var:
                    max_var = var
                    best_thresh = t
            threshold_val = best_thresh
            result = gray.point(lambda p: 255 if p > threshold_val else 0, mode="1")
        elif method == "binary_inv":
            result = gray.point(lambda p: 0 if p > threshold_val else 255, mode="1")
        elif method == "truncate":
            result = gray.point(lambda p: threshold_val if p > threshold_val else p)
        elif method == "to_zero":
            result = gray.point(lambda p: p if p > threshold_val else 0)
        else:
            result = gray.point(lambda p: 255 if p > threshold_val else 0, mode="1")

        buf = io.BytesIO()
        result.save(buf, format=fmt)
        return buf.getvalue()
