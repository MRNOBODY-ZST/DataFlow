from nodes.base import BaseNode, NodeContext
from nodes._input_utils import get_first_input


class AggregateNode(BaseNode):
    """Group-by aggregation on a pandas DataFrame."""

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            import pandas as pd
            df = get_first_input(inputs, "aggregate_node")
            if not isinstance(df, pd.DataFrame):
                raise RuntimeError(
                    f"聚合: 输入必须是 pandas DataFrame，实际收到的是 {type(df).__name__}。"
                    f"请将本节点连接到 DataFrame 输出节点（如 CSV读取、JSON读取）。"
                )
            group_by = ctx.config.get("group_by", [])
            agg = ctx.config.get("agg", {})
            if not group_by or not agg:
                return df
            try:
                return df.groupby(group_by).agg(agg).reset_index()
            except Exception as e:
                raise RuntimeError(
                    f"聚合: 计算失败。请检查 group_by={group_by} 与 agg={agg}"
                    f"是否与 DataFrame 列名匹配。底层错误: {e}"
                )
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"聚合: {e}")
