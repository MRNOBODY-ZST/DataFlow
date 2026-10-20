import io
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import resolve_media_bytes


class ImageOCRNode(BaseNode):

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            import easyocr

            raw = resolve_media_bytes(inputs, ctx, "image_ocr")

            lang = ctx.config.get("lang", ["en"])
            reader = easyocr.Reader(lang, gpu=False, verbose=False)
            results = reader.readtext(raw, detail=0)
            return "\n".join(results)
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"图像OCR: {e}")
