import io
import pytest
from PIL import Image
from nodes.media.image_resize import ImageResizeNode


def _png(w: int = 32, h: int = 32) -> bytes:
    img = Image.new("RGB", (w, h), "green")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _open_img(raw: bytes) -> Image.Image:
    return Image.open(io.BytesIO(raw))


def test_resize_width_height(ctx):
    ctx.config = {"width": 64, "height": 48}
    out = ImageResizeNode().execute([_png(32, 32)], ctx)
    img = _open_img(out)
    assert img.size == (64, 48)


def test_resize_width_only_preserves_ratio(ctx):
    ctx.config = {"width": 64}
    out = ImageResizeNode().execute([_png(32, 16)], ctx)
    img = _open_img(out)
    assert img.size[0] == 64
    assert img.size[1] == 32


def test_resize_height_only_preserves_ratio(ctx):
    ctx.config = {"height": 64}
    out = ImageResizeNode().execute([_png(16, 32)], ctx)
    img = _open_img(out)
    assert img.size[1] == 64
    assert img.size[0] == 32


def test_resize_format_jpeg(ctx):
    ctx.config = {"width": 32, "height": 32, "format": "JPEG"}
    out = ImageResizeNode().execute([_png(64, 64)], ctx)
    assert out.startswith(b"\xff\xd8\xff")


def test_resize_from_minio_when_no_input(mock_minio, ctx):
    raw = _png(32, 32)
    mock_minio.store["in/pic.png"] = raw
    ctx.config = {"key": "pic.png", "width": 16, "height": 16}
    out = ImageResizeNode().execute([], ctx)
    img = _open_img(out)
    assert img.size == (16, 16)
