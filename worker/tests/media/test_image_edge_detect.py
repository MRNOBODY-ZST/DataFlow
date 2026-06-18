import io
import numpy as np
import pytest
from PIL import Image
from nodes.media.image_edge_detect import ImageEdgeDetectNode


def _png_gradient(w=32, h=32) -> bytes:
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        arr[y, :, :] = y * 8
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_edge_find_edges(ctx):
    ctx.config = {"method": "find_edges"}
    out = ImageEdgeDetectNode().execute([_png_gradient()], ctx)
    assert len(out) > 0


def test_edge_contour(ctx):
    ctx.config = {"method": "contour"}
    out = ImageEdgeDetectNode().execute([_png_gradient()], ctx)
    assert len(out) > 0


def test_edge_edge_enhance(ctx):
    ctx.config = {"method": "edge_enhance"}
    out = ImageEdgeDetectNode().execute([_png_gradient()], ctx)
    assert len(out) > 0


def test_edge_edge_enhance_more(ctx):
    ctx.config = {"method": "edge_enhance_more"}
    out = ImageEdgeDetectNode().execute([_png_gradient()], ctx)
    assert len(out) > 0


def test_edge_sobel(ctx):
    ctx.config = {"method": "sobel"}
    out = ImageEdgeDetectNode().execute([_png_gradient()], ctx)
    assert len(out) > 0


def test_edge_unknown_fallback(ctx):
    ctx.config = {"method": "nope_not_exist"}
    out = ImageEdgeDetectNode().execute([_png_gradient()], ctx)
    assert len(out) > 0
