import io
import json
from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


class JsonReaderNode(BaseNode):
    """Read a JSON file from MinIO and return a Python object."""

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="json_reader",
            label="JSON 读取",
            category="readers",
            icon="CodeBracketIcon",
            fields=[
                FieldDef(key="key", label="MinIO 对象 Key", type="file-picker",
                         placeholder="input/xxx/data.json", required=True, inline=True),
            ],
        )

    def execute(self, inputs: list, ctx: NodeContext):
        key = ctx.config.get("key") or ctx.config.get("input_key")
        bucket = ctx.config.get("bucket", ctx.input_bucket)
        response = ctx.minio_client.get_object(bucket, key)
        try:
            data = json.loads(response.read().decode())
        finally:
            response.close()
            response.release_conn()
        return data
