import pytest
import jmespath
from nodes.transforms.json_transform import JsonTransformNode


def test_json_transform_simple(ctx):
    ctx.config = {"expression": "foo.bar"}
    out = JsonTransformNode().execute([{"foo": {"bar": "hello"}}], ctx)
    assert out == "hello"


def test_json_transform_array_wildcard(ctx):
    data = {"items": [{"id": 1}, {"id": 2}, {"id": 3}]}
    ctx.config = {"expression": "items[*].id"}
    out = JsonTransformNode().execute([data], ctx)
    assert out == [1, 2, 3]


def test_json_transform_default_identity(ctx):
    data = {"k": "v"}
    ctx.config = {"expression": "@"}
    assert JsonTransformNode().execute([data], ctx) == data


def test_json_transform_bad_expression(ctx):
    ctx.config = {"expression": "foo["}
    with pytest.raises(RuntimeError):
        JsonTransformNode().execute([{"foo": 1}], ctx)


def test_json_transform_no_input(ctx):
    ctx.config = {"expression": "@"}
    with pytest.raises(RuntimeError):
        JsonTransformNode().execute([], ctx)
