import io
import pytest
import numpy as np

try:
    import rasterio
except ImportError:
    pytest.skip("rasterio not installed", allow_module_level=True)

from nodes.S2Indices import (
    image_s2_ndvi,
    image_s2_gndvi,
    image_s2_ndre,
    image_s2_ireci,
    image_s2_savi,
    image_s2_ndwi,
    image_s2_evi,
)


def _make_s2_tiff_bytes(band_names: list[str], dtype: str = "uint16", h: int = 6, w: int = 6) -> bytes:
    profile = {
        "driver": "GTiff",
        "width": w, "height": h,
        "count": len(band_names),
        "dtype": dtype,
        "nodata": 0, "crs": None,
        "transform": rasterio.transform.from_origin(121.0, 31.0, 0.001, -0.001),
    }
    buf = io.BytesIO()
    with rasterio.open(buf, "w", **profile) as dst:
        for i, name in enumerate(band_names, 1):
            arr = (np.random.rand(h, w).astype(np.float64) * 5000 + 500).astype(np.uint16)
            dst.write(arr, i)
            dst.set_band_description(i, name)
    return buf.getvalue()


def test_s2_invalid_tiff_raises_runtimeerror(ctx):
    nodes = [
        image_s2_ndvi.ImageS2NdviNode(),
        image_s2_gndvi.ImageS2GndviNode(),
    ]
    for node in nodes:
        with pytest.raises(RuntimeError) as excinfo:
            node.execute([b"not a tiff file at all"], ctx)
        msg = str(excinfo.value)
        assert "TIFF 解析失败" in msg or "打开影像失败" in msg or "RuntimeError" in msg


def test_s2_missing_bands_raises_runtimeerror(ctx):
    raw = _make_s2_tiff_bytes(["B2", "B3"])
    with pytest.raises(RuntimeError) as excinfo:
        image_s2_ndvi.ImageS2NdviNode().execute([raw], ctx)
    msg = str(excinfo.value)
    assert "缺少必要波段" in msg or "缺少" in msg


def test_s2_empty_input_raises_runtimeerror(ctx):
    with pytest.raises(RuntimeError):
        image_s2_ndvi.ImageS2NdviNode().execute([], ctx)


def test_s2_non_bytes_input_raises_runtimeerror(ctx):
    with pytest.raises(RuntimeError):
        image_s2_ndvi.ImageS2NdviNode().execute(["not bytes"], ctx)


def test_s2_ndre_needs_rededge(ctx):
    raw = _make_s2_tiff_bytes(["B2", "B3", "B4", "B8"])
    with pytest.raises(RuntimeError) as excinfo:
        image_s2_ndre.ImageS2NdreNode().execute([raw], ctx)
    assert "缺少必要波段" in str(excinfo.value)


def test_s2_ireci_needs_four_rededge(ctx):
    raw = _make_s2_tiff_bytes(["B2", "B3", "B4", "B8A"])
    with pytest.raises(RuntimeError) as excinfo:
        image_s2_ireci.ImageS2IreciNode().execute([raw], ctx)
    assert "缺少必要波段" in str(excinfo.value)


def test_s2_ndwi_needs_nir_and_green(ctx):
    raw = _make_s2_tiff_bytes(["B2", "B4", "B8"])
    with pytest.raises(RuntimeError) as excinfo:
        image_s2_ndwi.ImageS2NdwiNode().execute([raw], ctx)
    assert "缺少必要波段" in str(excinfo.value)


def test_s2_runtimeerror_has_node_label(ctx):
    raw = _make_s2_tiff_bytes(["B2", "B3"])
    with pytest.raises(RuntimeError) as excinfo:
        image_s2_ndvi.ImageS2NdviNode().execute([raw], ctx)
    msg = str(excinfo.value)
    assert "S2_ndvi" in msg or "S2_NDVI" in msg or "ndvi" in msg.lower()


def test_s2_evi_needs_blue(ctx):
    raw = _make_s2_tiff_bytes(["B3", "B4", "B8"])
    with pytest.raises(RuntimeError) as excinfo:
        image_s2_evi.ImageS2EviNode().execute([raw], ctx)
    assert "缺少必要波段" in str(excinfo.value)


def test_s2_valid_input_no_exception(ctx):
    raw = _make_s2_tiff_bytes(["B2", "B3", "B4", "B8", "B11"])
    out = image_s2_ndvi.ImageS2NdviNode().execute([raw], ctx)
    assert isinstance(out, bytes)
    with rasterio.open(io.BytesIO(out)) as src:
        assert src.count == 1
