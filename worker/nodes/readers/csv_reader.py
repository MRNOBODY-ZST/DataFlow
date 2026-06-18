import io
import pandas as pd
from nodes.base import BaseNode, NodeContext


class CsvReaderNode(BaseNode):
    """Read a CSV from MinIO and return a pandas DataFrame."""

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            key = ctx.config.get("key") or ctx.config.get("input_key")
            if not key:
                raise RuntimeError(
                    "CSV读取: 请在节点配置中提供 key 或 input_key（MinIO 中的 CSV 对象路径）。"
                )
            bucket = ctx.config.get("bucket", ctx.input_bucket)
            response = ctx.minio_client.get_object(bucket, key)
            try:
                try:
                    df = pd.read_csv(io.BytesIO(response.read()))
                except Exception as e:
                    raise RuntimeError(
                        f"CSV读取: CSV 文件解析失败。请确认 {key} 是有效的 CSV。底层错误: {e}"
                    )
            finally:
                response.close()
                response.release_conn()
            return df
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"CSV读取: {e}")
