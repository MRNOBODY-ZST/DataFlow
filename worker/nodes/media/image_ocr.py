import io
from nodes.base import BaseNode, NodeContext


class ImageOCRNode(BaseNode):
    """Extract text from an image using EasyOCR.

    Config:
        lang: list[str] — language codes, default ["en"]
    """

    def execute(self, inputs: list, ctx: NodeContext):
        import easyocr
        raw = inputs[0] if inputs else None
        if raw is None:
            key = ctx.config.get("key") or ctx.config.get("input_key")
            response = ctx.minio_client.get_object(ctx.input_bucket, key)
            try:
                raw = response.read()
            finally:
                response.close()
                response.release_conn()

        lang = ctx.config.get("lang", ["en"])
        reader = easyocr.Reader(lang, gpu=False, verbose=False)
        results = reader.readtext(raw, detail=0)
        return "\n".join(results)
