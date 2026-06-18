import pytest
from nodes.transforms.json_mapper import JsonMapperNode


def test_json_mapper_simple(ctx):
    ctx.config = {"mappings": [{"source": "a", "target": "A"}]}
    out = JsonMapperNode().execute([{"a": 1, "b": 2}], ctx)
    assert out == {"A": 1}


def test_json_mapper_nested(ctx):
    ctx.config = {"mappings": [{"source": "a.b.c", "target": "out.v"}]}
    out = JsonMapperNode().execute([{"a": {"b": {"c": 42}}}], ctx)
    assert out == {"out": {"v": 42}}


def test_json_mapper_default(ctx):
    ctx.config = {"mappings": [{"source": "missing", "target": "m", "default": 99}]}
    out = JsonMapperNode().execute([{"a": 1}], ctx)
    assert out == {"m": 99}


def test_json_mapper_array_expand(ctx):
    data = {"items": [{"id": 1}, {"id": 2}, {"id": 3}]}
    ctx.config = {"mappings": [{"source": "items.[*].id", "target": "ids"}]}
    out = JsonMapperNode().execute([data], ctx)
    assert out == {"ids": [1, 2, 3]}


def test_json_mapper_empty_mappings_returns_same(ctx):
    data = {"x": 1}
    ctx.config = {"mappings": []}
    assert JsonMapperNode().execute([data], ctx) == data


def test_json_mapper_no_input(ctx):
    ctx.config = {"mappings": [{"source": "a", "target": "a"}]}
    with pytest.raises(RuntimeError):
        JsonMapperNode().execute([], ctx)
