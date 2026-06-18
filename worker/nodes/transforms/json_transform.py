import jmespath
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import (
    get_first_input,
    err_no_upstream,
    err_jmespath_syntax,
    err_generic,
)


class JsonTransformNode(BaseNode):
    def execute(self, inputs: list, ctx: NodeContext):
        try:
            if not inputs:
                err_no_upstream("json_transform")
            data = get_first_input(inputs, "json_transform")
            expression = ctx.config.get("expression", "@")
            if data is None:
                err_no_upstream("json_transform")
            try:
                return jmespath.search(expression, data)
            except jmespath.exceptions.ParseError:
                err_jmespath_syntax("json_transform", expression)
            except jmespath.exceptions.JMESPathError as e:
                raise RuntimeError(
                    f"JSON转换: JMESPath 执行失败。expression='{expression}'。底层错误: {e}"
                )
        except RuntimeError:
            raise
        except Exception as e:
            err_generic("json_transform", f"JSON 转换失败: {e}")
