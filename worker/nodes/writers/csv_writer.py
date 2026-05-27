import io

import pandas as pd

from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


class CsvWriterNode(BaseNode):

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="csv_writer",
            label="CSV 写出",
            category="writers",
            icon="TableCellsIcon",
            fields=[
                FieldDef(key="key", label="输出 Key", type="text",
                         placeholder="output/result.csv", inline=True),
            ],
        )

    def execute(self, inputs: list, ctx: NodeContext):
        if not inputs:
            raise ValueError("csv_writer requires an input DataFrame")
        data = inputs[0]
        if not isinstance(data, pd.DataFrame):
            raise TypeError("csv_writer expects a pandas DataFrame")

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
