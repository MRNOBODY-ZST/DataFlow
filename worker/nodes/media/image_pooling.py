import io
from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


class ImagePoolingNode(BaseNode):

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="image_pooling",
            label="图片池化",
            category="media",
            icon="Squares2X2Icon",
            fields=[
                FieldDef(key="key", label="源文件 Key（无上游时必填）", type="file-picker",
                         placeholder="input/xxx/image.jpg"),
                FieldDef(key="method", label="池化方法", type="select",
                         placeholder="max", required=True,
                         options=["max", "avg"], inline=True),
                FieldDef(key="pool_size", label="池化窗口大小", type="select",
                         placeholder="2", options=["2", "3", "4", "8"], inline=True),
                FieldDef(key="stride", label="步长（默认等于窗口大小）", type="number",
                         placeholder="2", inline=True),
                FieldDef(key="format", label="输出格式", type="select",
                         placeholder="JPEG", options=["JPEG", "PNG", "WEBP"], inline=True),
            ],
        )

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
