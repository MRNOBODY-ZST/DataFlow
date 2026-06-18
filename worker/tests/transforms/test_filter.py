import pandas as pd
import pytest
from nodes.transforms.filter_node import FilterNode


def _df(n: int = 5) -> pd.DataFrame:
    return pd.DataFrame({"name": ["a", "b", "c", "d", "e"][:n], "age": [10, 20, 30, 40, 50][:n]})


def test_filter_basic(ctx):
    ctx.config = {"query": "age > 30"}
    out = FilterNode().execute([_df()], ctx)
    assert list(out["age"]) == [40, 50]
    assert list(out["name"]) == ["d", "e"]


def test_filter_empty_query_returns_same(ctx):
    base = _df()
    ctx.config = {"query": ""}
    out = FilterNode().execute([base], ctx)
    assert out.shape == base.shape
    assert list(out["age"]) == list(base["age"])


def test_filter_bad_query_raises(ctx):
    ctx.config = {"query": "age not a valid pandas"}
    with pytest.raises(RuntimeError):
        FilterNode().execute([_df()], ctx)


def test_filter_non_df_raises(ctx):
    ctx.config = {"query": "x > 1"}
    with pytest.raises(RuntimeError):
        FilterNode().execute([[{"x": 1}]], ctx)
