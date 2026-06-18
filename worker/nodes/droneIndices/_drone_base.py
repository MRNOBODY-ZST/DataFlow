from __future__ import annotations
from typing import Dict, Any, List, Callable, Optional
import io
import os
import tempfile
import shutil
import numpy as np
import rasterio
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import err_s2_no_bands, err_s2_missing, err_drone_no_bands, err_tiff_open, err_math, err_tiff_write, err_minio_upload, err_no_upstream, err_generic, err_minio_not_found, err_minio_missing_key, err_bad_input_type, err_empty_bytes

# ─────────────────────────────────────────────
# 基本参数
# ─────────────────────────────────────────────
ZERO_AS_NODATA = True

# ─────────────────────────────────────────────
# 波段名称映射
# ─────────────────────────────────────────────
BAND_KEYWORDS = {
    "green": "Green", "g": "Green", "b2": "Green", "band2": "Green", "b02": "Green",
    "red": "Red", "r": "Red", "b3": "Red", "band3": "Red", "b03": "Red",
    "rededge": "RedEdge", "red_edge": "RedEdge", "re": "RedEdge",
    "b4": "RedEdge", "band4": "RedEdge", "b04": "RedEdge",
    "b5_rededge": "RedEdge", "band5_rededge": "RedEdge",
    "nir": "NIR", "n": "NIR",
    "b5": "NIR", "band5": "NIR", "b05": "NIR",
    "b8": "NIR", "band8": "NIR", "b08": "NIR",
}

# ─────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────
def safe_divide(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    out = np.full_like(numerator, np.nan, dtype=np.float32)
    valid = (
        np.isfinite(numerator)
        & np.isfinite(denominator)
        & (np.abs(denominator) > 1e-8)
    )
    out[valid] = numerator[valid] / denominator[valid]
    return out

def normalize_name(name: str) -> str:
    return str(name).lower().replace(" ", "").replace("_", "").replace("-", "")

def identify_bands(src) -> dict:
    identified = {}
    descs = list(src.descriptions)
    for band_idx, desc in enumerate(descs, 1):
        if desc is None: continue
        norm = normalize_name(desc)
        if norm in BAND_KEYWORDS:
            identified[BAND_KEYWORDS[norm]] = band_idx
            continue
        for kw in sorted(BAND_KEYWORDS.keys(), key=len, reverse=True):
            if normalize_name(kw) in norm:
                identified[BAND_KEYWORDS[kw]] = band_idx
                break
    return identified

def load_band(src, band_idx: int) -> np.ndarray:
    data = src.read(band_idx).astype(np.float32)
    if src.nodata is not None:
        data[data == src.nodata] = np.nan
    if ZERO_AS_NODATA:
        data[data <= 0] = np.nan
    return data

def array_to_tiff_bytes(arr: np.ndarray, profile: Dict[str, Any]) -> bytes:
    arr = arr.astype(np.float32)
    valid = np.isfinite(arr)
    if np.any(valid):
        min_val = np.nanmin(arr)
        max_val = np.nanmax(arr)
        if max_val > min_val:
            arr = (arr - min_val) / (max_val - min_val) * 255.0
    arr = np.nan_to_num(arr, nan=0.0)
    arr = np.clip(arr, 0, 255).astype(np.uint8)

    out_profile = profile.copy()
    out_profile.update(
        dtype="uint8",
        count=1,
        nodata=0,
        compress="lzw",
        predictor=2,
    )
    buf = io.BytesIO()
    with rasterio.open(buf, "w", **out_profile) as dst:
        dst.write(arr, 1)
    return buf.getvalue()

def read_bytes_to_array(data: bytes) -> tuple[np.ndarray, dict]:
    with rasterio.MemoryFile(data) as mf:
        with mf.open() as ds:
            arr = ds.read(1).astype(np.float32)
            prof = ds.profile.copy()
    return arr, prof

# ─────────────────────────────────────────────
# 指数计算函数（单波段 / 原始 DN 比值型）
# ─────────────────────────────────────────────
def calc_ndvi(bands):
    nir = bands["NIR"].astype(np.float32)
    red = bands["Red"].astype(np.float32)
    return safe_divide(nir - red, nir + red)

def calc_gndvi(bands):
    nir = bands["NIR"].astype(np.float32)
    green = bands["Green"].astype(np.float32)
    return safe_divide(nir - green, nir + green)

def calc_ndre(bands):
    nir = bands["NIR"].astype(np.float32)
    red_edge = bands["RedEdge"].astype(np.float32)
    return safe_divide(nir - red_edge, nir + red_edge)

def calc_lci(bands):
    nir = bands["NIR"].astype(np.float32)
    red_edge = bands["RedEdge"].astype(np.float32)
    red = bands["Red"].astype(np.float32)
    return safe_divide(nir - red_edge, nir + red)

def calc_sipi2(bands):
    nir = bands["NIR"].astype(np.float32)
    green = bands["Green"].astype(np.float32)
    red = bands["Red"].astype(np.float32)
    return safe_divide(nir - green, nir - red)

def calc_gci(bands):
    nir = bands["NIR"].astype(np.float32)
    green = bands["Green"].astype(np.float32)
    return safe_divide(nir, green) - 1.0

def calc_cirededge(bands):
    nir = bands["NIR"].astype(np.float32)
    red_edge = bands["RedEdge"].astype(np.float32)
    return safe_divide(nir, red_edge) - 1.0

def calc_ngrdi(bands):
    green = bands["Green"].astype(np.float32)
    red = bands["Red"].astype(np.float32)
    return safe_divide(green - red, green + red)

def calc_rvi(bands):
    nir = bands["NIR"].astype(np.float32)
    red = bands["Red"].astype(np.float32)
    return safe_divide(nir, red)

def calc_dvi(bands):
    nir = bands["NIR"].astype(np.float32)
    red = bands["Red"].astype(np.float32)
    return (nir - red).astype(np.float32)

def calc_savi(bands):
    L = 0.5
    nir = bands["NIR"].astype(np.float32)
    red = bands["Red"].astype(np.float32)
    return safe_divide(
        (nir - red) * (1.0 + L),
        nir + red + L,
    )

def calc_msavi(bands):
    nir = bands["NIR"].astype(np.float32)
    red = bands["Red"].astype(np.float32)
    msavi_term = (2.0 * nir + 1.0) ** 2 - 8.0 * (nir - red)
    msavi_term = np.where(msavi_term < 0, 0, msavi_term)
    return (
        (2.0 * nir + 1.0 - np.sqrt(msavi_term)) / 2.0
    ).astype(np.float32)


def _get_input_bytes(raw_inputs: list, ctx: NodeContext) -> bytes:
    if raw_inputs:
        data = raw_inputs[0]
        if isinstance(data, list):
            data = data[0]
        if isinstance(data, dict):
            data = data.get("data", b"")
        if isinstance(data, bytes) and data:
            return data

    bucket = getattr(ctx, "input_bucket", None) or (ctx.config.get("bucket", "") if getattr(ctx, "config", None) else "")
    key = getattr(ctx, "input_key", None) or (ctx.config.get("key", "") if getattr(ctx, "config", None) else "")
    if not key:
        err_minio_missing_key(getattr(ctx, 'node_id', '?'))
    try:
        response = ctx.minio_client.get_object(bucket, key)
        try:
            raw = response.read()
        finally:
            response.close()
            response.release_conn()
        return raw
    except Exception as e:
        err_minio_not_found(getattr(ctx, 'node_id', '?'), key, bucket or "dataflow-input")


def run_single_index(
    index_name: str,
    raw_inputs: list,
    ctx: NodeContext,
    calc_fn: Optional[Callable] = None,
    required_bands: Optional[List[str]] = None,
    node_label: Optional[str] = None,
) -> str:
    if calc_fn is None:
        calc_fn = globals().get(f"calc_{index_name.lower()}")
        if calc_fn is None:
            err_generic(f"drone_{index_name}", f"未找到 calc_{index_name.lower()}")

    if required_bands is None:
        required_bands = ["NIR", "Red", "Green", "RedEdge"]

    label = node_label or f"drone_{index_name}"

    try:
        raw = _get_input_bytes(raw_inputs, ctx)
    except RuntimeError:
        raise
    except Exception as e:
        err_no_upstream(label, "取输入失败: " + str(e))

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "result.tif")
        final_key = ""
        try:
            try:
                with rasterio.MemoryFile(raw) as mf:
                    with mf.open() as src:
                        band_map = identify_bands(src)
                        profile = src.profile
                        bands = {}
                        for name, idx in band_map.items():
                            bands[name] = load_band(src, idx)
            except rasterio.RasterioIOError as e:
                err_tiff_open(label, str(e))
            except Exception as e:
                err_tiff_open(label, str(e))

            missing = [b for b in required_bands if b not in bands]
            if missing:
                err_s2_missing(label, str(missing), str(list(bands.keys())))

            try:
                arr = calc_fn(bands)
            except Exception as e:
                err_math(label, index_name, str(e))

            try:
                tiff_bytes = array_to_tiff_bytes(arr, profile)
                with open(out_path, "wb") as f:
                    f.write(tiff_bytes)
            except Exception as e:
                err_tiff_write(label, str(e))

            source_key = getattr(ctx, "source_key", None)
            if source_key is None:
                cfg = getattr(ctx, "config", None)
                source_key = cfg.get("key", "input.tif") if cfg else "input.tif"
            stem = os.path.splitext(os.path.basename(source_key))[0]
            out_key = ctx.output_key(f"{stem}_{index_name.lower()}.tif")
            try:
                ctx.minio_client.fput_object(
                    getattr(ctx, "output_bucket", ""),
                    out_key,
                    out_path,
                )
            except Exception as e:
                err_minio_upload(label, out_key, str(e))
            final_key = out_key
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    return final_key


def _bytes_to_bytes_drone(
    index_name: str,
    raw,
    calc_fn: Callable,
    required_bands,
    node_label: str,
) -> bytes:
    required_bands = list(required_bands) if not isinstance(required_bands, list) else required_bands
    if raw is None:
        err_no_upstream(node_label)
    if not isinstance(raw, (bytes, bytearray)):
        err_bad_input_type(node_label, type(raw).__name__, "影像字节流 bytes")
    if len(raw) == 0:
        err_empty_bytes(node_label)
    try:
        with rasterio.MemoryFile(raw) as mf:
            with mf.open() as src:
                band_map = identify_bands(src)
                profile = src.profile
                bands = {}
                for name, idx in band_map.items():
                    bands[name] = load_band(src, idx)

                if not bands:
                    total = src.count
                    fmt = profile.get("driver", "?")
                    d = str(list(src.descriptions))[:200]
                    err_drone_no_bands(node_label, total, f"driver={fmt}, descriptions={d}")
    except RuntimeError:
        raise
    except rasterio.RasterioIOError as e:
        err_tiff_open(node_label, str(e))
    except Exception as e:
        err_tiff_open(node_label, str(e))

    missing = [b for b in required_bands if b not in bands]
    if missing:
        err_s2_missing(node_label, str(missing), str(list(bands.keys())))

    try:
        arr = calc_fn(bands)
    except Exception as e:
        err_math(node_label, index_name, str(e))

    try:
        return array_to_tiff_bytes(arr, profile)
    except Exception as e:
        err_tiff_write(node_label, str(e))


def make_execute_for_drone(
    index_name: str,
    calc_fn: Callable,
    required_bands,
    node_label: str,
):
    def execute(self, inputs, ctx):
        if not inputs:
            err_no_upstream(node_label)
        data = inputs[0]
        if isinstance(data, list):
            data = data[0]
        if isinstance(data, dict):
            data = data.get("data", b"")
        if data is None or data == b"":
            err_no_upstream(node_label)
        return _bytes_to_bytes_drone(
            index_name, data, calc_fn, required_bands, node_label,
        )
    return execute
