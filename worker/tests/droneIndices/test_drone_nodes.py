import io
import sys
import pytest
import numpy as np

try:
    import rasterio
except ImportError:
    pytest.skip("rasterio not installed", allow_module_level=True)

from nodes.droneIndices import (
    image_drone_ndvi,
    image_drone_gndvi,
    image_drone_ndre,
    image_drone_lci,
    image_drone_sipi2,
    image_drone_gci,
    image_drone_cirededge,
    image_drone_ngrdi,
    image_drone_rvi,
    image_drone_dvi,
    image_drone_savi,
    image_drone_msavi,
)

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))


def _make_tiff_bytes(descriptions: list[str], dtype: str = "float32", h: int = 8, w: int = 8) -> bytes:
    profile = {
        "driver": "GTiff",
        "width": w,
        "height": h,
        "count": len(descriptions),
        "dtype": dtype,
        "crs": None,
        "transform": rasterio.transform.from_origin(121.0, 31.0, 0.001, -0.001),
        "nodata": 0,
    }
    buf = io.BytesIO()
    with rasterio.open(buf, "w", **profile) as dst:
        for i, desc in enumerate(descriptions, 1):
            if dtype == "uint16":
                arr = (np.random.rand(h, w).astype(np.float64) * 5000 + 1000).astype(np.uint16)
            else:
                arr = (np.random.rand(h, w).astype(np.float32) * 0.6 + 0.2).astype(np.float32)
            dst.write(arr, i)
            dst.set_band_description(i, desc)
    return buf.getvalue()


def _check_tiff_bytes(raw: bytes, expected_shape: tuple[int, int] | None = None):
    buf = io.BytesIO(raw)
    with rasterio.open(buf) as src:
        if expected_shape:
            assert (src.height, src.width) == expected_shape
        band = src.read(1)
        assert band.dtype == np.float32 or band.dtype == np.uint8


def _run_and_check(node_cls, descriptions):
    raw = _make_tiff_bytes(descriptions)
    from nodes.base import NodeContext
    import types

    fake = types.SimpleNamespace(
        get_object=lambda *a, **k: None,
        put_object=lambda *a, **k: None,
        fput_object=lambda *a, **k: None,
        list_objects=lambda *a, **k: [],
    )
    ctx = NodeContext(
        task_id="t", node_id="n", config={},
        minio_client=fake,
        input_bucket="in", output_bucket="out", temp_bucket="tmp",
        output_prefix="run_t",
        source_key="s.tif",
    )
    out = node_cls().execute([raw], ctx)
    if isinstance(out, dict):
        if "multi_files" in out:
            bytes_list = out["multi_files"]
            assert isinstance(bytes_list, list) and len(bytes_list) >= 1
            for b in bytes_list:
                _check_tiff_bytes(b)
            return out
        if "data" in out:
            return out["data"]
    return out


def test_drone_ndvi(ctx):
    raw = _make_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    out = image_drone_ndvi.ImageDroneNdviNode().execute([raw], ctx)
    assert isinstance(out, bytes) or ("multi_files" not in out)
    if isinstance(out, bytes):
        _check_tiff_bytes(out, (8, 8))


def test_drone_gndvi(ctx):
    raw = _make_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    out = image_drone_gndvi.ImageDroneGndviNode().execute([raw], ctx)
    assert isinstance(out, bytes)


def test_drone_ndre(ctx):
    raw = _make_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    out = image_drone_ndre.ImageDroneNdreNode().execute([raw], ctx)
    assert isinstance(out, bytes)


def test_drone_lci(ctx):
    raw = _make_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    out = image_drone_lci.ImageDroneLciNode().execute([raw], ctx)
    assert isinstance(out, bytes)


def test_drone_sipi2(ctx):
    raw = _make_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    out = image_drone_sipi2.ImageDroneSipi2Node().execute([raw], ctx)
    assert isinstance(out, bytes)


def test_drone_gci(ctx):
    raw = _make_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    out = image_drone_gci.ImageDroneGciNode().execute([raw], ctx)
    assert isinstance(out, bytes)


def test_drone_cirededge(ctx):
    raw = _make_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    out = image_drone_cirededge.ImageDroneCirededgeNode().execute([raw], ctx)
    assert isinstance(out, bytes)


def test_drone_ngrdi(ctx):
    raw = _make_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    out = image_drone_ngrdi.ImageDroneNgrdiNode().execute([raw], ctx)
    assert isinstance(out, bytes)


def test_drone_rvi(ctx):
    raw = _make_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    out = image_drone_rvi.ImageDroneRviNode().execute([raw], ctx)
    assert isinstance(out, bytes)


def test_drone_dvi(ctx):
    raw = _make_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    out = image_drone_dvi.ImageDroneDviNode().execute([raw], ctx)
    assert isinstance(out, bytes)


def test_drone_savi(ctx):
    raw = _make_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    out = image_drone_savi.ImageDroneSaviNode().execute([raw], ctx)
    assert isinstance(out, bytes)


def test_drone_msavi_finite(ctx):
    raw = _make_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    out = image_drone_msavi.ImageDroneMsaviNode().execute([raw], ctx)
    assert isinstance(out, bytes)
    buf = io.BytesIO(out)
    with rasterio.open(buf) as src:
        arr = src.read(1)
        finite = arr[np.isfinite(arr)]
        assert finite.size > 0
        # 值域仅需有限即可（MSAVI 公式在边界可能出负）
        assert np.all(np.isfinite(arr))


def test_drone_ndvi_in_range(ctx):
    raw = _make_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    out = image_drone_ndvi.ImageDroneNdviNode().execute([raw], ctx)
    buf = io.BytesIO(out)
    with rasterio.open(buf) as src:
        arr = src.read(1)
        assert arr.dtype == np.uint8
        assert np.all(arr >= 0)
        assert np.all(arr <= 255)
