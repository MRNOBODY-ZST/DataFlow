import jmespath

from nodes.base import BaseNode, NodeContext


class JsonTransformNode(BaseNode):
    def execute(self, inputs: list, ctx: NodeContext):
        if not inputs:
            raise ValueError("json_transform requires an input payload")
        expression = ctx.config.get("expression", "@")
        return jmespath.search(expression, inputs[0])
