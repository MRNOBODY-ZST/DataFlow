from nodes.base import BaseNode, NodeContext
from nodes._input_utils import (
    get_first_input,
    err_bad_input_type,
    err_filter_syntax,
    err_generic,
)


class FilterNode(BaseNode):
    """Filter rows of a pandas DataFrame using a query expression."""

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            import pandas as pd
            df = get_first_input(inputs, "filter_node")
            if not isinstance(df, pd.DataFrame):
                err_bad_input_type("filter_node", type(df).__name__, "pandas DataFrame")
            query = ctx.config.get("query", "")
            if not query:
                return df
            try:
                return df.query(query).reset_index(drop=True)
            except Exception as e:
                err_filter_syntax("filter_node", query, f"{e}")
        except RuntimeError:
            raise
        except Exception as e:
            err_generic("filter_node", f"过滤失败: {e}")
