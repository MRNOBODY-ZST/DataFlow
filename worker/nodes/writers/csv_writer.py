import io
import pandas as pd
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import (
    err_no_upstream,
    err_bad_input_type,
    err_minio_upload,
    err_generic,
)


class CsvWriterNode(BaseNode):
    def execute(self, inputs: list, ctx: NodeContext):
        try:
            if not inputs:
                err_no_upstream("csv_writer")
            data = inputs[0]
            if not isinstance(data, pd.DataFrame):
                err_bad_input_type("csv_writer", type(data).__name__, "pandas DataFrame")

            key = ctx.config.get("key") or ctx.source_filename or "result.csv"
            if not key.endswith(".csv"):
                key += ".csv"
            key = ctx.output_key(key)

            raw = data.to_csv(index=False).encode()
            bucket = ctx.config.get("bucket", ctx.output_bucket)
            try:
                ctx.minio_client.put_object(
                    bucket,
                    key,
                    io.BytesIO(raw),
                    length=len(raw),
                    content_type="text/csv",
                )
            except Exception as e:
                err_minio_upload("csv_writer", key, f"{e}")
            return key
        except RuntimeError:
            raise
        except Exception as e:
            err_generic("csv_writer", f"CSV 写出失败: {e}")
