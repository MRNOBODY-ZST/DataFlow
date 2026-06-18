import io
import pytest
import numpy as np

try:
    import rasterio
except ImportError:
    pytest.skip("rasterio not installed", allow_module_level=True)

from nodes.media.image_s2_indices import ImageS2IndicesNode


def _make_s2_tiff(descriptions: list[str], w=6, h=6) -> bytes:
    profile = {
        "driver": "GTiff",
        "width": w,
        "height": h,
        "count": len(descriptions),
        "dtype": "uint16",
        "nodata": 0,
        "crs": None,
        "transform": rasterio.transform.from_origin(121.0, 31.0, 0.001, -0.001),
    }
    buf = io.BytesIO()
    with rasterio.open(buf, "w", **profile) as dst:
        for i, name in enumerate(descriptions, 1):
            arr = (np.random.rand(h, w).astype(np.float64) * 5000 + 500).astype(np.uint16)
            dst.write(arr, i)
            dst.set_band_description(i, name)
    return buf.getvalue()


def test_s2_indices_multi_files(ctx, s2_real_tiff_bytes):
    raw = s2_real_tiff_bytes
    out = ImageS2IndicesNode().execute([raw], ctx)
    assert isinstance(out, dict)
    assert "multi_files" in out
    assert len(out["multi_files"]) >= 3


def test_s2_indices_tiff_valid(ctx, s2_real_tiff_bytes):
    raw = s2_real_tiff_bytes
    out = ImageS2IndicesNode().execute([raw], ctx)
    for b in out["multi_files"]:
        with rasterio.open(io.BytesIO(b)) as src:
            assert src.count == 1


def test_s2_indices_only_creates_supported(ctx):
    raw = _make_s2_tiff(["B3", "B8"])
    out = ImageS2IndicesNode().execute([raw], ctx)
    assert len(out["multi_files"]) == 2
