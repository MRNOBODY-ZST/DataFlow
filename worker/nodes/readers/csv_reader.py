import io
import pandas as pd
from nodes.base import BaseNode, NodeContext


class CsvReaderNode(BaseNode):
    """Read a CSV from MinIO and return a pandas DataFrame."""

    def execute(self, inputs: list, ctx: NodeContext):
        key = ctx.config.get("key") or ctx.config.get("input_key")
        bucket = ctx.config.get("bucket", ctx.input_bucket)
        response = ctx.minio_client.get_object(bucket, key)
        try:
            df = pd.read_csv(io.BytesIO(response.read()))
        finally:
            response.close()
            response.release_conn()
        return df
