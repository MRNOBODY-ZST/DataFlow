from nodes.base import BaseNode, NodeContext
from nodes._input_utils import get_first_input


class MapNode(BaseNode):
    """Rename / select columns of a pandas DataFrame."""

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            import pandas as pd
            df = get_first_input(inputs, "map_node")
            if not isinstance(df, pd.DataFrame):
                raise RuntimeError(
                    f"字段映射: 输入必须是 pandas DataFrame，实际收到的是 {type(df).__name__}。"
                    f"请将本节点连接到 DataFrame 输出节点。"
                )
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
            raise RuntimeError(f"字段映射: {e}")
