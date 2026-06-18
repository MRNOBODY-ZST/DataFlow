import io
import numpy as np
import pytest
from PIL import Image
from nodes.media.image_pooling import ImagePoolingNode


def _png(w=16, h=16) -> bytes:
    img = Image.fromarray(np.random.randint(0, 255, (h, w, 3), dtype=np.uint8))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_pooling_max_default(ctx):
    ctx.config = {}
    out = ImagePoolingNode().execute([_png()], ctx)
    img = Image.open(io.BytesIO(out))
    assert img.size == (8, 8)


def test_pooling_mean(ctx):
    ctx.config = {"method": "mean"}
    out = ImagePoolingNode().execute([_png()], ctx)
    img = Image.open(io.BytesIO(out))
    assert img.size == (8, 8)


def test_pooling_custom_stride(ctx):
    ctx.config = {"pool_size": 4, "stride": 2}
    out = ImagePoolingNode().execute([_png(16, 16)], ctx)
    img = Image.open(io.BytesIO(out))
    h, w = img.size[1], img.size[0]
    assert h >= 1 and w >= 1


def test_pooling_grayscale(ctx):
    arr = np.random.randint(0, 255, (16, 16), dtype=np.uint8)
    img = Image.fromarray(arr, mode="L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    ctx.config = {}
    out = ImagePoolingNode().execute([buf.getvalue()], ctx)
    assert len(out) > 0
