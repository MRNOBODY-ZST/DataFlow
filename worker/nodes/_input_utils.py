"""Shared input/config validation helpers used by media/*, readers/*, writers/*, transforms/*.

These helpers give *friendly* Chinese error messages (with node name in Chinese)
PLUS possible reasons and suggested fixes, instead of letting a low-level
IndexError/TypeError bubble up to the user.
"""

from __future__ import annotations


_NODE_NAME_CN = {
    "image_convolution": "图像卷积",
    "image_edge_detect": "图像边缘检测",
    "image_format_convert": "图像格式转换",
    "image_gaussian_blur": "图像高斯模糊",
    "image_ocr": "图像OCR",
    "image_pooling": "图像池化",
    "image_resize": "图像缩放",
    "image_sharpen": "图像锐化",
    "image_threshold": "图像阈值",
    "image_drone_index": "无人机多指数",
    "image_s2_indices": "哨兵2多指数",
    "video_extract": "视频抽帧",
    "video_transcode": "视频转码",
    "audio_extract": "音频抽取",
    "csv_reader": "CSV读取",
    "json_reader": "JSON读取",
    "minio_reader": "MinIO读取",
    "csv_writer": "CSV写入",
    "json_writer": "JSON写入",
    "minio_writer": "MinIO写入",
    "aggregate_node": "聚合",
    "filter_node": "过滤",
    "json_mapper": "JSON映射",
    "json_transform": "JSON转换",
    "map_node": "字段映射",
    "preview_node": "预览",
    "image_s2_ndvi":  "哨兵2 NDVI",
    "image_s2_gndvi": "哨兵2 GNDVI",
    "image_s2_ndre":  "哨兵2 NDRE",
    "image_s2_ireci": "哨兵2 IRECI",
    "image_s2_savi":  "哨兵2 SAVI",
    "image_s2_msavi2":"哨兵2 MSAVI2",
    "image_s2_osavi": "哨兵2 OSAVI",
    "image_s2_lswi":  "哨兵2 LSWI",
    "image_s2_ndwi":  "哨兵2 NDWI",
    "image_s2_mndwi": "哨兵2 MNDWI",
    "image_s2_ndmi":  "哨兵2 NDMI",
    "image_s2_evi":   "哨兵2 EVI",
    "image_s2_ndsi":  "哨兵2 NDSI",
    "image_s2_ndti":  "哨兵2 NDTI",
    "image_drone_ndvi":     "无人机 NDVI",
    "image_drone_gndvi":    "无人机 GNDVI",
    "image_drone_ndre":     "无人机 NDRE",
    "image_drone_savi":     "无人机 SAVI",
    "image_drone_msavi":    "无人机 MSAVI",
    "image_drone_rvi":      "无人机 RVI",
    "image_drone_ngrdi":    "无人机 NGRDI",
    "image_drone_gci":      "无人机 GCI",
    "image_drone_lci":      "无人机 LCI",
    "image_drone_sipi2":    "无人机 SIPI2",
    "image_drone_dvi":      "无人机 DVI",
    "image_drone_ciredge": "无人机 CI RedEdge",
    "image_drone_cirededge":"无人机 CIREdge",
}


def _cn(label: str) -> str:
    return _NODE_NAME_CN.get(label, label)


def _emit(label: str, reason: str, fix: str, detail: str | None = None) -> RuntimeError:
    node_cn = _cn(label)
    msg = f"{node_cn}: {reason}"
    if detail:
        msg += f"（{detail}）"
    msg += f"\n可能原因：{reason}\n解决方法：{fix}"
    raise RuntimeError(msg)


def err_no_upstream(label: str, detail: str = "") -> RuntimeError:
    _emit(
        label,
        "未接收到任何上游数据",
        "请将本节点连接到上游节点（如 CSV读取、图像格式转换等），或在节点配置中手动设置输入文件 key。",
        detail or None,
    )


def err_bad_input_type(label: str, got_type: str, expected: str) -> RuntimeError:
    _emit(
        label,
        f"输入数据类型不正确，实际收到 {got_type}",
        f"请确认上游节点的输出是否为【{expected}】，或在流水线中加入数据转换节点。",
    )


def err_empty_bytes(label: str) -> RuntimeError:
    _emit(
        label,
        "输入文件为空（0 字节）",
        "请确认文件已正确上传到 MinIO，或检查上游节点是否输出了有效数据。",
    )


def err_minio_not_found(label: str, key: str, bucket: str) -> RuntimeError:
    _emit(
        label,
        f"MinIO 中找不到文件 key='{key}'（bucket='{bucket}'）",
        "请检查：① 文件名/路径拼写是否正确；② 文件是否已上传到对应的 bucket；③ 是否需要加上目录前缀如 'input/'。",
    )


def err_minio_missing_key(label: str) -> RuntimeError:
    _emit(
        label,
        "既没有收到上游数据，也没有配置输入 key",
        "请将本节点连接到上游输出节点，或在节点配置里设置 key='input/xxx.tif'（也支持 prefix= 读取整个前缀）。",
    )


def err_media_not_image(label: str, size_hint: str = "") -> RuntimeError:
    _emit(
        label,
        "无法解析为有效的图片字节流",
        "请确认上传的文件是 JPEG/PNG/TIFF 等标准图片格式，而不是 txt/json/csv 文件。",
        size_hint or None,
    )


def err_s2_no_bands(label: str, n_bands: int, sample: str) -> RuntimeError:
    _emit(
        label,
        f"未识别到任何 Sentinel-2 波段（共 {n_bands} 个物理波段）",
        "请上传真正的 Sentinel-2 多光谱 TIFF（包含 B2/B3/B4/B8/B11 等多波段），不要传 RGB/JPEG/PNG/单波段影像。",
        sample,
    )


def err_s2_missing(label: str, missing_bands: str, has: str) -> RuntimeError:
    _emit(
        label,
        f"影像缺少必要波段 [{missing_bands}]，当前识别到 [{has}]",
        "请使用包含所有计算所需波段的 Sentinel-2 影像（建议使用官方 ESA/USGS 出口的 L2A 产品）。",
    )


def err_drone_no_bands(label: str, n_bands: int, sample: str) -> RuntimeError:
    _emit(
        label,
        f"未识别到任何无人机多光谱波段（共 {n_bands} 个物理波段）",
        "请上传真正的无人机多光谱 TIFF（通常包含 G/R/NIR/RE 等 4~6 个波段），不要传普通手机拍的 RGB 图片。",
        sample,
    )


def err_fps_invalid(label: str, val) -> RuntimeError:
    _emit(
        label,
        f"fps 必须大于 0，当前配置 {val}",
        "请把节点配置里的 fps 改成正整数，例如 1、2、5。",
    )


def err_ffmpeg_missing(label: str, hint: str = "") -> RuntimeError:
    _emit(
        label,
        f"系统找不到 FFmpeg 可执行程序",
        "请安装 FFmpeg 并加入 PATH（Windows: 下载 gpl build 的 ffmpeg.exe 放到 C:\\Windows\\System32 或项目目录）。",
        hint or None,
    )


def err_ffmpeg_encoder_missing(label: str, need: str) -> RuntimeError:
    _emit(
        label,
        f"FFmpeg 缺少 {need} 编码器",
        "请安装带完整 GPL 版的 FFmpeg（Windows 推荐 ffmpeg-win64-gpl），或把输出格式改成 H.264。",
    )


def err_filter_syntax(label: str, query: str, hint: str) -> RuntimeError:
    _emit(
        label,
        f"过滤表达式执行失败 query='{query}'",
        "请检查 Pandas Query 语法：字段名不能含空格、字符串需单引号、逻辑用 and/or。例如 age > 18 and city == '北京'。",
        hint,
    )


def err_agg_field_missing(label: str, missing: str, cols: str) -> RuntimeError:
    _emit(
        label,
        f"分组或聚合字段 '{missing}' 在数据中不存在",
        f"请在节点配置里把字段名改成实际存在的列名。当前数据列：[{cols}]",
    )


def err_jmespath_syntax(label: str, expr: str) -> RuntimeError:
    _emit(
        label,
        f"JMESPath 表达式解析失败 expression='{expr}'",
        "请用 [JMESPath 在线校验器](https://jmespath.org/) 验证表达式，注意数组用 [*]、字段用 .key、不要漏引号。",
    )


def err_json_malformed(label: str, hint: str = "") -> RuntimeError:
    _emit(
        label,
        "输入不是合法 JSON",
        "请检查是否上传了完整的 JSON 字符串（成对 {} [] ''，没有注释），或确认上游 JSON 读取节点是否成功。",
        hint,
    )


def err_math(label: str, what: str, hint: str) -> RuntimeError:
    _emit(
        label,
        f"{what} 公式计算失败",
        "可能是数据中有负数或 NaN 导致非法数学运算（如对负数开平方、除以 0）。请确认影像是否完整覆盖计算范围。",
        hint,
    )


def err_tiff_write(label: str, hint: str) -> RuntimeError:
    _emit(
        label,
        "结果 TIFF 写出失败",
        "请检查磁盘空间与写入权限，或更换输出路径/key。",
        hint,
    )


def err_minio_upload(label: str, key: str, hint: str) -> RuntimeError:
    _emit(
        label,
        f"结果上传 MinIO 失败 key='{key}'",
        "请检查：① MinIO 服务是否在运行；② bucket 是否存在；③ 凭据 AK/SK 是否正确；④ 文件名中有没有非法字符。",
        hint,
    )


def err_tiff_open(label: str, hint: str) -> RuntimeError:
    _emit(
        label,
        "无法打开为 TIFF 文件",
        "请确认上传的文件确实是 GeoTIFF 格式（扩展名 .tif/.tiff，包含地理坐标），不要传 PNG/JPEG。",
        hint,
    )


def err_generic(label: str, hint: str) -> RuntimeError:
    _emit(
        label,
        f"执行失败",
        "请把上述错误信息、节点类型、使用的数据文件一起发给运维同学排查。",
        hint,
    )


def err_ocr_no_tesseract(label: str, hint: str = "") -> RuntimeError:
    _emit(
        label,
        "系统找不到 Tesseract OCR 引擎",
        "请安装 Tesseract（Windows: 下载 UB-Mannheim 版 tesseract-ocr-w64-setup.exe），并把安装目录加入 PATH。",
        hint or None,
    )


def err_ocr_fail(label: str, hint: str) -> RuntimeError:
    _emit(
        label,
        "OCR 识别失败",
        "请确认上传的是包含清晰文字的图片，文字方向正确、对比度足够，必要时先在前端图片缩放/锐化/二值化后再 OCR。",
        hint,
    )


def get_first_input(inputs, node_label: str):
    """
    Return the first upstream value, or None if no upstream data (MinIO fallback path).

    Accepts:
      - inputs is a list -> inputs[0] if non-empty
      - inputs is a dict with "data" -> inputs["data"]
      - inputs is bytes/str/etc -> return as-is (single-value path)
      - inputs is None / empty / falsy -> return None (caller should try MinIO)
      - first value is dict with "data" -> unwrap (batch-item convention)
    """
    if inputs is None:
        return None
    if isinstance(inputs, list):
        if len(inputs) == 0:
            return None
        value = inputs[0]
    elif isinstance(inputs, tuple):
        if len(inputs) == 0:
            return None
        value = inputs[0]
    elif isinstance(inputs, dict) and "data" in inputs:
        value = inputs["data"]
    else:
        value = inputs

    if isinstance(value, dict) and "data" in value:
        value = value["data"]
    return value


def resolve_media_bytes(inputs, ctx, node_label: str, allow_minio_fallback=True):
    """
    Resolve raw bytes for a media operator.

    Priority:
      1) inputs[0] (direct bytes from upstream)
      2) ctx.config["key"] -> read from MinIO
    """
    raw = get_first_input(inputs, node_label)

    if raw is None:
        if allow_minio_fallback:
            key = ctx.config.get("key") or ctx.config.get("input_key")
            if not key:
                err_minio_missing_key(node_label)
            try:
                response = ctx.minio_client.get_object(ctx.input_bucket, key)
                try:
                    raw = response.read()
                finally:
                    response.close()
                    response.release_conn()
            except Exception as e:
                err_minio_not_found(node_label, key, ctx.input_bucket or "dataflow-input")
        else:
            err_no_upstream(node_label)

    if not isinstance(raw, (bytes, bytearray)):
        err_bad_input_type(node_label, type(raw).__name__, "图片/视频字节流 bytes")
    if len(raw) == 0:
        err_empty_bytes(node_label)
    return raw


def friendly(label: str, detail: str) -> RuntimeError:
    """Generic helper for unknown backend error, still gives node name in Chinese."""
    err_generic(label, detail)