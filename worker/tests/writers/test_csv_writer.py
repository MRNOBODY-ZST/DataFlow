import pandas as pd
import pytest
from nodes.writers.csv_writer import CsvWriterNode


def _df() -> pd.DataFrame:
    return pd.DataFrame({"a": [1, 2], "b": [3, 4]})


def test_csv_writer_calls_minio_put(mock_minio, ctx):
    ctx.config = {"key": "out"}
    ctx.source_key = "in.csv"
    key = CsvWriterNode().execute([_df()], ctx)
    assert key == "run_t1/out.csv"
    assert len(mock_minio.put_calls) == 1
    bucket, obj_key, raw, ct = mock_minio.put_calls[0]
    assert bucket == "out"
    assert obj_key.endswith(".csv")
    assert b"a,b" in raw
    assert ct == "text/csv"


def test_csv_writer_key_has_ext_already(mock_minio, ctx):
    ctx.config = {"key": "already.csv"}
    key = CsvWriterNode().execute([_df()], ctx)
    assert key.endswith("already.csv")
    assert not key.endswith("already.csv.csv")


def test_csv_writer_non_df_raises(ctx):
    with pytest.raises(RuntimeError):
        CsvWriterNode().execute([{"a": 1}], ctx)


def test_csv_writer_no_input_raises(ctx):
    with pytest.raises(RuntimeError):
        CsvWriterNode().execute([], ctx)
