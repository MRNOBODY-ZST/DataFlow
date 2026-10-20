from nodes.base import BaseNode, NodeContext
from nodes._input_utils import (
    get_first_input,
    err_bad_input_type,
    err_generic,
)


class MapNode(BaseNode):
    """Rename / select columns of a pandas DataFrame."""

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            import pandas as pd
            df = get_first_input(inputs, "map_node")
            if not isinstance(df, pd.DataFrame):
                err_bad_input_type("map_node", type(df).__name__, "pandas DataFrame")
            rename = ctx.config.get("rename", {})
            if rename:
                df = df.rename(columns=rename)
            select = ctx.config.get("select", [])
            if select:
                df = df[[c for c in select if c in df.columns]]
            return df
        except RuntimeError:
            raise
        except Exception as e:
            err_generic("map_node", f"字段映射失败: {e}")
