import io
import pandas as pd
import pytest
from nodes.utils.preview_node import PreviewNode


def _png_bytes() -> bytes:
    from PIL import Image
    img = Image.new("RGB", (4, 4), "blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_preview_bytes_put_into_temp(mock_minio, ctx):
    ctx.config = {}
    ctx.source_key = "data/image.png"
    out = PreviewNode().execute([_png_bytes()], ctx)
    assert out.startswith(b"\x89PNG")
    assert len(mock_minio.put_calls) == 1
    bucket, key, _, ct = mock_minio.put_calls[0]
    assert bucket == "tmp"
    assert key.endswith("image.png")
    assert ct == "image/png"


def test_preview_df_as_csv(mock_minio, ctx):
    ctx.config = {}
    ctx.source_key = "data/x"
    df = pd.DataFrame({"a": [1, 2]})
    PreviewNode().execute([df], ctx)
    _, _, raw, ct = mock_minio.put_calls[0]
    assert b"a" in raw
    assert ct == "text/csv"


def test_preview_list_as_json(mock_minio, ctx):
    ctx.config = {}
    ctx.source_key = "data/x"
    PreviewNode().execute([[1, 2, {"k": True}]], ctx)
    _, _, raw, ct = mock_minio.put_calls[0]
    assert ct == "application/json"
    assert b"1" in raw


def test_preview_tif_to_tiff_extension(mock_minio, ctx):
    ctx.config = {}
    ctx.source_key = "a/b/file.tif"
    PreviewNode().execute([_png_bytes()], ctx)
    _, key, _, _ = mock_minio.put_calls[0]
    assert key.endswith(".tiff")
    assert not key.endswith(".tif")


def test_preview_label_overrides_source(mock_minio, ctx):
    ctx.config = {"label": "override.txt"}
    ctx.source_key = "should_not_appear"
    PreviewNode().execute(["hi"], ctx)
    _, key, _, _ = mock_minio.put_calls[0]
    assert key.endswith("override.txt")


def test_preview_return_value_is_passthrough(mock_minio, ctx):
    payload = {"a": 1}
    ctx.config = {}
    ctx.source_key = "data/x.json"
    out = PreviewNode().execute([payload], ctx)
    assert out is payload


def test_preview_none_passthrough_no_upload(mock_minio, ctx):
    out = PreviewNode().execute([None], ctx)
    assert out is None
    assert len(mock_minio.put_calls) == 0
