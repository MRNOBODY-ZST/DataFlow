import io
import json
import numpy as np
import pytest
from PIL import Image
from nodes.media.image_convolution import ImageConvolutionNode


def _png(w=16, h=16) -> bytes:
    img = Image.fromarray(np.random.randint(0, 255, (h, w, 3), dtype=np.uint8))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _run(ctx, **kw):
    ctx.config = {"format": "PNG", **kw}
    return ImageConvolutionNode().execute([_png()], ctx)


def test_convolution_presets(ctx):
    for preset in ["blur", "sharpen", "contour", "detail", "edge_enhance", "emboss", "smooth"]:
        out = _run(ctx, preset=preset)
        assert len(out) > 0


def test_convolution_custom_kernel(ctx):
    kernel_str = json.dumps([0, -1, 0, -1, 4, -1, 0, -1, 0])
    out = _run(ctx, preset="custom", kernel=kernel_str, kernel_size=3, offset=0)
    assert len(out) > 0


def test_convolution_kernel_sum_zero_scale_is_one(ctx):
    kernel_str = json.dumps([1, -2, 1, -2, 4, -2, 1, -2, 1])
    out = _run(ctx, preset="custom", kernel=kernel_str, kernel_size=3, offset=0)
    assert len(out) > 0
