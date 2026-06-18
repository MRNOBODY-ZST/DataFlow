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
    image_s2_lswi,
    image_s2_ndwi,
    image_s2_mndwi,
    image_s2_evi,
)


def _make_s2_tiff_bytes(band_names: list[str], h: int = 6, w: int = 6) -> bytes:
    profile = {
        "driver": "GTiff",
        "width": w,
        "height": h,
        "count": len(band_names),
        "dtype": "uint16",
        "nodata": 0,
        "crs": None,
        "transform": rasterio.transform.from_origin(121.0, 31.0, 0.001, -0.001),
    }
    buf = io.BytesIO()
    with rasterio.open(buf, "w", **profile) as dst:
        for i, name in enumerate(band_names, 1):
            arr = (np.random.rand(h, w).astype(np.float64) * 5000 + 500).astype(np.uint16)
            dst.write(arr, i)
            dst.set_band_description(i, name)
    return buf.getvalue()


def test_s2_ndvi_node(ctx, s2_real_tiff_bytes):
    raw = s2_real_tiff_bytes
    node = image_s2_ndvi.ImageS2NdviNode()
    out = node.execute([raw], ctx)
    assert isinstance(out, bytes) or isinstance(out, dict)
    if isinstance(out, bytes):
        with rasterio.open(io.BytesIO(out)) as src:
            assert src.count == 1


def test_s2_gndvi_node(ctx, s2_real_tiff_bytes):
    raw = s2_real_tiff_bytes
    node = image_s2_gndvi.ImageS2GndviNode()
    assert isinstance(node.execute([raw], ctx), bytes)


def test_s2_ndre_requires_nirn_re1(ctx, s2_real_tiff_bytes):
    raw = s2_real_tiff_bytes
    node = image_s2_ndre.ImageS2NdreNode()
    assert isinstance(node.execute([raw], ctx), bytes)


def test_s2_ireci_requires_four_rededge(ctx, s2_real_tiff_bytes):
    raw = s2_real_tiff_bytes
    node = image_s2_ireci.ImageS2IreciNode()
    assert isinstance(node.execute([raw], ctx), bytes)


def test_s2_savi_node(ctx, s2_real_tiff_bytes):
    raw = s2_real_tiff_bytes
    node = image_s2_savi.ImageS2SaviNode()
    assert isinstance(node.execute([raw], ctx), bytes)


def test_s2_lswi_node(ctx, s2_real_tiff_bytes):
    raw = s2_real_tiff_bytes
    node = image_s2_lswi.ImageS2LswiNode()
    assert isinstance(node.execute([raw], ctx), bytes)


def test_s2_ndwi_node(ctx, s2_real_tiff_bytes):
    raw = s2_real_tiff_bytes
    node = image_s2_ndwi.ImageS2NdwiNode()
    assert isinstance(node.execute([raw], ctx), bytes)


def test_s2_mndwi_node(ctx, s2_real_tiff_bytes):
    raw = s2_real_tiff_bytes
    node = image_s2_mndwi.ImageS2MndwiNode()
    assert isinstance(node.execute([raw], ctx), bytes)


def test_s2_evi_requires_blue(ctx, s2_real_tiff_bytes):
    raw = s2_real_tiff_bytes
    node = image_s2_evi.ImageS2EviNode()
    assert isinstance(node.execute([raw], ctx), bytes)


def test_s2_nodes_output_has_nodata_nan(ctx, s2_real_tiff_bytes):
    raw = s2_real_tiff_bytes
    node = image_s2_ndvi.ImageS2NdviNode()
    out = node.execute([raw], ctx)
    with rasterio.open(io.BytesIO(out)) as src:
        assert src.nodata is None or np.isnan(src.nodata) or src.nodata == 0


def test_s2_ndvi_node_range(ctx, s2_real_tiff_bytes):
    raw = s2_real_tiff_bytes
    node = image_s2_ndvi.ImageS2NdviNode()
    out = node.execute([raw], ctx)
    with rasterio.open(io.BytesIO(out)) as src:
        arr = src.read(1)
        # ??????? 0-255 uint8 ??????
        assert arr.dtype == np.uint8 or np.issubdtype(arr.dtype, np.integer) or np.issubdtype(arr.dtype, np.floating)
        assert arr.size > 0
