#!/usr/bin/env python3
"""Generate node_schemas.json for the DataFlow backend.

Scans nodes/__init__.py NODE_REGISTRY and emits one NodeSchemaDTO per node,
matching NodeSchemaDTO.java (type, label, category, icon, fields[]).

Usage:
    cd worker && python schema_export.py
    -> writes worker/node_schemas.json
    -> backend reads ../worker/node_schemas.json on startup
"""
from __future__ import annotations
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nodes import NODE_REGISTRY

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "node_schemas.json")


def fd(key, label, type_, placeholder=None, required=False, auto_filled=False,
       options=None, widget=None, widget_config=None, inline=False):
    d = {
        "key": key,
        "label": label,
        "type": type_,
        "placeholder": placeholder,
        "required": required,
        "autoFilled": auto_filled,
        "inline": inline,
    }
    if options is not None:
        d["options"] = options
    if widget is not None:
        d["widget"] = widget
    if widget_config is not None:
        d["widgetConfig"] = widget_config
    return d


def wc(key_placeholder, value_placeholder, value_type=None, value_options=None):
    c = {
        "keyPlaceholder": key_placeholder,
        "valuePlaceholder": value_placeholder,
    }
    if value_type is not None:
        c["valueType"] = value_type
    if value_options is not None:
        c["valueOptions"] = value_options
    return c


MEDIA_KEY = fd("key", "源文件 Key（无上游时必填）", "file-picker",
               "input/xxx/image.tif", required=False)


def SPECTRAL(label, widget="PhotoIcon"):
    return {
        "key": {
            "type": "image_s2_indices",
            "label": label,
            "category": "spectral-s2",
            "icon": widget,
            "fields": [
                fd("key", "Sentinel-2 多光谱 TIFF Key", "file-picker",
                   "input/xxx/s2.tif", required=False),
                fd("format", "输出格式", "select", "GTiff", required=False,
                   options=["GTiff", "PNG", "JPEG"]),
            ],
        },
        "drone": {
            "type": "image_drone_index",
            "label": "无人机多光谱指数",
            "category": "spectral-drone",
            "icon": "CameraIcon",
            "fields": [
                fd("key", "无人机多光谱 TIFF Key", "file-picker",
                   "input/xxx/drone.tif", required=False),
                fd("format", "输出格式", "select", "GTiff", required=False,
                   options=["GTiff", "PNG", "JPEG"]),
            ],
        },
    }


S2_COMMON = [
    MEDIA_KEY,
    fd("format", "输出格式", "select", "GTiff", required=False,
       options=["GTiff", "PNG", "JPEG"]),
]
DRONE_COMMON = [
    MEDIA_KEY,
    fd("format", "输出格式", "select", "GTiff", required=False,
       options=["GTiff", "PNG", "JPEG"]),
]


SCHEMA = {
    # ── readers ─────────────────────────────────────
    "csv_reader": {
        "type": "csv_reader", "label": "CSV 读取", "category": "readers", "icon": "DocumentTextIcon",
        "fields": [MEDIA_KEY],
    },
    "json_reader": {
        "type": "json_reader", "label": "JSON 读取", "category": "readers", "icon": "CodeBracketIcon",
        "fields": [MEDIA_KEY],
    },
    "minio_reader": {
        "type": "minio_reader", "label": "MinIO 读取", "category": "readers", "icon": "CloudArrowDownIcon",
        "fields": [
            fd("key", "文件或文件夹路径", "file-picker", "input/xxx/file", required=False),
            fd("bucket", "源 Bucket（默认 dataflow-input）", "text", "dataflow-input", required=False),
            fd("prefix", "对象前缀（递归批量时使用）", "text", "input/", required=False),
            fd("recursive", "递归读取子目录", "checkbox", None, required=False),
            fd("batch", "批量模式（key 为前缀时自动开启）", "checkbox", None, required=False),
        ],
    },

    # ── transforms ───────────────────────────────────
    "filter": {
        "type": "filter", "label": "过滤", "category": "transforms", "icon": "FunnelIcon",
        "fields": [
            fd("query", "Pandas Query 表达式", "text", "age > 18", required=True),
        ],
    },
    "map": {
        "type": "map", "label": "字段映射", "category": "transforms", "icon": "ArrowsRightLeftIcon",
        "fields": [
            fd("rename", "字段重命名", "textarea", '{"old":"new"}', required=False,
               widget="key-value",
               widget_config=wc("原字段名", "新字段名")),
            fd("select", "保留列", "text", '["colA","colB"]', required=False,
               widget="string-array"),
        ],
    },
    "aggregate": {
        "type": "aggregate", "label": "聚合", "category": "transforms", "icon": "ChartBarIcon",
        "fields": [
            fd("group_by", "分组列", "text", '["category"]', required=True,
               widget="string-array"),
            fd("agg", "聚合方法", "textarea", '{"amount":"sum"}', required=True,
               widget="key-value",
               widget_config=wc("字段名", "聚合函数", "select",
                                ["sum", "avg", "min", "max", "count", "first", "last"])),
        ],
    },
    "json_transform": {
        "type": "json_transform", "label": "JSON 转换", "category": "transforms", "icon": "CodeBracketSquareIcon",
        "fields": [
            fd("expression", "JMESPath 表达式", "text", "items[*].name", required=True,
               widget="jmespath"),
        ],
    },
    "json_mapper": {
        "type": "json_mapper", "label": "JSON 可视化映射", "category": "transforms", "icon": "MapIcon",
        "fields": [
            fd("mappings", "字段映射", "text", None, required=False,
               widget="json-mapper"),
            fd("sample", "JSON 样本（用于解析字段树）", "textarea", "{}", required=False),
        ],
    },

    # ── media ───────────────────────────────────────
    "image_resize": {
        "type": "image_resize", "label": "图片缩放", "category": "media", "icon": "PhotoIcon",
        "fields": [
            MEDIA_KEY,
            fd("width", "宽度 (px)", "number", "800", required=False),
            fd("height", "高度 (px)", "number", "600", required=False),
            fd("format", "输出格式", "select", "JPEG", required=False,
               options=["JPEG", "PNG", "WEBP", "BMP"]),
        ],
    },
    "image_ocr": {
        "type": "image_ocr", "label": "图片 OCR", "category": "media", "icon": "LanguageIcon",
        "fields": [
            MEDIA_KEY,
            fd("lang", "语言", "text", '["ch_sim","en"]', required=False,
               widget="string-array"),
            fd("format", "输出格式", "select", "text", required=False,
               options=["text", "json"]),
        ],
    },
    "image_format_convert": {
        "type": "image_format_convert", "label": "图片格式转换", "category": "media", "icon": "ArrowPathIcon",
        "fields": [
            MEDIA_KEY,
            fd("format", "目标格式", "select", "PNG", required=True,
               options=["JPEG", "PNG", "WEBP", "BMP", "TIFF"]),
        ],
    },
    "image_convolution": {
        "type": "image_convolution", "label": "图像卷积", "category": "media", "icon": "AdjustmentsHorizontalIcon",
        "fields": [
            MEDIA_KEY,
            fd("preset", "预设卷积核", "select", "blur", required=False,
               options=["blur", "sharpen", "contour", "detail",
                        "edge_enhance", "emboss", "smooth", "custom"]),
            fd("kernel", "自定义卷积核（3x3 JSON 数组）", "textarea",
               "[0,-1,0,-1,5,-1,0,-1,0]", required=False),
            fd("kernel_size", "卷积核尺寸", "select", "3", required=False,
               options=["3", "5"]),
            fd("offset", "偏移量", "number", "0", required=False),
            fd("format", "输出格式", "select", "JPEG", required=False,
               options=["JPEG", "PNG", "WEBP"]),
        ],
    },
    "image_pooling": {
        "type": "image_pooling", "label": "图像池化", "category": "media", "icon": "Squares2X2Icon",
        "fields": [
            MEDIA_KEY,
            fd("method", "池化方法", "select", "max", required=True,
               options=["max", "avg"]),
            fd("pool_size", "池化窗口大小", "select", "2", required=False,
               options=["2", "3", "4", "8"]),
            fd("stride", "步长（默认等于窗口大小）", "number", "2", required=False),
            fd("format", "输出格式", "select", "JPEG", required=False,
               options=["JPEG", "PNG", "WEBP"]),
        ],
    },
    "image_gaussian_blur": {
        "type": "image_gaussian_blur", "label": "高斯模糊", "category": "media", "icon": "EyeDropperIcon",
        "fields": [
            MEDIA_KEY,
            fd("radius", "模糊半径 (sigma)", "number", "2", required=True),
            fd("format", "输出格式", "select", "JPEG", required=False,
               options=["JPEG", "PNG", "WEBP"]),
        ],
    },
    "image_sharpen": {
        "type": "image_sharpen", "label": "图像锐化", "category": "media", "icon": "SparklesIcon",
        "fields": [
            MEDIA_KEY,
            fd("method", "锐化方法", "select", "unsharp_mask", required=True,
               options=["unsharp_mask", "sharpen_filter", "detail"]),
            fd("radius", "USM 半径", "number", "2", required=False),
            fd("percent", "USM 强度 (%)", "number", "150", required=False),
            fd("threshold", "USM 阈值", "number", "3", required=False),
            fd("factor", "额外锐化因子（1.0=不变）", "number", "1.0", required=False),
            fd("format", "输出格式", "select", "JPEG", required=False,
               options=["JPEG", "PNG", "WEBP"]),
        ],
    },
    "image_edge_detect": {
        "type": "image_edge_detect", "label": "边缘检测", "category": "media", "icon": "ViewfinderCircleIcon",
        "fields": [
            MEDIA_KEY,
            fd("method", "检测方法", "select", "find_edges", required=True,
               options=["find_edges", "sobel", "contour",
                        "edge_enhance", "edge_enhance_more"]),
            fd("format", "输出格式", "select", "PNG", required=False,
               options=["JPEG", "PNG", "WEBP"]),
        ],
    },
    "image_threshold": {
        "type": "image_threshold", "label": "图片二值化", "category": "media", "icon": "SunIcon",
        "fields": [
            MEDIA_KEY,
            fd("method", "阈值方法", "select", "binary", required=True,
               options=["binary", "binary_inv", "truncate", "to_zero", "otsu"]),
            fd("threshold", "阈值 0-255（Otsu 时自动）", "number", "128", required=False),
            fd("format", "输出格式", "select", "PNG", required=False,
               options=["JPEG", "PNG", "WEBP"]),
        ],
    },

    "video_extract": {
        "type": "video_extract", "label": "视频抽帧", "category": "media", "icon": "FilmIcon",
        "fields": [
            MEDIA_KEY,
            fd("fps", "抽帧率 (FPS)", "number", "1", required=False),
            fd("output_prefix", "输出前缀（MinIO 下的子路径）", "text",
               "frames/task1/", required=False),
            fd("format", "图片格式", "select", "JPEG", required=False,
               options=["JPEG", "PNG"]),
        ],
    },
    "video_transcode": {
        "type": "video_transcode", "label": "视频转码", "category": "media", "icon": "VideoCameraIcon",
        "fields": [
            MEDIA_KEY,
            fd("codec", "编码格式", "select", "h264", required=True,
               options=["h264", "h265", "vp9"]),
            fd("bitrate", "码率 (kbps)", "number", "2000", required=False),
        ],
    },
    "audio_extract": {
        "type": "audio_extract", "label": "音频提取", "category": "media", "icon": "MusicalNoteIcon",
        "fields": [
            MEDIA_KEY,
            fd("format", "音频格式", "select", "mp3", required=True,
               options=["mp3", "aac", "wav", "flac", "m4a"]),
            fd("bitrate", "码率 (kbps)", "number", "128", required=False),
        ],
    },

    # ── 旧通用入口（保留兼容） ────────────────────────
    "image_s2_indices": {
        "type": "image_s2_indices", "label": "S2 通用多光谱指数",
        "category": "spectral-s2", "icon": "GlobeEuropeAfricaIcon",
        "fields": S2_COMMON,
    },
    "image_drone_index": {
        "type": "image_drone_index", "label": "无人机通用多光谱指数",
        "category": "spectral-drone", "icon": "CameraIcon",
        "fields": DRONE_COMMON,
    },

    # ── Sentinel-2 单指数 ────────────────────────────
    "image_s2_ndvi":    {"type": "image_s2_ndvi",    "label": "NDVI（植被指数）",       "category": "spectral-s2", "icon": "LeafIcon",      "fields": S2_COMMON},
    "image_s2_gndvi":   {"type": "image_s2_gndvi",   "label": "GNDVI（绿色 NDVI）",    "category": "spectral-s2", "icon": "LeafIcon",      "fields": S2_COMMON},
    "image_s2_ndre":    {"type": "image_s2_ndre",    "label": "NDRE（红边植被指数）",   "category": "spectral-s2", "icon": "LeafIcon",      "fields": S2_COMMON},
    "image_s2_ireci":   {"type": "image_s2_ireci",   "label": "IRECI（反演红边指数）",  "category": "spectral-s2", "icon": "LeafIcon",      "fields": S2_COMMON},
    "image_s2_savi":    {"type": "image_s2_savi",    "label": "SAVI（土壤调节植被指数）","category": "spectral-s2", "icon": "LeafIcon",      "fields": S2_COMMON},
    "image_s2_msavi2":  {"type": "image_s2_msavi2",  "label": "MSAVI2（修改 SAVI）",    "category": "spectral-s2", "icon": "LeafIcon",      "fields": S2_COMMON},
    "image_s2_osavi":   {"type": "image_s2_osavi",   "label": "OSAVI（优化 SAVI）",     "category": "spectral-s2", "icon": "LeafIcon",      "fields": S2_COMMON},
    "image_s2_lswi":    {"type": "image_s2_lswi",    "label": "LSWI（地表水指数）",      "category": "spectral-s2", "icon": "DropletIcon",   "fields": S2_COMMON},
    "image_s2_ndwi":    {"type": "image_s2_ndwi",    "label": "NDWI（归一化水指数）",    "category": "spectral-s2", "icon": "DropletIcon",   "fields": S2_COMMON},
    "image_s2_mndwi":   {"type": "image_s2_mndwi",   "label": "MNDWI（改进 NDWI）",     "category": "spectral-s2", "icon": "DropletIcon",   "fields": S2_COMMON},
    "image_s2_ndmi":    {"type": "image_s2_ndmi",    "label": "NDMI（归一化湿度指数）",  "category": "spectral-s2", "icon": "DropletIcon",   "fields": S2_COMMON},
    "image_s2_evi":     {"type": "image_s2_evi",     "label": "EVI（增强植被指数）",     "category": "spectral-s2", "icon": "LeafIcon",      "fields": S2_COMMON},
    "image_s2_ndsi":    {"type": "image_s2_ndsi",    "label": "NDSI（归一化差异雪指数）","category": "spectral-s2", "icon": "SnowflakeIcon", "fields": S2_COMMON},
    "image_s2_ndti":    {"type": "image_s2_ndti",    "label": "NDTI（归一化差异温度指数）","category": "spectral-s2","icon": "ThermometerIcon","fields": S2_COMMON},

    # ── Drone 单指数 ──────────────────────────────────
    "image_drone_ndvi":     {"type": "image_drone_ndvi",     "label": "Drone NDVI",     "category": "spectral-drone", "icon": "CameraIcon", "fields": DRONE_COMMON},
    "image_drone_gndvi":    {"type": "image_drone_gndvi",    "label": "Drone GNDVI",    "category": "spectral-drone", "icon": "CameraIcon", "fields": DRONE_COMMON},
    "image_drone_ndre":     {"type": "image_drone_ndre",     "label": "Drone NDRE",     "category": "spectral-drone", "icon": "CameraIcon", "fields": DRONE_COMMON},
    "image_drone_savi":     {"type": "image_drone_savi",     "label": "Drone SAVI",     "category": "spectral-drone", "icon": "CameraIcon", "fields": DRONE_COMMON},
    "image_drone_msavi":    {"type": "image_drone_msavi",    "label": "Drone MSAVI",    "category": "spectral-drone", "icon": "CameraIcon", "fields": DRONE_COMMON},
    "image_drone_rvi":      {"type": "image_drone_rvi",      "label": "Drone RVI",      "category": "spectral-drone", "icon": "CameraIcon", "fields": DRONE_COMMON},
    "image_drone_ngrdi":    {"type": "image_drone_ngrdi",    "label": "Drone NGRDI",    "category": "spectral-drone", "icon": "CameraIcon", "fields": DRONE_COMMON},
    "image_drone_gci":      {"type": "image_drone_gci",      "label": "Drone GCI",      "category": "spectral-drone", "icon": "CameraIcon", "fields": DRONE_COMMON},
    "image_drone_lci":      {"type": "image_drone_lci",      "label": "Drone LCI",      "category": "spectral-drone", "icon": "CameraIcon", "fields": DRONE_COMMON},
    "image_drone_sipi2":    {"type": "image_drone_sipi2",    "label": "Drone SIPI2",    "category": "spectral-drone", "icon": "CameraIcon", "fields": DRONE_COMMON},
    "image_drone_dvi":      {"type": "image_drone_dvi",      "label": "Drone DVI",      "category": "spectral-drone", "icon": "CameraIcon", "fields": DRONE_COMMON},
    "image_drone_ciredge": {"type": "image_drone_ciredge", "label": "Drone CI RedEdge", "category": "spectral-drone", "icon": "CameraIcon", "fields": DRONE_COMMON},
    "image_drone_cirededge":{"type": "image_drone_cirededge","label": "Drone CIREdge",  "category": "spectral-drone", "icon": "CameraIcon", "fields": DRONE_COMMON},

    # ── utils ─────────────────────────────────────────
    "preview": {
        "type": "preview", "label": "预览", "category": "utils", "icon": "EyeIcon",
        "fields": [
            fd("label", "自定义文件名", "text", "留空则使用原文件名",
               required=False),
        ],
    },

    # ── writers ───────────────────────────────────────
    "minio_writer": {
        "type": "minio_writer", "label": "MinIO 写出", "category": "writers", "icon": "CloudArrowUpIcon",
        "fields": [
            fd("key", "输出 Key（可留空使用自动命名）", "text",
               "output/result", required=False),
            fd("bucket", "目标 Bucket（默认 dataflow-output）", "text",
               "dataflow-output", required=False),
        ],
    },
    "csv_writer": {
        "type": "csv_writer", "label": "CSV 写出", "category": "writers", "icon": "TableCellsIcon",
        "fields": [
            fd("key", "输出 Key", "text", "output/result.csv", required=False),
            fd("bucket", "目标 Bucket（默认 dataflow-output）", "text",
               "dataflow-output", required=False),
        ],
    },
    "json_writer": {
        "type": "json_writer", "label": "JSON 写出", "category": "writers", "icon": "CodeBracketIcon",
        "fields": [
            fd("key", "输出 Key", "text", "output/result.json", required=False),
            fd("bucket", "目标 Bucket（默认 dataflow-output）", "text",
               "dataflow-output", required=False),
            fd("indent", "缩进空格数", "number", "2", required=False),
            fd("ensure_ascii", "转义非 ASCII 字符", "checkbox",
               None, required=False),
        ],
    },
}


def main():
    exported = []
    missing = []
    for node_type, cls in NODE_REGISTRY.items():
        if node_type not in SCHEMA:
            missing.append(node_type)
            continue
        s = SCHEMA[node_type]
        entry = {
            "type": s["type"],
            "label": s["label"],
            "category": s["category"],
            "icon": s["icon"],
            "fields": s["fields"],
        }
        exported.append(entry)

    if missing:
        print(f"[WARN] {len(missing)} nodes in NODE_REGISTRY but not in SCHEMA:")
        for m in missing:
            print(f"  - {m}")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(exported, f, ensure_ascii=False, indent=2)

    print(f"[OK] Wrote {len(exported)} node schemas -> {OUTPUT}")
    from collections import Counter
    cats = Counter(e["category"] for e in exported)
    for cat, n in sorted(cats.items()):
        print(f"  {cat}: {n}")


if __name__ == "__main__":
    main()
