from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


class FilterNode(BaseNode):
    """Filter rows of a pandas DataFrame using a query expression."""

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="filter",
            label="过滤",
            category="transforms",
            icon="FunnelIcon",
            fields=[
                FieldDef(key="query", label="Pandas Query 表达式", type="text",
                         placeholder="age > 18", required=True, inline=True),
            ],
        )

    def execute(self, inputs: list, ctx: NodeContext):
        import pandas as pd
        df = inputs[0]
        if not isinstance(df, pd.DataFrame):
            raise TypeError("FilterNode expects a DataFrame as input")
        query = ctx.config.get("query", "")
        if not query:
            return df
        return df.query(query).reset_index(drop=True)
