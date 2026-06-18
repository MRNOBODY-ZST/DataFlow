import io
import numpy as np
import pytest
from PIL import Image
from nodes.media.image_format_convert import ImageFormatConvertNode


def _png_bytes() -> bytes:
    arr = np.zeros((32, 32, 3), dtype=np.uint8)
    arr[:, :] = [100, 150, 200]
    img = Image.fromarray(arr, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _rgba_png_bytes() -> bytes:
    arr = np.zeros((16, 16, 4), dtype=np.uint8)
    arr[:, :, 0] = 200
    arr[:, :, 1] = 50
    arr[:, :, 2] = 50
    arr[:, :, 3] = 0
    img = Image.fromarray(arr, mode="RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _single_band_tiff_bytes(w=16, h=16) -> bytes:
    import rasterio
    data = np.random.rand(h, w).astype(np.float32) * 0.5
    profile = {
        "driver": "GTiff",
        "width": w,
        "height": h,
        "count": 1,
        "dtype": "float32",
        "crs": None,
        "transform": rasterio.transform.from_origin(121.0, 31.0, 0.001, -0.001),
        "nodata": 0,
    }
    buf = io.BytesIO()
    with rasterio.open(buf, "w", **profile) as dst:
        dst.write(data, 1)
    return buf.getvalue()


def test_png_to_jpeg(ctx):
    ctx.config = {"format": "JPEG"}
    out = ImageFormatConvertNode().execute([_png_bytes()], ctx)
    assert out.startswith(b"\xff\xd8\xff")


def test_tiff_to_png(ctx):
    ctx.config = {"format": "PNG"}
    out = ImageFormatConvertNode().execute([_single_band_tiff_bytes()], ctx)
    assert out.startswith(b"\x89PNG")


def test_input_required(ctx):
    ctx.config = {"format": "PNG"}
    with pytest.raises(RuntimeError):
        ImageFormatConvertNode().execute([None], ctx)


def test_rgba_to_jpeg_bg_composite(ctx):
    ctx.config = {"format": "JPEG"}
    out = ImageFormatConvertNode().execute([_rgba_png_bytes()], ctx)
    assert out.startswith(b"\xff\xd8\xff")


def test_format_case_insensitive(ctx):
    ctx.config = {"format": "jpeg"}
    out = ImageFormatConvertNode().execute([_png_bytes()], ctx)
    assert out.startswith(b"\xff\xd8\xff")
