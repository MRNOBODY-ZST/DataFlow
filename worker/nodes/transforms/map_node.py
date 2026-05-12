from nodes.base import BaseNode, NodeContext


class MapNode(BaseNode):
    """Rename / select columns of a pandas DataFrame.

    Config:
        rename: dict[str, str]  — old_col -> new_col
        select: list[str]       — columns to keep (applied after rename)
    """

    def execute(self, inputs: list, ctx: NodeContext):
        import pandas as pd
        df = inputs[0]
        if not isinstance(df, pd.DataFrame):
            raise TypeError("MapNode expects a DataFrame as input")
        rename = ctx.config.get("rename", {})
        if rename:
            df = df.rename(columns=rename)
        select = ctx.config.get("select", [])
        if select:
            df = df[[c for c in select if c in df.columns]]
        return df
