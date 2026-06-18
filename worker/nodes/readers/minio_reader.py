from minio.error import S3Error
from nodes.base import BaseNode, NodeContext


class MinioReaderNode(BaseNode):
    """Read from MinIO — single file or batch (all files under a prefix).

    Config:
        key: str       — object key (single mode)
        prefix: str    — key prefix / folder (batch mode)
        bucket: str    — source bucket (default: input)
        batch: bool    — when true, read all files under prefix and return list
    """

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            bucket = ctx.config.get("bucket", ctx.input_bucket)
            key = ctx.config.get("key", "")
            prefix = ctx.config.get("prefix", "")
            batch = bool(prefix) or (key and key.endswith("/"))

            if batch:
                folder = prefix or key
                if not folder:
                    raise RuntimeError(
                        "MinIO读取: 请在节点配置中提供 prefix（文件夹前缀）或 key（以 / 结尾）。"
                    )
                objects = ctx.minio_client.list_objects(bucket, prefix=folder, recursive=True)
                items = []
                for obj in objects:
                    if obj.object_name.endswith("/"):
                        continue
                    response = ctx.minio_client.get_object(bucket, obj.object_name)
                    try:
                        data = response.read()
                    finally:
                        response.close()
                        response.release_conn()
                    items.append({"key": obj.object_name, "data": data})
                if not items:
                    raise RuntimeError(
                        f"MinIO读取: 在 bucket '{bucket}' 前缀 '{folder}' 下找不到任何文件。请确认路径是否正确。"
                    )
                return items

            obj_key = key or ctx.config.get("input_key")
            if not obj_key:
                raise RuntimeError(
                    "MinIO读取: 请在节点配置中提供 key / input_key / prefix 之一，或连接上游节点。"
                )
            try:
                response = ctx.minio_client.get_object(bucket, obj_key)
            except S3Error as e:
                if e.code == "NoSuchKey":
                    raise RuntimeError(
                        f"MinIO读取: MinIO 中找不到 key='{obj_key}'（bucket='{bucket}'）。请确认文件是否存在或路径是否正确。"
                    )
                raise
            try:
                data = response.read()
            finally:
                response.close()
                response.release_conn()
            return data
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"MinIO读取: {e}")
