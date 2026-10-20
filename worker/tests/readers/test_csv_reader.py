import io
import pytest
import pandas as pd
from nodes.readers.csv_reader import CsvReaderNode


def _put(mock_minio, bucket: str, key: str, data: bytes):
    full = f"{bucket}/{key}"
    mock_minio.store[full] = data


def test_csv_reader_returns_dataframe(mock_minio, ctx, sample_csv_bytes):
    _put(mock_minio, "in", "data.csv", sample_csv_bytes)
    ctx.config = {"key": "data.csv"}
    df = CsvReaderNode().execute([], ctx)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (3, 3)
    assert list(df.columns) == ["a", "b", "c"]
    assert df.iloc[0]["a"] == 1
    assert df.iloc[2]["c"] == 9


def test_csv_reader_input_key_alias(mock_minio, ctx, sample_csv_bytes):
    _put(mock_minio, "in", "d.csv", sample_csv_bytes)
    ctx.config = {"input_key": "d.csv"}
    df = CsvReaderNode().execute([], ctx)
    assert df.shape == (3, 3)


def test_csv_reader_custom_bucket(mock_minio, ctx, sample_csv_bytes):
    _put(mock_minio, "other", "x.csv", sample_csv_bytes)
    ctx.config = {"key": "x.csv", "bucket": "other"}
    df = CsvReaderNode().execute([], ctx)
    assert df.shape == (3, 3)


def test_csv_reader_malformed(mock_minio, ctx):
    # quoting=3 means QUOTE_NONE which requires csv.QUOTE_NONE behavior
    # we just send obviously broken bytes that will choke pandas csv parser
    _put(mock_minio, "in", "bad.csv", b"a,b,c\n1,2,3\n4,5,6\n7,8,9\n\nnot utf8:\xff\xfe\xfd\xfc")
    ctx.config = {"key": "bad.csv"}
    with pytest.raises(RuntimeError):
        CsvReaderNode().execute([], ctx)
