import io
import json
from nodes.base import BaseNode, NodeContext


class JsonWriterNode(BaseNode):

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            if not inputs:
                raise RuntimeError(
                    "JSON写入: 没有收到上游数据。请将本节点连接到上游输出节点。"
                )
            data = inputs[0]

            import pandas as pd
            if isinstance(data, pd.DataFrame):
                payload = data.to_dict(orient="records")
            elif isinstance(data, (bytes, bytearray)):
                try:
                    payload = json.loads(data.decode("utf-8"))
                except Exception:
                    raise RuntimeError(
                        f"JSON写入: 输入是 bytes 但不是合法 JSON（{len(data)} 字节）。"
                    )
            elif isinstance(data, str):
                try:
                    payload = json.loads(data)
                except Exception:
                    payload = data
            else:
                payload = data

            indent = ctx.config.get("indent", 2)
            ensure_ascii = bool(ctx.config.get("ensure_ascii", False))
            raw = json.dumps(
                payload, ensure_ascii=ensure_ascii, indent=indent,
                default=str,
            ).encode("utf-8")

            key = ctx.config.get("key") or ctx.source_filename or "result.json"
            if not key.lower().endswith(".json"):
                key = key + ".json"
            key = ctx.output_key(key)

            bucket = ctx.config.get("bucket", ctx.output_bucket)
            ctx.minio_client.put_object(
                bucket,
                key,
                io.BytesIO(raw),
                length=len(raw),
                content_type="application/json",
            )
            return key
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"JSON写入: {e}")
