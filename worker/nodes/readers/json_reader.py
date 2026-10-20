import io
import json
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import err_minio_missing_key, err_minio_not_found, err_json_malformed, err_generic


class JsonReaderNode(BaseNode):
    """Read a JSON file from MinIO and return a Python object."""

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            key = ctx.config.get("key") or ctx.config.get("input_key")
            if not key:
                err_minio_missing_key("json_reader")
            bucket = ctx.config.get("bucket", ctx.input_bucket)
            try:
                response = ctx.minio_client.get_object(bucket, key)
            except Exception as e:
                err_minio_not_found("json_reader", key, bucket)
            try:
                raw = response.read()
            finally:
                response.close()
                response.release_conn()
            try:
                data = json.loads(raw.decode())
            except json.JSONDecodeError as e:
                err_json_malformed("json_reader", f"{e}")
            return data
        except RuntimeError:
            raise
        except Exception as e:
            err_generic("json_reader", f"JSON 读取失败: {e}")
