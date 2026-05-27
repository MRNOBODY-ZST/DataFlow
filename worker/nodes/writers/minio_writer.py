import io
from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


class MinioWriterNode(BaseNode):
    """Write data to MinIO.

    Accepts:
        - bytes / bytearray  → written directly
        - pandas DataFrame   → written as CSV
        - str                → written as UTF-8 text
        - list               → written as JSON

    Config:
        key: str      — destination object key
        bucket: str   — destination bucket (default: output)
    """

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="minio_writer",
            label="MinIO 写出",
            category="writers",
            icon="CloudArrowUpIcon",
            fields=[
                FieldDef(key="key", label="输出 Key", type="text",
                         placeholder="output/result", inline=True),
                FieldDef(key="bucket", label="目标 Bucket（默认 dataflow-output）", type="text",
                         placeholder="dataflow-output"),
            ],
        )

    _SIGNATURES = {
        b"\xff\xd8\xff": ("image/jpeg", ".jpg"),
        b"\x89PNG\r\n\x1a\n": ("image/png", ".png"),
        b"RIFF": ("image/webp", ".webp"),
        b"BM": ("image/bmp", ".bmp"),
        b"II\x2a\x00": ("image/tiff", ".tiff"),
        b"MM\x00\x2a": ("image/tiff", ".tiff"),
        b"GIF8": ("image/gif", ".gif"),
    }

    @staticmethod
    def _detect_image(data: bytes) -> tuple[str, str] | None:
        for sig, result in MinioWriterNode._SIGNATURES.items():
            if data[:len(sig)] == sig:
                return result
        return None

    def execute(self, inputs: list, ctx: NodeContext):
        import json
        import pandas as pd

        data = inputs[0]
        key = ctx.config.get("key") or ctx.source_key or ""
        bucket = ctx.config.get("bucket", ctx.output_bucket)

        if not key:
            import pandas as pd
            if isinstance(data, (bytes, bytearray)):
                key = "result"
            elif hasattr(pd, 'DataFrame') and isinstance(data, pd.DataFrame):
                key = "result.csv"
            elif isinstance(data, (list, dict)):
                key = "result.json"
            else:
                key = "result"

        if isinstance(data, (bytes, bytearray)):
            raw = bytes(data)
            detected = self._detect_image(raw)
            if detected:
                content_type, ext = detected
                if not any(key.lower().endswith(e) for e in
                           (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif")):
                    key += ext
            else:
                content_type = "application/octet-stream"
        elif isinstance(data, pd.DataFrame):
            raw = data.to_csv(index=False).encode()
            content_type = "text/csv"
            if not key.endswith(".csv"):
                key += ".csv"
        elif isinstance(data, str):
            raw = data.encode()
            content_type = "text/plain"
            if not any(key.lower().endswith(e) for e in (".txt", ".text", ".log", ".csv", ".json", ".xml", ".html")):
                key += ".txt"
        elif isinstance(data, (list, dict)):
            raw = json.dumps(data, ensure_ascii=False, indent=2).encode()
            content_type = "application/json"
            if not key.endswith(".json"):
                key += ".json"
        else:
            raise TypeError(f"MinioWriterNode: unsupported data type {type(data)}")

        key = ctx.output_key(key)
        ctx.minio_client.put_object(bucket, key, io.BytesIO(raw), length=len(raw), content_type=content_type)
        return key
