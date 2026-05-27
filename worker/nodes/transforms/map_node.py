from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef, WidgetConfig


class MapNode(BaseNode):
    """Rename / select columns of a pandas DataFrame.

    Config:
        rename: dict[str, str]  — old_col -> new_col
        select: list[str]       — columns to keep (applied after rename)
    """

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="map",
            label="字段映射",
            category="transforms",
            icon="ArrowsRightLeftIcon",
            fields=[
                FieldDef(key="rename", label="字段重命名", type="textarea",
                         placeholder='{"old":"new"}', widget="key-value",
                         widget_config=WidgetConfig(key_placeholder="原字段名", value_placeholder="新字段名", value_type="text")),
                FieldDef(key="select", label="保留列", type="text",
                         placeholder='["colA","colB"]', widget="string-array"),
            ],
        )

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
