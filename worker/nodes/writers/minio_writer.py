import io
from nodes.base import BaseNode, NodeContext


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

    def execute(self, inputs: list, ctx: NodeContext):
        import json
        import pandas as pd

        data = inputs[0]
        key = ctx.config.get("key") or ctx.source_filename or "result"
        bucket = ctx.config.get("bucket", ctx.output_bucket)

        if isinstance(data, (bytes, bytearray)):
            raw = bytes(data)
            content_type = "application/octet-stream"
        elif isinstance(data, pd.DataFrame):
            raw = data.to_csv(index=False).encode()
            content_type = "text/csv"
            if not key.endswith(".csv"):
                key += ".csv"
        elif isinstance(data, str):
            raw = data.encode()
            content_type = "text/plain"
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
