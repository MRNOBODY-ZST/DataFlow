import io
from nodes.base import BaseNode, NodeContext


class ImageFormatConvertNode(BaseNode):
    def execute(self, inputs: list, ctx: NodeContext):
        from PIL import Image
        raw = inputs[0] if inputs else None
        if raw is None:
            key = ctx.config.get("key") or ctx.config.get("input_key")
            response = ctx.minio_client.get_object(ctx.input_bucket, key)
            try:
                raw = response.read()
            finally:
                response.close()
                response.release_conn()

        target_format = ctx.config.get("format", "PNG").upper()
        img = Image.open(io.BytesIO(raw))

        if target_format in ("JPEG", "JPG"):
            if img.mode in ("RGBA", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "LA":
                    img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode == "P":
                    img = img.convert("RGB")
                elif img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")

        buf = io.BytesIO()
        img.save(buf, format=target_format)
