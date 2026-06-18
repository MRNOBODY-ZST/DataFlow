import pytest
import numpy as np

try:
    import rasterio
except ImportError:
    pytest.skip("rasterio not installed", allow_module_level=True)

from nodes.droneIndices._drone_base import (
    safe_divide,
    normalize_name,
    identify_bands as drone_identify_bands,
    calc_ndvi,
    calc_gndvi,
    calc_ndre,
    calc_lci,
    calc_sipi2,
    calc_gci,
    calc_cirededge,
    calc_ngrdi,
    calc_rvi,
    calc_dvi,
    calc_savi,
    calc_msavi,
)


def test_safe_divide_zero_denominator_nan():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([1.0, 0.0, 2.0])
    out = safe_divide(a, b)
    assert np.isfinite(out[0])
    assert np.isnan(out[1])
    assert np.isfinite(out[2])


def test_safe_divide_eps_small_denominator():
    a = np.array([1.0])
    b = np.array([1e-10])
    out = safe_divide(a, b)
    assert np.isnan(out[0])


def test_normalize_name():
    assert normalize_name(" Red Edge ") == "rededge"
    assert normalize_name("B_04-Test") == "b04test"
    assert normalize_name("NIR") == "nir"


def test_identify_bands_drone(tmp_path=None):
    import io

    from PIL import Image

    data = np.zeros((4, 4, 4), dtype=np.uint16) + 1000
    buf = io.BytesIO()
    with rasterio.open(
        buf,
        "w",
        driver="GTiff",
        width=4,
        height=4,
        count=4,
        dtype="uint16",
        nodata=0,
        crs=None,
        transform=rasterio.transform.from_origin(121.0, 31.0, 0.001, -0.001),
    ) as dst:
        dst.write(data[:, :, 0], 1)
        dst.set_band_description(1, "Green")
        dst.write(data[:, :, 1], 2)
        dst.set_band_description(2, "Red")
        dst.write(data[:, :, 2], 3)
        dst.set_band_description(3, "RedEdge")
        dst.write(data[:, :, 3], 4)
        dst.set_band_description(4, "NIR")

    buf.seek(0)
    with rasterio.open(io.BytesIO(buf.getvalue())) as src:
        band_map = drone_identify_bands(src)
    assert "Green" in band_map
    assert "Red" in band_map
    assert "RedEdge" in band_map
    assert "NIR" in band_map


def _four_bands():
    return {
        "Green": np.array([[100.0, 200.0]], dtype=np.float32),
        "Red": np.array([[50.0, 150.0]], dtype=np.float32),
        "RedEdge": np.array([[80.0, 120.0]], dtype=np.float32),
        "NIR": np.array([[200.0, 100.0]], dtype=np.float32),
    }


def test_calc_ndvi_expected():
    bands = _four_bands()
    arr = calc_ndvi(bands)
    expected = np.array([
        [(200.0 - 50.0) / (200.0 + 50.0), (100.0 - 150.0) / (100.0 + 150.0)],
    ], dtype=np.float32)
    np.testing.assert_allclose(arr, expected, rtol=1e-5)


def test_calc_gndvi():
    bands = _four_bands()
    arr = calc_gndvi(bands)
    expected = np.array([
        [(200.0 - 100.0) / (200.0 + 100.0), (100.0 - 200.0) / (100.0 + 200.0)],
    ], dtype=np.float32)
    np.testing.assert_allclose(arr, expected, rtol=1e-5)


def test_calc_dvi_equals_diff():
    bands = _four_bands()
    arr = calc_dvi(bands)
    np.testing.assert_allclose(arr, bands["NIR"] - bands["Red"])


def test_calc_msavi_range():
    bands = _four_bands()
    arr = calc_msavi(bands)
    assert np.all(np.isfinite(arr))
    # MSAVI = (2*NIR+1-sqrt(term))/2；NIR/Red �?[0,1] reflectance (float), 输出可能 >0 但理论可 0
    # 这里 NIR=200、Red=50 都是 reflectance 放大数；只检查有�?    assert np.all(arr >= -1)
    assert np.all(arr <= 1.5)


def test_calc_savi_range():
    bands = _four_bands()
    arr = calc_savi(bands)
    assert np.all(np.isfinite(arr))


def test_calc_rvi_ratio():
    bands = _four_bands()
    arr = calc_rvi(bands)
    expected = bands["NIR"] / bands["Red"]
    np.testing.assert_allclose(arr, expected, rtol=1e-5)


def test_calc_ndre():
    bands = _four_bands()
    arr = calc_ndre(bands)
    assert arr.shape == (1, 2)


def test_calc_lci():
    bands = _four_bands()
    arr = calc_lci(bands)
    assert arr.shape == (1, 2)


def test_calc_sipi2():
    bands = _four_bands()
    arr = calc_sipi2(bands)
    assert arr.shape == (1, 2)


def test_calc_gci_positive_for_nir_gt_green():
    bands = _four_bands()
    arr = calc_gci(bands)
    assert arr[0, 0] > 0


def test_calc_cirededge():
    bands = _four_bands()
    arr = calc_cirededge(bands)
    assert np.all(np.isfinite(arr))


def test_calc_ngrdi():
    bands = _four_bands()
    arr = calc_ngrdi(bands)
    assert np.all(np.isfinite(arr))
