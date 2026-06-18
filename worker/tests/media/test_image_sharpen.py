import io
import numpy as np
import pytest
from PIL import Image
from nodes.media.image_sharpen import ImageSharpenNode


def _png(w=32, h=32) -> bytes:
    img = Image.fromarray(np.random.randint(0, 255, (h, w, 3), dtype=np.uint8))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_sharpen_unsharp_mask_default(ctx):
    ctx.config = {}
    out = ImageSharpenNode().execute([_png()], ctx)
    assert len(out) > 0


def test_sharpen_sharpen_filter(ctx):
    ctx.config = {"method": "sharpen_filter"}
    out = ImageSharpenNode().execute([_png()], ctx)
    assert len(out) > 0


def test_sharpen_detail(ctx):
    ctx.config = {"method": "detail"}
    out = ImageSharpenNode().execute([_png()], ctx)
    assert len(out) > 0


def test_sharpen_with_factor_plus(ctx):
    ctx.config = {"factor": 2.0}
    out = ImageSharpenNode().execute([_png()], ctx)
    assert len(out) > 0
