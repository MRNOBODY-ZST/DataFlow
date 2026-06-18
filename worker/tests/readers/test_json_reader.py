import json
import pytest
from nodes.readers.json_reader import JsonReaderNode


def _put(mock_minio, bucket: str, key: str, data: bytes):
    full = f"{bucket}/{key}"
    mock_minio.store[full] = data


def test_json_reader_object(mock_minio, ctx, sample_json_bytes):
    _put(mock_minio, "in", "d.json", sample_json_bytes)
    ctx.config = {"key": "d.json"}
    out = JsonReaderNode().execute([], ctx)
    assert out == {"x": 1, "y": {"nested": [1, 2, 3]}}


def test_json_reader_array(mock_minio, ctx):
    _put(mock_minio, "in", "a.json", b'[1, 2, {"k": true}]')
    ctx.config = {"key": "a.json"}
    out = JsonReaderNode().execute([], ctx)
    assert out == [1, 2, {"k": True}]


def test_json_reader_malformed(mock_minio, ctx):
    _put(mock_minio, "in", "b.json", b"{not valid json")
    ctx.config = {"key": "b.json"}
    with pytest.raises(RuntimeError):
        JsonReaderNode().execute([], ctx)


def test_json_reader_input_key_alias(mock_minio, ctx, sample_json_bytes):
    _put(mock_minio, "in", "x.json", sample_json_bytes)
    ctx.config = {"input_key": "x.json"}
    assert JsonReaderNode().execute([], ctx)["x"] == 1
