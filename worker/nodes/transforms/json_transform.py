import jmespath
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import get_first_input


class JsonTransformNode(BaseNode):
    def execute(self, inputs: list, ctx: NodeContext):
        try:
            if not inputs:
                raise RuntimeError(
                    "JSON转换: 没有收到上游数据。请将本节点连接到上游 JSON/字典节点。"
                )
            data = get_first_input(inputs, "json_transform")
            expression = ctx.config.get("expression", "@")
            if data is None:
                raise RuntimeError(
                    "JSON转换: 上游没有传输出数据（输入为空）。请检查上游节点是否已成功执行，或连接上游。"
                )
            try:
                return jmespath.search(expression, data)
            except jmespath.exceptions.ParseError as e:
                raise RuntimeError(
                    f"JSON转换: JMESPath 表达式解析失败。请检查 expression='{expression}' 是否合法。底层错误: {e}"
                )
            except jmespath.exceptions.JMESPathError as e:
                raise RuntimeError(
                    f"JSON转换: JMESPath 执行失败。expression='{expression}'。底层错误: {e}"
                )
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"JSON转换: {e}")
