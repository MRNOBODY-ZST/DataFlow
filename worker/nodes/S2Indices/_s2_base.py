from __future__ import annotations
from typing import Dict, Any, List, Callable, Optional
import io
import os
import tempfile
import shutil
import numpy as np
import rasterio
from nodes.base import BaseNode, NodeContext

# ─────────────────────────────────────────────
# 基本参数
# ─────────────────────────────────────────────
EPS = 1e-8

# Sentinel-2 SR DN 缩放因子

SCALE_FACTOR = 10000.0

# GEE 导出影像 nodata=None 时，0 通常是背景/无效值
ZERO_AS_NODATA = True

# ─────────────────────────────────────────────
# 波段名称映射
# ─────────────────────────────────────────────
BAND_KEYWORDS = {
    # Blue - B2
    "b2": "Blue",   "band2": "Blue",  "blue": "Blue",   "b02": "Blue",

    # Green - B3
    "b3": "Green",  "band3": "Green", "green": "Green", "b03": "Green",

    # Red - B4
    "b4": "Red",    "band4": "Red",   "red": "Red",     "b04": "Red",

    # Red Edge 1 - B5
    "b5": "RE1",    "band5": "RE1",   "rededge1": "RE1", "rededge": "RE1",
    "re1": "RE1",   "b05": "RE1",     "red_edge_1": "RE1",

    # Red Edge 2 - B6
    "b6": "RE2",    "band6": "RE2",   "rededge2": "RE2", "re2": "RE2",
    "b06": "RE2",   "red_edge_2": "RE2",

    # Red Edge 3 - B7
    "b7": "RE3",    "band7": "RE3",   "rededge3": "RE3", "re3": "RE3",
    "b07": "RE3",   "red_edge_3": "RE3",

    # NIR broad - B8
    "b8": "NIR",    "band8": "NIR",   "nir": "NIR",     "b08": "NIR",
    "nir_broad": "NIR",

    # NIR narrow - B8A
    "b8a": "NIRn",  "band8a": "NIRn", "nirnarrow": "NIRn", "nir_narrow": "NIRn",
    "b8_a": "NIRn", "band_8a": "NIRn", "b08a": "NIRn",

    # SWIR1 - B11
    "b11": "SWIR1", "band11": "SWIR1", "swir1": "SWIR1", "swir_1": "SWIR1",

    # SWIR2 - B12
    "b12": "SWIR2", "band12": "SWIR2", "swir2": "SWIR2", "swir_2": "SWIR2",
}

# ─────────────────────────────────────────────
# 指数计算函数
# ─────────────────────────────────────────────
def calc_ndvi(bands):
    """NDVI = (NIR - Red) / (NIR + Red)"""
    nir = bands["NIR"].astype(np.float64) / SCALE_FACTOR
    red = bands["Red"].astype(np.float64) / SCALE_FACTOR
    return (nir - red) / (nir + red + EPS)

def calc_gndvi(bands):
    """GNDVI = (NIR - Green) / (NIR + Green)"""
    nir = bands["NIR"].astype(np.float64) / SCALE_FACTOR
    green = bands["Green"].astype(np.float64) / SCALE_FACTOR
    return (nir - green) / (nir + green + EPS)

def calc_ndre(bands):
    """
    NDRE = (NIRn - RE1) / (NIRn + RE1)
    Sentinel-2：NIRn = B8A, RE1 = B5
    """
    nirn = bands["NIRn"].astype(np.float64) / SCALE_FACTOR
    re1 = bands["RE1"].astype(np.float64) / SCALE_FACTOR
    return (nirn - re1) / (nirn + re1 + EPS)

def calc_ireci(bands):
    """
    IRECI = (RE3 - Red) / (RE1 / RE2)
    RE3=B7, Red=B4, RE1=B5, RE2=B6
    """
    re3 = bands["RE3"].astype(np.float64) / SCALE_FACTOR
    red = bands["Red"].astype(np.float64) / SCALE_FACTOR
    re1 = bands["RE1"].astype(np.float64) / SCALE_FACTOR
    re2 = bands["RE2"].astype(np.float64) / SCALE_FACTOR
    return (re3 - red) / ((re1 + EPS) / (re2 + EPS) + EPS)

def calc_savi(bands):
    """SAVI = (NIR - Red) / (NIR + Red + L) * (1 + L), L=0.5"""
    L = 0.5
    nir = bands["NIR"].astype(np.float64) / SCALE_FACTOR
    red = bands["Red"].astype(np.float64) / SCALE_FACTOR
    return (nir - red) / (nir + red + L + EPS) * (1.0 + L)

def calc_lswi(bands):
    """LSWI / NDMI = (NIR - SWIR1) / (NIR + SWIR1)"""
    nir = bands["NIR"].astype(np.float64) / SCALE_FACTOR
    swir1 = bands["SWIR1"].astype(np.float64) / SCALE_FACTOR
    return (nir - swir1) / (nir + swir1 + EPS)

def calc_ndwi(bands):
    """NDWI = (Green - NIR) / (Green + NIR)"""
    green = bands["Green"].astype(np.float64) / SCALE_FACTOR
    nir = bands["NIR"].astype(np.float64) / SCALE_FACTOR
    return (green - nir) / (green + nir + EPS)

def calc_mndwi(bands):
    """MNDWI = (Green - SWIR1) / (Green + SWIR1)"""
    green = bands["Green"].astype(np.float64) / SCALE_FACTOR
    swir1 = bands["SWIR1"].astype(np.float64) / SCALE_FACTOR
    return (green - swir1) / (green + swir1 + EPS)

def calc_evi(bands):
    """EVI = 2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)"""
    nir = bands["NIR"].astype(np.float64)/SCALE_FACTOR
    red = bands["Red"].astype(np.float64)/SCALE_FACTOR
    blue = bands["Blue"].astype(np.float64)/SCALE_FACTOR
    return 2.5 * (nir - red) / (nir + 6.0*red - 7.5*blue + 1 + EPS)

def calc_msavi2(bands):
    """MSAVI2 = (2*NIR + 1 - sqrt((2*NIR+1)^2 - 8*(NIR-Red))) / 2"""
    nir = bands["NIR"].astype(np.float64) / SCALE_FACTOR
    red = bands["Red"].astype(np.float64) / SCALE_FACTOR
    term = (2.0 * nir + 1.0) ** 2 - 8.0 * (nir - red)
    term = np.where(term < 0, 0.0, term)
    return (2.0 * nir + 1.0 - np.sqrt(term)) / 2.0

def calc_ndsi(bands):
    """NDSI = (Green - SWIR2) / (Green + SWIR2)"""
    green = bands["Green"].astype(np.float64) / SCALE_FACTOR
    swir2 = bands["SWIR2"].astype(np.float64) / SCALE_FACTOR
    return (green - swir2) / (green + swir2 + EPS)

def calc_ndti(bands):
    """NDTI = (SWIR1 - SWIR2) / (SWIR1 + SWIR2)"""
    swir1 = bands["SWIR1"].astype(np.float64) / SCALE_FACTOR
    swir2 = bands["SWIR2"].astype(np.float64) / SCALE_FACTOR
    return (swir1 - swir2) / (swir1 + swir2 + EPS)

def calc_osavi(bands):
    """OSAVI = (NIR - Red) / (NIR + Red + 0.16)"""
    nir = bands["NIR"].astype(np.float64) / SCALE_FACTOR
    red = bands["Red"].astype(np.float64) / SCALE_FACTOR
    return (nir - red) / (nir + red + 0.16 + EPS)

INDEX_REGISTRY = {
    "NDVI": {"required": ["NIR", "Red"], "func": calc_ndvi},
    "GNDVI": {"required": ["NIR", "Green"], "func": calc_gndvi},
    "NDRE": {"required": ["NIRn", "RE1"], "func": calc_ndre},
    "IRECI": {"required": ["RE3", "Red", "RE1", "RE2"], "func": calc_ireci},
    "SAVI": {"required": ["NIR", "Red"], "func": calc_savi},
    "LSWI": {"required": ["NIR", "SWIR1"], "func": calc_lswi},
    "NDMI": {"required": ["NIR", "SWIR1"], "func": calc_lswi},
    "NDWI": {"required": ["Green", "NIR"], "func": calc_ndwi},
    "MNDWI": {"required": ["Green", "SWIR1"], "func": calc_mndwi},
    "EVI": {"required": ["NIR", "Red", "Blue"], "func": calc_evi},
    "msavi2": {"required": ["NIR", "Red"], "func": calc_msavi2},
    "ndsi": {"required": ["Green", "SWIR2"], "func": calc_ndsi},
    "ndti": {"required": ["SWIR1", "SWIR2"], "func": calc_ndti},
    "osavi": {"required": ["NIR", "Red"], "func": calc_osavi},
}
ALL_INDICES = list(INDEX_REGISTRY.keys())

# ─────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────
def normalize_name(name: str) -> str:
    """去除空格、下划线、连字符，转小写"""
    return str(name).lower().replace(" ", "").replace("_", "").replace("-", "")

def identify_bands(src) -> dict:
    """
    从 rasterio 数据集中识别各逻辑波段对应的波段索引，1-based。
    """
    identified = {}
    descs = list(src.descriptions)
    for band_idx, desc in enumerate(descs, 1):
        if desc is None:
            continue
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
    """
    读取单个波段，返回原始 DN 值。
    处理：nodata → NaN，0 → NaN
    不除以 10000
    """
    data = src.read(band_idx).astype(np.float64)
    if src.nodata is not None:
        data[data == src.nodata] = np.nan
    if ZERO_AS_NODATA:
        data[data <= 0] = np.nan
    return data

def array_to_tiff_bytes(arr: np.ndarray, profile: Dict[str, Any]) -> bytes:
    # 自动拉伸到 0-255，解决前端预览黑/白问题
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
        BIGTIFF="IF_SAFER"
    )
    buf = io.BytesIO()
    with rasterio.open(buf, "w", **out_profile) as dst:
        dst.write(arr, 1)
    return buf.getvalue()


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
        raise RuntimeError(f"{getattr(ctx, 'node_id', '?')}: 未指定输入 key")
    try:
        response = ctx.minio_client.get_object(bucket, key)
        try:
            raw = response.read()
        finally:
            response.close()
            response.release_conn()
        return raw
    except Exception as e:
        raise RuntimeError(f"{getattr(ctx, 'node_id', '?')}: MinIO 读取失败 bucket={bucket} key={key}: {e}")


def run_single_index(
    index_name: str,
    raw_inputs: list,
    ctx: NodeContext,
) -> str:
    """
    单指数统一入口（S2 / Drone 单指数节点共用）
    流程：取输入 bytes → rasterio 开 TIFF → 识别波段 → 计算一个指数 → 归一化写 TIFF → MinIO 上传
    返回上传后的对象 key。
    """
    node_label = f"S2_{index_name}"

    try:
        raw = _get_input_bytes(raw_inputs, ctx)
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"{node_label}: 取输入失败: {e}")

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
                raise RuntimeError(f"{node_label}: TIFF 解析失败: {e}")
            except Exception as e:
                raise RuntimeError(f"{node_label}: 打开影像失败: {e}")

            required = INDEX_REGISTRY[index_name]["required"]
            missing = [r for r in required if r not in bands]
            if missing:
                raise RuntimeError(
                    f"{node_label}: 影像缺少必要波段 {missing}，"
                    f"当前识别到 {list(bands.keys())}"
                )

            try:
                arr = INDEX_REGISTRY[index_name]["func"](bands)
            except Exception as e:
                raise RuntimeError(f"{node_label}: {index_name} 公式计算失败: {e}")

            try:
                tiff_bytes = array_to_tiff_bytes(arr, profile)
                with open(out_path, "wb") as f:
                    f.write(tiff_bytes)
            except Exception as e:
                raise RuntimeError(f"{node_label}: 结果 TIFF 写出失败: {e}")

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
                raise RuntimeError(f"{node_label}: MinIO 上传失败 key={out_key}: {e}")
            final_key = out_key
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    return final_key


def _bytes_to_bytes(index_name: str, raw) -> bytes:
    """
    直接 bytes → bytes（不走 MinIO），供单元测试和 Operator.execute() 使用。
    """
    node_label = f"S2_{index_name}"
    if raw is None:
        raise RuntimeError(f"{node_label}: 未接收到输入文件，请在流水线中连接上游节点或传入影像数据。")
    if not isinstance(raw, (bytes, bytearray)):
        raise RuntimeError(
            f"{node_label}: 输入必须是影像字节流（bytes），"
            f"实际收到的是 {type(raw).__name__}。"
        )
    if len(raw) == 0:
        raise RuntimeError(f"{node_label}: 输入文件为空，请确认已正确上传 Sentinel-2 影像。")
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
                    raise RuntimeError(
                        f"{node_label}: 未在影像中识别到任何 Sentinel-2 波段。"
                        f" 当前共 {total} 个物理波段（格式={fmt}，描述={list(src.descriptions)}），"
                        f"请确认输入是 Sentinel-2 多光谱 TIFF（如 B2/B3/B4/B8/B11…），"
                        f"而不是 RGB/JPEG/PNG 或单波段影像。"
                    )
    except RuntimeError:
        raise
    except rasterio.RasterioIOError as e:
        msg = str(e)
        if "bad header" in msg.lower() or "not a geotiff" in msg.lower():
            raise RuntimeError(
                f"{node_label}: 文件格式无法识别，可能是 JPEG/PNG/普通图片。"
                f"请上传 Sentinel-2 多光谱 TIFF 影像。"
            )
        raise RuntimeError(f"{node_label}: TIFF 解析失败: {e}")
    except Exception as e:
        raise RuntimeError(f"{node_label}: 打开影像失败: {e}")

    required = INDEX_REGISTRY[index_name]["required"]
    missing = [r for r in required if r not in bands]
    if missing:
        raise RuntimeError(
            f"{node_label}: 影像缺少必要波段 {missing}，当前识别到 {list(bands.keys())}。"
            f"请使用包含所有必要波段的 Sentinel-2 多光谱 TIFF。"
        )

    try:
        arr = INDEX_REGISTRY[index_name]["func"](bands)
    except Exception as e:
        raise RuntimeError(f"{node_label}: {index_name} 公式计算失败: {e}")

    return array_to_tiff_bytes(arr, profile)


def make_execute_for_s2(index_name: str):
    """
    返回一个可绑定到 Operator 类的 execute 方法（bytes 输入 → bytes 输出）。
    """
    def execute(self, inputs, ctx):
        if not inputs:
            raise RuntimeError(
                f"S2_{index_name}: 上游没有传输出数据（输入为空列表）。请检查上游节点是否已成功执行，或连接上游。"
            )
        data = inputs[0]
        if isinstance(data, list):
            data = data[0]
        if isinstance(data, dict):
            data = data.get("data", b"")
        if data is None or data == b"":
            raise RuntimeError(
                f"S2_{index_name}: 上游没有传输出数据（输入为空）。请检查上游节点是否已成功执行，或连接上游。"
            )
        return _bytes_to_bytes(index_name, data)
    return execute


# ─────────────────────────────────────────────
# 平台节点主类（多指数批量）
# ─────────────────────────────────────────────
class ImageS2IndicesNode(BaseNode):
    def execute(self, inputs: List[Any], ctx: NodeContext):
        # 读取输入
        try:
            data = inputs[0]
            if isinstance(data, list):
                data = data[0]
            if isinstance(data, dict):
                data = data.get("data", b"")

            # 打开影像
            with rasterio.MemoryFile(data) as mf:
                with mf.open() as src:
                    band_map = identify_bands(src)
                    profile = src.profile

                    # 加载所有识别到的波段
                    bands = {}
                    for name, idx in band_map.items():
                        bands[name] = load_band(src, idx)

            # 计算所有可用指数
            outputs = []
            for name, cfg in INDEX_REGISTRY.items():
                # 检查波段是否齐全
                required = cfg["required"]
                if all(r in bands for r in required):
                    try:
                        arr = cfg["func"](bands)
                        outputs.append(array_to_tiff_bytes(arr, profile))
                    except Exception as e:
                        import logging as _lg
                        _lg.getLogger(__name__).warning("S2 指数 %s 计算跳过: %s", name, e)
                        continue

            # ✅ 安全输出格式，只对自己生效
            return {"multi_files": outputs}
        except RuntimeError:
            raise
        except rasterio.RasterioIOError as e:
            raise RuntimeError(f"S2 多指数: TIFF 解析失败: {e}")
        except Exception as e:
            raise RuntimeError(f"S2 多指数执行失败: {e}")
