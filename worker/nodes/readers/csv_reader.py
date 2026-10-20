import io
import pandas as pd
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import err_minio_missing_key, err_minio_not_found, err_generic


class CsvReaderNode(BaseNode):
    """Read a CSV from MinIO and return a pandas DataFrame."""

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            key = ctx.config.get("key") or ctx.config.get("input_key")
            if not key:
                err_minio_missing_key("csv_reader")
            bucket = ctx.config.get("bucket", ctx.input_bucket)
            try:
                response = ctx.minio_client.get_object(bucket, key)
            except Exception as e:
                err_minio_not_found("csv_reader", key, bucket)
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
            err_generic("csv_reader", f"CSV 解析失败，请检查文件是否是合法 CSV。底层: {e}")
