import io
import json
import pandas as pd
import pytest
from nodes.writers.minio_writer import MinioWriterNode


def _jpeg_bytes() -> bytes:
    from PIL import Image
    img = Image.new("RGB", (4, 4), "red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _df() -> pd.DataFrame:
    return pd.DataFrame({"k": [1, 2]})


def test_writer_bytes_jpeg_auto_ext(mock_minio, ctx):
    ctx.config = {"key": "out"}
    key = MinioWriterNode().execute([_jpeg_bytes()], ctx)
    assert key.endswith("out.jpg")
    assert len(mock_minio.put_calls) == 1
    _, _, raw, ct = mock_minio.put_calls[0]
    assert raw.startswith(b"\xff\xd8\xff")
    assert ct == "image/jpeg"


def test_writer_df_as_csv(mock_minio, ctx):
    ctx.config = {"key": "t"}
    key = MinioWriterNode().execute([_df()], ctx)
    assert key.endswith("t.csv")
    _, _, raw, ct = mock_minio.put_calls[0]
    assert b"k\n1\n2\n" in raw or b"k" in raw
    assert ct == "text/csv"


def test_writer_str_as_txt(mock_minio, ctx):
    ctx.config = {"key": "m"}
    key = MinioWriterNode().execute(["hello"], ctx)
    assert key.endswith("m.txt")
    _, _, raw, ct = mock_minio.put_calls[0]
    assert raw == b"hello"
    assert ct == "text/plain"


def test_writer_dict_as_json(mock_minio, ctx):
    ctx.config = {"key": "j"}
    key = MinioWriterNode().execute([{"a": [1, 2]}], ctx)
    assert key.endswith("j.json")
    _, _, raw, ct = mock_minio.put_calls[0]
    assert json.loads(raw) == {"a": [1, 2]}
    assert ct == "application/json"


def test_writer_already_has_ext_no_append(mock_minio, ctx):
    ctx.config = {"key": "mystuff.json"}
    key = MinioWriterNode().execute([{"a": 1}], ctx)
    assert key.endswith("mystuff.json")
    assert ".json.json" not in key


def test_writer_multi_files_dict(mock_minio, ctx):
    b = _jpeg_bytes()
    ctx.config = {"key": "group"}
    key = MinioWriterNode().execute([{"multi_files": [b, b]}], ctx)
    assert key == "group"
    assert len(mock_minio.put_calls) == 2


def test_writer_unsupported_type_raises(ctx):
    class Obj:
        pass

    ctx.config = {"key": "o"}
    with pytest.raises(RuntimeError):
        MinioWriterNode().execute([Obj()], ctx)
