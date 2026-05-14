import io
import pathlib
from nodes.base import BaseNode, NodeContext


FORMAT_MAP = {
    b"\xff\xd8\xff": (".jpg", "image/jpeg"),
    b"\x89PNG\r\n\x1a\n": (".png", "image/png"),
    b"RIFF": (".webp", "image/webp"),
    b"BM": (".bmp", "image/bmp"),
    b"GIF8": (".gif", "image/gif"),
    b"II\x2a\x00": (".tiff", "image/tiff"),
    b"MM\x00\x2a": (".tiff", "image/tiff"),
}


def _detect(data: bytes) -> tuple[str, str]:
    for sig, (ext, ct) in FORMAT_MAP.items():
        if data[: len(sig)] == sig:
            return ext, ct
    return "", "application/octet-stream"


class PreviewNode(BaseNode):

    def execute(self, inputs: list, ctx: NodeContext):
        import json
        import pandas as pd

        data = inputs[0] if inputs else None
        if data is None:
            return data

        prefix = f"run_{ctx.task_id}/{ctx.node_id}"

        custom_label = ctx.config.get("label", "").strip()
        if custom_label:
            file_path = custom_label
        elif ctx.source_key:
            file_path = ctx.source_key
        else:
            file_path = "preview"

        name = pathlib.PurePosixPath(file_path).name
        has_ext = "." in name

        if isinstance(data, (bytes, bytearray)):
            raw = bytes(data)
            ext, content_type = _detect(raw)
            if not has_ext:
                file_path += ext
        elif isinstance(data, pd.DataFrame):
            raw = data.to_csv(index=False).encode()
            content_type = "text/csv"
            if not has_ext:
                file_path += ".csv"
        elif isinstance(data, str):
            raw = data.encode()
            content_type = "text/plain"
            if not has_ext:
                file_path += ".txt"
        elif isinstance(data, (list, dict)):
            raw = json.dumps(data, ensure_ascii=False, indent=2).encode()
            content_type = "application/json"
            if not has_ext:
                file_path += ".json"
        else:
            return data

        key = f"{prefix}/{file_path}"
        ctx.minio_client.put_object(
            ctx.temp_bucket,
            key,
            io.BytesIO(raw),
            length=len(raw),
            content_type=content_type,
        )

        return data
