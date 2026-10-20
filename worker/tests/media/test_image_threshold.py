import io
import numpy as np
import pytest
from PIL import Image
from nodes.media.image_threshold import ImageThresholdNode


def _png(w=16, h=16) -> bytes:
    arr = np.zeros((h, w), dtype=np.uint8)
    arr[: h // 2, :] = 64
    arr[h // 2 :, :] = 192
    img = Image.fromarray(arr, mode="L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_threshold_binary(ctx):
    ctx.config = {"method": "binary", "threshold": 128}
    out = ImageThresholdNode().execute([_png()], ctx)
    assert len(out) > 0


def test_threshold_binary_inv(ctx):
    ctx.config = {"method": "binary_inv", "threshold": 128}
    out = ImageThresholdNode().execute([_png()], ctx)
    assert len(out) > 0


def test_threshold_truncate(ctx):
    ctx.config = {"method": "truncate", "threshold": 128}
    out = ImageThresholdNode().execute([_png()], ctx)
    assert len(out) > 0


def test_threshold_to_zero(ctx):
    ctx.config = {"method": "to_zero", "threshold": 128}
    out = ImageThresholdNode().execute([_png()], ctx)
    assert len(out) > 0


def test_threshold_otsu(ctx):
    ctx.config = {"method": "otsu"}
    out = ImageThresholdNode().execute([_png()], ctx)
    assert len(out) > 0


def test_threshold_default_binary(ctx):
    ctx.config = {}
    out = ImageThresholdNode().execute([_png()], ctx)
    assert len(out) > 0
