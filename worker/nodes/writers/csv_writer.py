import io
import pandas as pd
from nodes.base import BaseNode, NodeContext


class CsvWriterNode(BaseNode):
    def execute(self, inputs: list, ctx: NodeContext):
        try:
            if not inputs:
                raise RuntimeError(
                    "CSV写入: 没有收到上游数据。请将本节点连接到 DataFrame 输出节点。"
                )
            data = inputs[0]
            if not isinstance(data, pd.DataFrame):
                raise RuntimeError(
                    f"CSV写入: 输入必须是 pandas DataFrame，实际收到的是 {type(data).__name__}。"
                )

            key = ctx.config.get("key") or ctx.source_filename or "result.csv"
            if not key.endswith(".csv"):
                key += ".csv"
            key = ctx.output_key(key)

            raw = data.to_csv(index=False).encode()
            ctx.minio_client.put_object(
                ctx.output_bucket,
                key,
                io.BytesIO(raw),
                length=len(raw),
                content_type="text/csv",
            )
            return key
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"CSV写入: {e}")
