from nodes.base import BaseNode, NodeContext
from nodes._input_utils import get_first_input


class FilterNode(BaseNode):
    """Filter rows of a pandas DataFrame using a query expression."""

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            import pandas as pd
            df = get_first_input(inputs, "filter_node")
            if not isinstance(df, pd.DataFrame):
                raise RuntimeError(
                    f"过滤: 输入必须是 pandas DataFrame，实际收到的是 {type(df).__name__}。"
                    f"请将本节点连接到 DataFrame 输出节点。"
                )
            query = ctx.config.get("query", "")
            if not query:
                return df
            try:
                return df.query(query).reset_index(drop=True)
            except Exception as e:
                raise RuntimeError(
                    f"过滤: 表达式执行失败。请检查 query='{query}' 是否合法。底层错误: {e}"
                )
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"过滤: {e}")
