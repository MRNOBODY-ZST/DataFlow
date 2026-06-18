import io
import pytest
import numpy as np

try:
    import rasterio
except ImportError:
    pytest.skip("rasterio not installed", allow_module_level=True)

from nodes.media.image_drone_index import ImageDroneIndexNode


def _make_four_band_tiff(descriptions: list[str], w=8, h=8) -> bytes:
    profile = {
        "driver": "GTiff",
        "width": w,
        "height": h,
        "count": 4,
        "dtype": "float32",
        "crs": None,
        "transform": rasterio.transform.from_origin(121.0, 31.0, 0.001, -0.001),
        "nodata": 0,
    }
    buf = io.BytesIO()
    with rasterio.open(buf, "w", **profile) as dst:
        for i in range(1, 5):
            arr = np.random.rand(h, w).astype(np.float32) * 0.5 + 0.25
            dst.write(arr, i)
    return buf.getvalue()


def test_drone_index_multi_files(ctx):
    raw = _make_four_band_tiff(["Green", "Red", "RedEdge", "NIR"])
    out = ImageDroneIndexNode().execute([raw], ctx)
    assert isinstance(out, dict)
    assert "multi_files" in out
    assert isinstance(out["multi_files"], list)
    assert len(out["multi_files"]) == 12


def test_drone_index_multi_files_are_tiff(ctx):
    raw = _make_four_band_tiff(["Green", "Red", "RedEdge", "NIR"])
    out = ImageDroneIndexNode().execute([raw], ctx)
    for b in out["multi_files"]:
        with rasterio.open(io.BytesIO(b)) as src:
            assert src.count == 1
            assert src.height == 8
            assert src.width == 8
