import io
import pytest
import numpy as np

try:
    import rasterio
except ImportError:
    pytest.skip("rasterio not installed", allow_module_level=True)

from nodes.S2Indices._s2_base import (
    INDEX_REGISTRY,
    ALL_INDICES,
    calc_ndvi as s2_calc_ndvi,
    calc_gndvi,
    calc_ndre,
    calc_ireci,
    calc_savi,
    calc_lswi,
    calc_ndwi,
    calc_mndwi,
    calc_evi,
    identify_bands,
    SCALE_FACTOR,
)


def test_scale_factor_is_10k():
    assert SCALE_FACTOR == 10000.0


def test_index_registry_complete():
    assert "NDVI" in INDEX_REGISTRY
    assert "EVI" in INDEX_REGISTRY
    assert "IRECI" in INDEX_REGISTRY
    assert ALL_INDICES[0] == "NDVI"


def test_ndvi_formula_scaled():
    nir = np.array([5000.0, 10000.0], dtype=np.float64)
    red = np.array([2500.0, 2500.0], dtype=np.float64)
    bands = {"NIR": nir, "Red": red}
    out = s2_calc_ndvi(bands)
    expected = (nir / 10000.0 - red / 10000.0) / (nir / 10000.0 + red / 10000.0 + 1e-8)
    np.testing.assert_allclose(out, expected, rtol=1e-6)


def test_ndvi_balanced_is_zero():
    nir = np.array([5000.0], dtype=np.float64)
    red = np.array([5000.0], dtype=np.float64)
    out = s2_calc_ndvi({"NIR": nir, "Red": red})
    assert abs(out[0]) < 1e-6


def test_ndvi_range_true_vegetation():
    nir = np.array([8000.0], dtype=np.float64)
    red = np.array([1000.0], dtype=np.float64)
    out = s2_calc_ndvi({"NIR": nir, "Red": red})
    assert 0.5 < out[0] < 1.0


def test_ndvi_range_soil():
    nir = np.array([3000.0], dtype=np.float64)
    red = np.array([2500.0], dtype=np.float64)
    out = s2_calc_ndvi({"NIR": nir, "Red": red})
    assert abs(out[0]) < 0.5


def test_gndvi():
    nir = np.array([8000.0], dtype=np.float64)
    green = np.array([1000.0], dtype=np.float64)
    out = calc_gndvi({"NIR": nir, "Green": green})
    assert out[0] > 0


def test_ndre_requires_nirn_and_re1():
    nirn = np.array([7000.0], dtype=np.float64)
    re1 = np.array([2000.0], dtype=np.float64)
    out = calc_ndre({"NIRn": nirn, "RE1": re1})
    assert np.isfinite(out[0])


def test_ireci_requires_four_rededge():
    re3 = np.array([6000.0], dtype=np.float64)
    red = np.array([1000.0], dtype=np.float64)
    re1 = np.array([5000.0], dtype=np.float64)
    re2 = np.array([5500.0], dtype=np.float64)
    out = calc_ireci({"RE3": re3, "Red": red, "RE1": re1, "RE2": re2})
    assert np.isfinite(out[0])


def test_savi_formula():
    nir = np.array([8000.0], dtype=np.float64)
    red = np.array([1000.0], dtype=np.float64)
    out = calc_savi({"NIR": nir, "Red": red})
    assert np.isfinite(out[0])
    assert out[0] > 0


def test_lswi():
    nir = np.array([6000.0], dtype=np.float64)
    swir1 = np.array([2000.0], dtype=np.float64)
    out = calc_lswi({"NIR": nir, "SWIR1": swir1})
    assert np.isfinite(out[0])


def test_ndwi():
    green = np.array([4000.0], dtype=np.float64)
    nir = np.array([2000.0], dtype=np.float64)
    out = calc_ndwi({"Green": green, "NIR": nir})
    assert out[0] > 0


def test_mndwi_water():
    green = np.array([3000.0], dtype=np.float64)
    swir1 = np.array([1000.0], dtype=np.float64)
    out = calc_mndwi({"Green": green, "SWIR1": swir1})
    assert out[0] > 0


def test_evi_blue_term():
    nir = np.array([8000.0], dtype=np.float64)
    red = np.array([1000.0], dtype=np.float64)
    blue = np.array([500.0], dtype=np.float64)
    out = calc_evi({"NIR": nir, "Red": red, "Blue": blue})
    assert np.isfinite(out[0])
    assert out[0] > 0


def test_identify_bands_s2_keywords():
    import io

    data = np.ones((4, 4, 8), dtype=np.uint16) * 5000
    profile = {
        "driver": "GTiff",
        "width": 4,
        "height": 4,
        "count": 8,
        "dtype": "uint16",
        "nodata": 0,
        "crs": None,
        "transform": rasterio.transform.from_origin(121.0, 31.0, 0.001, -0.001),
    }
    buf = io.BytesIO()
    with rasterio.open(buf, "w", **profile) as dst:
        for i, name in enumerate(["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A"], 1):
            dst.write(data[:, :, 0], i)
            dst.set_band_description(i, name)
    buf.seek(0)
    with rasterio.open(io.BytesIO(buf.getvalue())) as src:
        band_map = identify_bands(src)
    for expected, keyword in [
        ("Blue", "B2"),
        ("Green", "B3"),
        ("Red", "B4"),
        ("RE1", "B5"),
        ("RE2", "B6"),
        ("RE3", "B7"),
        ("NIR", "B8"),
        ("NIRn", "B8A"),
    ]:
        assert expected in band_map, f"{expected} missing (from {keyword})"
