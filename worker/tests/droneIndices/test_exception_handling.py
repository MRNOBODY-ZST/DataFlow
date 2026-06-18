import io
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


def _make_drone_tiff_bytes(descriptions: list[str], dtype: str = "float32", h: int = 8, w: int = 8) -> bytes:
    profile = {
        "driver": "GTiff",
        "width": w, "height": h,
        "count": len(descriptions),
        "dtype": dtype, "crs": None,
        "nodata": 0,
        "transform": rasterio.transform.from_origin(121.0, 31.0, 0.001, -0.001),
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


def test_drone_invalid_tiff_raises_runtimeerror(ctx):
    nodes = [
        image_drone_ndvi.ImageDroneNdviNode(),
        image_drone_gndvi.ImageDroneGndviNode(),
    ]
    for node in nodes:
        with pytest.raises(RuntimeError) as excinfo:
            node.execute([b"not a tiff file at all"], ctx)
        msg = str(excinfo.value)
        assert "TIFF 解析失败" in msg or "打开影像失败" in msg


def test_drone_missing_nir_raises_runtimeerror(ctx):
    raw = _make_drone_tiff_bytes(["Green", "Red"])
    with pytest.raises(RuntimeError) as excinfo:
        image_drone_ndvi.ImageDroneNdviNode().execute([raw], ctx)
    msg = str(excinfo.value)
    assert "缺少必要波段" in msg or "缺少" in msg


def test_drone_missing_red_raises_runtimeerror(ctx):
    raw = _make_drone_tiff_bytes(["Green", "NIR"])
    with pytest.raises(RuntimeError) as excinfo:
        image_drone_ndvi.ImageDroneNdviNode().execute([raw], ctx)
    assert "缺少必要波段" in str(excinfo.value)


def test_drone_empty_input_raises(ctx):
    with pytest.raises(RuntimeError):
        image_drone_ndvi.ImageDroneNdviNode().execute([], ctx)


def test_drone_non_bytes_input_raises(ctx):
    with pytest.raises(RuntimeError):
        image_drone_ndvi.ImageDroneNdviNode().execute(["not bytes"], ctx)


@pytest.mark.parametrize("node_mod,cls_name,label_hint,required_hint", [
    (image_drone_ndvi, "ImageDroneNdviNode", "drone_ndvi", "NIR"),
    (image_drone_gndvi, "ImageDroneGndviNode", "drone_gndvi", "NIR"),
    (image_drone_ndre, "ImageDroneNdreNode", "drone_ndre", "RedEdge"),
    (image_drone_lci, "ImageDroneLciNode", "drone_lci", "RedEdge"),
    (image_drone_sipi2, "ImageDroneSipi2Node", "drone_sipi2", "RedEdge"),
    (image_drone_gci, "ImageDroneGciNode", "drone_gci", "Green"),
    (image_drone_cirededge, "ImageDroneCirededgeNode", "drone_ciredge", "RedEdge"),
    (image_drone_ngrdi, "ImageDroneNgrdiNode", "drone_ngrdi", "Green"),
    (image_drone_rvi, "ImageDroneRviNode", "drone_rvi", "NIR"),
    (image_drone_dvi, "ImageDroneDviNode", "drone_dvi", "NIR"),
    (image_drone_savi, "ImageDroneSaviNode", "drone_savi", "NIR"),
    (image_drone_msavi, "ImageDroneMsaviNode", "drone_msavi", "NIR"),
])
def test_drone_all_nodes_have_runtime_error_wrapping(ctx, node_mod, cls_name, label_hint, required_hint):
    node = getattr(node_mod, cls_name)()
    with pytest.raises(RuntimeError) as excinfo:
        node.execute([b"garbage bytes not a tiff"], ctx)
    msg = str(excinfo.value)
    assert "TIFF 解析失败" in msg or "打开影像失败" in msg or label_hint in msg


def test_drone_runtimeerror_has_node_label(ctx):
    raw = _make_drone_tiff_bytes(["Green"])
    with pytest.raises(RuntimeError) as excinfo:
        image_drone_ndvi.ImageDroneNdviNode().execute([raw], ctx)
    msg = str(excinfo.value)
    assert "drone_ndvi" in msg


def test_drone_rvi_needs_nir(ctx):
    raw = _make_drone_tiff_bytes(["Green", "Red"])
    with pytest.raises(RuntimeError) as excinfo:
        image_drone_rvi.ImageDroneRviNode().execute([raw], ctx)
    msg = str(excinfo.value)
    assert "缺少必要波段" in msg or "NIR" in msg


def test_drone_valid_input_no_exception(ctx):
    raw = _make_drone_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    out = image_drone_ndvi.ImageDroneNdviNode().execute([raw], ctx)
    assert isinstance(out, bytes)
    with rasterio.open(io.BytesIO(out)) as src:
        assert src.count == 1


def test_drone_formula_error_wrapped(ctx, monkeypatch):
    import nodes.droneIndices._drone_base as base_mod

    original = base_mod.calc_ndvi

    def _boom(bands):
        raise ValueError("simulated formula crash")

    monkeypatch.setattr(base_mod, "calc_ndvi", _boom)

    raw = _make_drone_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    with pytest.raises(RuntimeError) as excinfo:
        image_drone_ndvi.ImageDroneNdviNode().execute([raw], ctx)
    msg = str(excinfo.value)
    assert "公式计算失败" in msg or "simulated formula crash" in msg
    monkeypatch.setattr(base_mod, "calc_ndvi", original)


def test_drone_tiff_write_error_wrapped(ctx, monkeypatch):
    import nodes.droneIndices._drone_base as base_mod

    original = base_mod.array_to_tiff_bytes

    def _boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(base_mod, "array_to_tiff_bytes", _boom)

    raw = _make_drone_tiff_bytes(["Green", "Red", "RedEdge", "NIR"])
    with pytest.raises(RuntimeError) as excinfo:
        image_drone_ndvi.ImageDroneNdviNode().execute([raw], ctx)
    assert "结果 TIFF 写出失败" in str(excinfo.value)
    monkeypatch.setattr(base_mod, "array_to_tiff_bytes", original)
