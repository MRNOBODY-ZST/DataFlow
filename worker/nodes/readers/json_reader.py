import io
import json
from nodes.base import BaseNode, NodeContext


class JsonReaderNode(BaseNode):
    """Read a JSON file from MinIO and return a Python object."""

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            key = ctx.config.get("key") or ctx.config.get("input_key")
            if not key:
                raise RuntimeError(
                    "JSON读取: 请在节点配置中提供 key 或 input_key（MinIO 中的 JSON 对象路径）。"
                )
            bucket = ctx.config.get("bucket", ctx.input_bucket)
            response = ctx.minio_client.get_object(bucket, key)
            try:
                raw = response.read()
            finally:
                response.close()
                response.release_conn()
            try:
                data = json.loads(raw.decode())
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"JSON读取: JSON 解析失败。请确认 {key} 是有效的 JSON 格式。底层错误: {e}"
                )
            return data
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"JSON读取: {e}")
