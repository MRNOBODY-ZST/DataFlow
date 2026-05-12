from nodes.base import BaseNode, NodeContext


class FilterNode(BaseNode):
    """Filter rows of a pandas DataFrame using a query expression."""

    def execute(self, inputs: list, ctx: NodeContext):
        import pandas as pd
        df = inputs[0]
        if not isinstance(df, pd.DataFrame):
            raise TypeError("FilterNode expects a DataFrame as input")
        query = ctx.config.get("query", "")
        if not query:
            return df
        return df.query(query).reset_index(drop=True)
