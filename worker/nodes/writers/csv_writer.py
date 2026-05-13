import io

import pandas as pd

from nodes.base import BaseNode, NodeContext


class CsvWriterNode(BaseNode):
    def execute(self, inputs: list, ctx: NodeContext):
        if not inputs:
            raise ValueError("csv_writer requires an input DataFrame")
        data = inputs[0]
        if not isinstance(data, pd.DataFrame):
            raise TypeError("csv_writer expects a pandas DataFrame")

        key = ctx.config.get("key", f"output/{ctx.task_id}/result.csv")
        if not key.endswith(".csv"):
            key += ".csv"

        raw = data.to_csv(index=False).encode()
        ctx.minio_client.put_object(
            ctx.output_bucket,
            key,
            io.BytesIO(raw),
            length=len(raw),
            content_type="text/csv",
        )
        return key
