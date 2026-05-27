import io
from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


class ImageEdgeDetectNode(BaseNode):

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="image_edge_detect",
            label="边缘检测",
            category="media",
            icon="ViewfinderCircleIcon",
            fields=[
                FieldDef(key="key", label="源文件 Key（无上游时必填）", type="file-picker",
                         placeholder="input/xxx/image.jpg"),
                FieldDef(key="method", label="检测方法", type="select",
                         placeholder="find_edges", required=True,
                         options=["find_edges", "sobel", "contour", "edge_enhance", "edge_enhance_more"],
                         inline=True),
                FieldDef(key="format", label="输出格式", type="select",
                         placeholder="PNG", options=["JPEG", "PNG", "WEBP"], inline=True),
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
                size=(3, 3),
                kernel=[-1, 0, 1, -2, 0, 2, -1, 0, 1],
                scale=1,
                offset=128,
            )
            sobel_y = ImageFilter.Kernel(
                size=(3, 3),
                kernel=[-1, -2, -1, 0, 0, 0, 1, 2, 1],
                scale=1,
                offset=128,
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
