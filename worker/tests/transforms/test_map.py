import pandas as pd
import pytest
from nodes.transforms.map_node import MapNode


def _df() -> pd.DataFrame:
    return pd.DataFrame({"name": ["a", "b"], "age": [20, 30], "city": ["x", "y"]})


def test_map_rename(ctx):
    ctx.config = {"rename": {"name": "username"}}
    out = MapNode().execute([_df()], ctx)
    assert "username" in out.columns
    assert "name" not in out.columns


def test_map_select(ctx):
    ctx.config = {"select": ["name", "age"]}
    out = MapNode().execute([_df()], ctx)
    assert list(out.columns) == ["name", "age"]


def test_map_rename_then_select(ctx):
    ctx.config = {"rename": {"name": "n"}, "select": ["n", "age"]}
    out = MapNode().execute([_df()], ctx)
    assert list(out.columns) == ["n", "age"]


def test_map_select_ignores_missing(ctx):
    ctx.config = {"select": ["name", "nonexistent", "age"]}
    out = MapNode().execute([_df()], ctx)
    assert list(out.columns) == ["name", "age"]


def test_map_non_df_raises(ctx):
    ctx.config = {}
    with pytest.raises(RuntimeError):
        MapNode().execute([{"a": 1}], ctx)
