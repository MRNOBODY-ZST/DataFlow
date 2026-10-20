from nodes.base import BaseNode, NodeContext
from nodes._input_utils import (
    get_first_input,
    err_bad_input_type,
    err_generic,
)


class JsonMapperNode(BaseNode):
    """Declarative JSON field mapper - no JMESPath required."""

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            data = get_first_input(inputs, "json_mapper")
            mappings = ctx.config.get("mappings", [])
            if not isinstance(data, (dict, list)):
                err_bad_input_type("json_mapper", type(data).__name__, "dict 或 list")

            if not mappings:
                return data

            result = {}
            for m in mappings:
                source = m.get("source", "")
                target = m.get("target", source)
                default = m.get("default")

                value = _resolve_source(data, source)
                if value is None and default is not None:
                    value = default

                target_parts = [p for p in target.split(".") if p]
                if target_parts:
                    _set_by_path(result, target_parts, value)

            return result
        except RuntimeError:
            raise
        except Exception as e:
            err_generic("json_mapper", f"JSON 映射失败: {e}")


def _get_by_path(obj, path_parts: list[str]):
    current = obj
    for part in path_parts:
        if part == "[*]":
            if not isinstance(current, list):
                return []
            return current
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return None
        else:
            return None
        if current is None:
            return None
    return current


def _set_by_path(obj: dict, path_parts: list[str], value):
    current = obj
    for i, part in enumerate(path_parts[:-1]):
        nxt = path_parts[i + 1]
        if part not in current:
            current[part] = [] if nxt == "[*]" else {}
        current = current[part]
    if path_parts:
        current[path_parts[-1]] = value


def _resolve_source(data, source_path: str):
    if not source_path:
        return data
    parts = source_path.split(".")
    expand_idx = None
    for i, p in enumerate(parts):
        if p == "[*]":
            expand_idx = i
            break

    if expand_idx is None:
        return _get_by_path(data, parts)

    prefix = parts[:expand_idx]
    suffix = parts[expand_idx + 1:]
    arr = _get_by_path(data, prefix)
    if not isinstance(arr, list):
        return []
    if not suffix:
        return arr
    return [_get_by_path(item, suffix) for item in arr]
