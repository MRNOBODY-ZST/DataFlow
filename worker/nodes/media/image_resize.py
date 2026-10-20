import io
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import resolve_media_bytes


class ImageResizeNode(BaseNode):

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            from PIL import Image

            raw = resolve_media_bytes(inputs, ctx, "image_resize")
            img = Image.open(io.BytesIO(raw))

            width = ctx.config.get("width")
            height = ctx.config.get("height")
            fmt = ctx.config.get("format", "JPEG").upper()

            if not width and not height:
                raise RuntimeError(
                    f"图像缩放: 请在节点配置中提供 width 或 height（至少一项）。"
                    f" 如 {{'width': 640}} 或 {{'height': 480}}。"
                )

            if width and height:
                img = img.resize((int(width), int(height)), Image.LANCZOS)
            elif width:
                ratio = int(width) / img.width
                img = img.resize((int(width), int(img.height * ratio)), Image.LANCZOS)
            elif height:
                ratio = int(height) / img.height
                img = img.resize((int(img.width * ratio), int(height)), Image.LANCZOS)

            buf = io.BytesIO()
            img.save(buf, format=fmt)
            return buf.getvalue()
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"图像缩放: {e}")
