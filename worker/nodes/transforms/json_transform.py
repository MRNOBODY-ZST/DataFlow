import jmespath

from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef


class JsonTransformNode(BaseNode):

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="json_transform",
            label="JSON 转换",
            category="transforms",
            icon="CodeBracketSquareIcon",
            fields=[
                FieldDef(key="expression", label="JMESPath 表达式", type="text",
                         placeholder="items[*].name", required=True, widget="jmespath", inline=True),
            ],
        )

    def execute(self, inputs: list, ctx: NodeContext):
        if not inputs:
            raise ValueError("json_transform requires an input payload")
        expression = ctx.config.get("expression", "@")
        return jmespath.search(expression, inputs[0])
