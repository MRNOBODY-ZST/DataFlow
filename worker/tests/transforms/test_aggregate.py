import pandas as pd
import pytest
from nodes.transforms.aggregate_node import AggregateNode


def _df() -> pd.DataFrame:
    return pd.DataFrame({
        "city": ["A", "A", "B", "B", "B"],
        "product": ["x", "y", "x", "y", "z"],
        "amount": [10, 20, 30, 40, 50],
    })


def test_aggregate_basic(ctx):
    ctx.config = {"group_by": ["city"], "agg": {"amount": "sum"}}
    out = AggregateNode().execute([_df()], ctx)
    assert "city" in out.columns
    assert "amount" in out.columns
    row_a = out[out["city"] == "A"].iloc[0]
    assert int(row_a["amount"]) == 30


def test_aggregate_empty_group_by_returns_same(ctx):
    base = _df()
    ctx.config = {"group_by": [], "agg": {"amount": "sum"}}
    out = AggregateNode().execute([base], ctx)
    assert out.shape == base.shape


def test_aggregate_empty_agg_returns_same(ctx):
    base = _df()
    ctx.config = {"group_by": ["city"], "agg": {}}
    out = AggregateNode().execute([base], ctx)
    assert out.shape == base.shape


def test_aggregate_non_df_raises(ctx):
    ctx.config = {"group_by": ["k"], "agg": {"v": "sum"}}
    with pytest.raises(RuntimeError):
        AggregateNode().execute([{"k": "x", "v": 1}], ctx)
