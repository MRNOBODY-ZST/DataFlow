from nodes.base import BaseNode, NodeContext
from nodes._input_utils import (
    get_first_input,
    err_bad_input_type,
    err_agg_field_missing,
    err_generic,
)


class AggregateNode(BaseNode):
    """Group-by aggregation on a pandas DataFrame."""

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            import pandas as pd
            df = get_first_input(inputs, "aggregate_node")
            if not isinstance(df, pd.DataFrame):
                err_bad_input_type("aggregate_node", type(df).__name__, "pandas DataFrame")
            group_by = ctx.config.get("group_by", [])
            agg = ctx.config.get("agg", {})
            if not group_by or not agg:
                return df
            try:
                return df.groupby(group_by).agg(agg).reset_index()
            except Exception as e:
                missing = None
                cols_str = str(df.columns.tolist())
                if isinstance(e, KeyError):
                    missing = str(e).strip("'\"")
                elif isinstance(e, NotImplementedError):
                    missing = "group_by/agg expression"
                if missing is not None:
                    err_agg_field_missing("aggregate_node", missing, cols_str)
                raise RuntimeError(
                    f"聚合: 计算失败。请检查 group_by={group_by} 与 agg={agg}"
                    f"是否与 DataFrame 列名匹配。底层错误: {e}"
                )
        except RuntimeError:
            raise
        except Exception as e:
            err_generic("aggregate_node", f"聚合失败: {e}")
