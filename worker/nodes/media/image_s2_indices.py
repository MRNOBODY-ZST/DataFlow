from __future__ import annotations
from typing import Dict, Any, List
import io
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
    re3 = bands["RE3"].astype(np.float64)
    red = bands["Red"].astype(np.float64)
    re1 = bands["RE1"].astype(np.float64)
    re2 = bands["RE2"].astype(np.float64)
    return (re3/10000.0 - red/10000.0) / ((re1/10000.0 + EPS) / (re2/10000.0 + EPS) + EPS)

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

# ─────────────────────────────────────────────
# 指数注册表
# ─────────────────────────────────────────────
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

def array_to_tiff_bytes(arr: np.ndarray, profile: Dict[str,Any]) -> bytes:
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


# ─────────────────────────────────────────────
# 平台节点主类
# ─────────────────────────────────────────────
class ImageS2IndicesNode(BaseNode):
    def execute(self, inputs: List[Any], ctx: NodeContext):
        # 读取输入
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
            try:
                # 检查波段是否齐全
                required = cfg["required"]
                if all(r in bands for r in required):
                    arr = cfg["func"](bands)
                    outputs.append(array_to_tiff_bytes(arr, profile))
            except:
                continue

        # ✅ 安全输出格式，只对自己生效
        return {"multi_files": outputs}