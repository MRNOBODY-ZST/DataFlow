import io
import json
import pandas as pd
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import (
    err_no_upstream,
    err_bad_input_type,
    err_minio_upload,
    err_generic,
)


class MinioWriterNode(BaseNode):

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            if not inputs:
                err_no_upstream("minio_writer")
            data = inputs[0]

            if isinstance(data, dict) and data.get("multi_files"):
                files = data["multi_files"]
                key = ctx.config.get("key") or ctx.source_filename or "multi"
                for idx, raw in enumerate(files):
                    obj_key = f"{key}_{idx}.jpg"
                    try:
                        ctx.minio_client.put_object(
                            ctx.output_bucket,
                            obj_key,
                            io.BytesIO(raw),
                            length=len(raw),
                            content_type="image/jpeg",
                        )
                    except Exception as e:
                        err_minio_upload("minio_writer", obj_key, f"{e}")
                return key

            fmt = ctx.config.get("format") or ctx.config.get("fmt")
            if fmt is None:
                if isinstance(data, pd.DataFrame):
                    fmt = "csv"
                elif isinstance(data, bytes):
                    ctx.config.setdefault("_auto_key_ext", ".bin")
                    key_lower = (ctx.config.get("key", ctx.source_filename) or "").lower()
                    if key_lower.endswith(".jpg") or key_lower.endswith(".jpeg"):
                        fmt = "bytes_image"
                    elif key_lower.endswith(".png"):
                        fmt = "bytes_png"
                    else:
                        fmt = "bytes"
                elif isinstance(data, str):
                    fmt = "txt"
                elif isinstance(data, (dict, list)):
                    fmt = "json"
                else:
                    fmt = "csv"

            key = ctx.config.get("key") or ctx.source_filename

            if fmt == "csv":
                if not isinstance(data, pd.DataFrame):
                    err_bad_input_type("minio_writer", type(data).__name__, "pandas DataFrame")
                if key and not key.lower().endswith(".csv"):
                    key = key + ".csv"
                key = ctx.output_key(key or "result.csv")
                raw = data.to_csv(index=False).encode()
                ct = "text/csv"
            elif fmt in ("bytes_image", "bytes", "jpeg", "jpg", "image/jpeg"):
                if isinstance(data, str):
                    data = data.encode()
                else:
                    raw = bytes(data)
                if key and not (key.lower().endswith(".jpg") or key.lower().endswith(".jpeg")):
                    key = key + ".jpg"
                key = ctx.output_key(key or "result.jpg")
                raw = data if isinstance(data, (bytes, bytearray)) else bytes(data)
                ct = "image/jpeg"
            elif fmt in ("bytes_png", "png", "image/png"):
                if key and not key.lower().endswith(".png"):
                    key = key + ".png"
                key = ctx.output_key(key or "result.png")
                raw = data if isinstance(data, (bytes, bytearray)) else bytes(data)
                ct = "image/png"
            elif fmt == "txt":
                if isinstance(data, bytes):
                    raw = data
                else:
                    raw = str(data).encode()
                if key and not key.lower().endswith(".txt"):
                    key = key + ".txt"
                key = ctx.output_key(key or "result.txt")
                ct = "text/plain"
            elif fmt == "json":
                if isinstance(data, pd.DataFrame):
                    payload = data.to_dict(orient="records")
                else:
                    payload = data
                raw = json.dumps(payload, ensure_ascii=False, default=str).encode()
                if key and not key.lower().endswith(".json"):
                    key = key + ".json"
                key = ctx.output_key(key or "result.json")
                ct = "application/json"
            else:
                if isinstance(data, bytes):
                    raw = data
                elif isinstance(data, pd.DataFrame):
                    raw = data.to_csv(index=False).encode()
                else:
                    raw = str(data).encode()
                if not key:
                    key = "result.bin"
                key = ctx.output_key(key)
                ct = "application/octet-stream"

            bucket = ctx.config.get("bucket", ctx.output_bucket)
            try:
                ctx.minio_client.put_object(
                    bucket,
                    key,
                    io.BytesIO(raw),
                    length=len(raw),
                    content_type=ct,
                )
            except Exception as e:
                err_minio_upload("minio_writer", key, f"{e}")
            return key
        except RuntimeError:
            raise
        except Exception as e:
            err_generic("minio_writer", f"MinIO 写入失败: {e}")
