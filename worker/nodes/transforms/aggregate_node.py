from nodes.base import BaseNode, NodeContext


class AggregateNode(BaseNode):
    """Group-by aggregation on a pandas DataFrame.

    Config:
        group_by: list[str]
        agg: dict[str, str]  — col -> func  (e.g. {"amount": "sum"})
    """

    def execute(self, inputs: list, ctx: NodeContext):
        import pandas as pd
        df = inputs[0]
        if not isinstance(df, pd.DataFrame):
            raise TypeError("AggregateNode expects a DataFrame as input")
        group_by = ctx.config.get("group_by", [])
        agg = ctx.config.get("agg", {})
        if not group_by or not agg:
            return df
        return df.groupby(group_by).agg(agg).reset_index()
