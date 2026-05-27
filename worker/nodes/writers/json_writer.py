import io
import json

import pandas as pd

from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


class JsonWriterNode(BaseNode):
    """Write JSON data to MinIO.

    Config:
        key: str           — destination object key
        bucket: str        — destination bucket (default: output)
        indent: int        — JSON indentation (default: 2)
        ensure_ascii: bool — escape non-ASCII chars (default: false)
    """

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="json_writer",
            label="JSON 写出",
            category="writers",
            icon="CodeBracketIcon",
            fields=[
                FieldDef(key="key", label="输出 Key", type="text",
                         placeholder="output/result.json", inline=True),
                FieldDef(key="indent", label="缩进空格数", type="number",
                         placeholder="2"),
                FieldDef(key="ensure_ascii", label="转义非 ASCII 字符", type="checkbox"),
            ],
        )

    def execute(self, inputs: list, ctx: NodeContext):
        if not inputs:
            raise ValueError("json_writer requires an input payload")

        data = inputs[0]

        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")
        elif isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass

        indent = int(ctx.config.get("indent", 2))
        ensure_ascii = bool(ctx.config.get("ensure_ascii", False))

        if isinstance(data, (dict, list)):
            raw = json.dumps(data, ensure_ascii=ensure_ascii, indent=indent).encode()
        elif isinstance(data, str):
            raw = data.encode()
        else:
            raw = json.dumps(data, ensure_ascii=ensure_ascii, indent=indent, default=str).encode()

        key = ctx.config.get("key") or ctx.source_key or "result"
        bucket = ctx.config.get("bucket", ctx.output_bucket)
        if not key.endswith(".json"):
            key += ".json"
        key = ctx.output_key(key)

        ctx.minio_client.put_object(
            bucket, key, io.BytesIO(raw),
            length=len(raw),
            content_type="application/json",
        )
        return key
