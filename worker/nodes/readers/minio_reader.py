import io
from nodes.base import BaseNode, NodeContext


class MinioReaderNode(BaseNode):
    """Read raw bytes from MinIO and return them."""

    def execute(self, inputs: list, ctx: NodeContext):
        key = ctx.config.get("key") or ctx.config.get("input_key")
        bucket = ctx.config.get("bucket", ctx.input_bucket)
        response = ctx.minio_client.get_object(bucket, key)
        try:
            data = response.read()
        finally:
            response.close()
            response.release_conn()
        return data
