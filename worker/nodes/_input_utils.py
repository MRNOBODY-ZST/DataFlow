"""Shared input/config validation helpers used by media/*, readers/*, writers/*, transforms/*.

These helpers give *friendly* Chinese error messages (with node name in Chinese)
instead of letting a low-level IndexError/TypeError bubble up to the user.
"""


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
    "minio_writer": "MinIO写入",
    "aggregate_node": "聚合",
    "filter_node": "过滤",
    "json_mapper": "JSON映射",
    "json_transform": "JSON转换",
    "map_node": "字段映射",
    "preview_node": "预览",
}


def _cn(label: str) -> str:
    return _NODE_NAME_CN.get(label, label)


def friendly(label: str, detail: str) -> RuntimeError:
    """Build a Chinese-friendly RuntimeError with node name and detail."""
    raise RuntimeError(f"{_cn(label)}: {detail}")


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
      2) ctx.config["key"] → read from MinIO
    """
    raw = get_first_input(inputs, node_label)

    if raw is None:
        if allow_minio_fallback:
            key = ctx.config.get("key") or ctx.config.get("input_key")
            if not key:
                raise RuntimeError(
                    f"{_cn(node_label)}: 既没有收到上游图像，也没有配置 MinIO key。"
                    f"请将本节点连接到上游（图像/视频节点的输出会自动传递），"
                    f"或在节点配置中设置 key / input_key。"
                )
            response = ctx.minio_client.get_object(ctx.input_bucket, key)
            try:
                raw = response.read()
            finally:
                response.close()
                response.release_conn()
        else:
            raise RuntimeError(
                f"{_cn(node_label)}: 未接收到输入数据。"
                f"请在流水线中连接上游节点，或提供正确的输入。"
            )

    if not isinstance(raw, (bytes, bytearray)):
        raise RuntimeError(
            f"{_cn(node_label)}: 输入必须是字节流（bytes），实际收到的是"
            f"{type(raw).__name__}。请确认上游节点是否正确传递了图像/视频数据。"
        )
    if len(raw) == 0:
        raise RuntimeError(f"{_cn(node_label)}: 输入数据为空（0 字节），请确认文件已正确上传。")
    return raw
