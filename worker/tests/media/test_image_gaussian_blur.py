import io
import numpy as np
import pytest
from PIL import Image
from nodes.media.image_gaussian_blur import ImageGaussianBlurNode


def _png(w=32, h=32) -> bytes:
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[h // 2:, :] = 128
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_gaussian_blur_default_radius(ctx):
    ctx.config = {}
    out = ImageGaussianBlurNode().execute([_png()], ctx)
    from PIL import Image as I

    img = I.open(io.BytesIO(out))
    assert img.size == (32, 32)


def test_gaussian_blur_custom_radius(ctx):
    ctx.config = {"radius": 5}
    out1 = ImageGaussianBlurNode().execute([_png()], ctx)
    ctx.config = {"radius": 20}
    out2 = ImageGaussianBlurNode().execute([_png()], ctx)
    assert len(out1) > 0
    assert len(out2) > 0


def test_gaussian_blur_rgba_to_jpeg(ctx):
    arr = np.zeros((16, 16, 4), dtype=np.uint8)
    arr[:, :, 0] = 200
    arr[:, :, 3] = 255
    img = Image.fromarray(arr, mode="RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    ctx.config = {"format": "JPEG"}
    out = ImageGaussianBlurNode().execute([buf.getvalue()], ctx)
    assert out.startswith(b"\xff\xd8\xff")


def test_gaussian_blur_from_minio(mock_minio, ctx):
    raw = _png()
    mock_minio.store["in/photo.png"] = raw
    ctx.config = {"key": "photo.png", "radius": 1}
    out = ImageGaussianBlurNode().execute([], ctx)
    assert len(out) > 0
