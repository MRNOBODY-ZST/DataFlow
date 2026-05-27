from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef, WidgetConfig


class AggregateNode(BaseNode):
    """Group-by aggregation on a pandas DataFrame.

    Config:
        group_by: list[str]
        agg: dict[str, str]  — col -> func  (e.g. {"amount": "sum"})
    """

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="aggregate",
            label="聚合",
            category="transforms",
            icon="ChartBarIcon",
            fields=[
                FieldDef(key="group_by", label="分组列", type="text",
                         placeholder='["category"]', required=True, widget="string-array"),
                FieldDef(key="agg", label="聚合方法", type="textarea",
                         placeholder='{"amount":"sum"}', required=True, widget="key-value",
                         widget_config=WidgetConfig(key_placeholder="字段名", value_placeholder="聚合函数",
                                                   value_type="select",
                                                   value_options=["sum", "avg", "min", "max", "count", "first", "last"])),
            ],
        )

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
