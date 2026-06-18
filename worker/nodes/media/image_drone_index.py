from __future__ import annotations
from typing import Dict, Any, List
import io
import numpy as np
import rasterio
from nodes.base import BaseNode, NodeContext

"""
输入波段：
1. Green    绿光波段
2. Red      红光波段
3. RedEdge  红边波段
4. NIR      近红外波段

计算的植被指数包括：

1. NDVI
   Normalized Difference Vegetation Index
   归一化植被指数
   NDVI = (NIR - Red) / (NIR + Red)

2. GNDVI
   Green Normalized Difference Vegetation Index
   绿光归一化植被指数
   GNDVI = (NIR - Green) / (NIR + Green)

3. NDRE
   Normalized Difference Red Edge Index
   归一化红边指数
   NDRE = (NIR - RedEdge) / (NIR + RedEdge)

4. LCI
   Leaf Chlorophyll Index
   叶绿素指数
   LCI = (NIR - RedEdge) / (NIR + Red)

5. SIPI2
   Structure Insensitive Pigment Index 2
   结构不敏感色素指数
   SIPI2 = (NIR - Green) / (NIR - Red)

6. GCI / CIgreen
   Green Chlorophyll Index
   绿光叶绿素指数
   GCI = NIR / Green - 1

7. CIredEdge
   Red-edge Chlorophyll Index
   红边叶绿素指数
   CIredEdge = NIR / RedEdge - 1

8. NGRDI
   Normalized Green Red Difference Index
   归一化绿红差异指数
   NGRDI = (Green - Red) / (Green + Red)

9. RVI
   Ratio Vegetation Index
   比值植被指数
   RVI = NIR / Red

10. DVI
    Difference Vegetation Index
    差值植被指数
    DVI = NIR - Red

11. SAVI
    Soil Adjusted Vegetation Index
    土壤调节植被指数
    SAVI = ((NIR - Red) * (1 + L)) / (NIR + Red + L) 
     L = 0.5

12. MSAVI
    Modified Soil Adjusted Vegetation Index
    修正型土壤调节植被指数
    MSAVI = [2 * NIR + 1 - sqrt((2 * NIR + 1)^2 - 8 * (NIR - Red))] / 2

说明：
- 输出结果为 float32 类型的单波段 GeoTIFF。
- 输出文件会保存到脚本所在目录。
- SAVI 和 MSAVI 中的 可以暂时不用
"""
def safe_divide(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    out = np.full_like(numerator, np.nan, dtype=np.float32)
    valid = (
        np.isfinite(numerator)
        & np.isfinite(denominator)
        & (np.abs(denominator) > 1e-8)
    )
    out[valid] = numerator[valid] / denominator[valid]
    return out


def calc_indices(bands: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    nir = bands["NIR"]
    red = bands["Red"]
    green = bands["Green"]
    red_edge = bands["RedEdge"]

    savi_l = 0.5

    # MSAVI 中根号内的部分
    msavi_term = (2.0 * nir + 1.0) ** 2 - 8.0 * (nir - red)
    msavi_term = np.where(msavi_term < 0, 0, msavi_term)

    indices: Dict[str, np.ndarray] = {
        # NDVI = (NIR - Red) / (NIR + Red)
        "NDVI": safe_divide(nir - red, nir + red),

        # GNDVI = (NIR - Green) / (NIR + Green)
        "GNDVI": safe_divide(nir - green, nir + green),

        # NDRE = (NIR - RedEdge) / (NIR + RedEdge)
        "NDRE": safe_divide(nir - red_edge, nir + red_edge),

        # LCI = (NIR - RedEdge) / (NIR + Red)
        "LCI": safe_divide(nir - red_edge, nir + red),

        # SIPI2 = (NIR - Green) / (NIR - Red)
        "SIPI2": safe_divide(nir - green, nir - red),

        # GCI / CIgreen = NIR / Green - 1
        "GCI": safe_divide(nir, green) - 1.0,

        # CIredEdge = NIR / RedEdge - 1
        "CIredEdge": safe_divide(nir, red_edge) - 1.0,

        # NGRDI = (Green - Red) / (Green + Red)
        "NGRDI": safe_divide(green - red, green + red),

        # RVI = NIR / Red
        "RVI": safe_divide(nir, red),

        # DVI = NIR - Red
        "DVI": (nir - red).astype(np.float32),

        # SAVI = ((NIR - Red) * (1 + L)) / (NIR + Red + L)
        "SAVI": safe_divide(
            (nir - red) * (1.0 + savi_l),
            nir + red + savi_l,
        ),

        # MSAVI = [2NIR + 1 - sqrt((2NIR + 1)^2 - 8(NIR - Red))] / 2
        "MSAVI": (
            (2.0 * nir + 1.0 - np.sqrt(msavi_term)) / 2.0
        ).astype(np.float32),
    }

    return indices


def array_to_tiff_bytes(arr: np.ndarray, profile: Dict[str, Any]) -> bytes:
    out_profile = profile.copy()
    out_profile.update(
        dtype="float32",
        count=1,
        nodata=np.nan,
        compress="lzw"
    )
    buf = io.BytesIO()
    with rasterio.open(buf, "w", **out_profile) as dst:
        dst.write(arr.astype(np.float32), 1)
    return buf.getvalue()


def read_bytes_to_array(data: bytes) -> tuple[np.ndarray, dict]:
    with rasterio.MemoryFile(data) as mf:
        with mf.open() as ds:
            arr = ds.read(1).astype(np.float32)
            prof = ds.profile.copy()
    return arr, prof


class ImageDroneIndexNode(BaseNode):
    def execute(self, inputs: List[Any], ctx: NodeContext):
        try:
            data = inputs[0]
            if isinstance(data, list):
                data = data[0]
            if isinstance(data, dict):
                data = data.get("data", b"")

            arr, profile = read_bytes_to_array(data)
            bands = {"Green": arr, "Red": arr, "RedEdge": arr, "NIR": arr}
            indices = calc_indices(bands)

            # 输出安全格式
            outputs = [array_to_tiff_bytes(a, profile) for a in indices.values()]
            return {"multi_files": outputs}
        except RuntimeError:
            raise
        except rasterio.RasterioIOError as e:
            raise RuntimeError(f"Drone 多指数: TIFF 解析失败: {e}")
        except Exception as e:
            raise RuntimeError(f"Drone 多指数执行失败: {e}")