from minio.error import S3Error
from nodes.base import BaseNode, NodeContext
from nodes._input_utils import err_minio_missing_key, err_minio_not_found, err_generic


class MinioReaderNode(BaseNode):
    """Read from MinIO."""

    def execute(self, inputs: list, ctx: NodeContext):
        try:
            bucket = ctx.config.get("bucket", ctx.input_bucket)
            key = ctx.config.get("key", "")
            prefix = ctx.config.get("prefix", "")
            batch = bool(prefix) or (key and key.endswith("/"))

            if batch:
                folder = prefix or key
                if not folder:
                    err_minio_missing_key("minio_reader")
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
                    err_minio_not_found("minio_reader", folder, bucket)
                return items

            obj_key = key or ctx.config.get("input_key")
            if not obj_key:
                err_minio_missing_key("minio_reader")
            try:
                response = ctx.minio_client.get_object(bucket, obj_key)
            except S3Error as e:
                err_minio_not_found("minio_reader", obj_key, bucket)
            try:
                data = response.read()
            finally:
                response.close()
                response.release_conn()
            return data
        except RuntimeError:
            raise
        except Exception as e:
            err_generic("minio_reader", f"MinIO 读取失败: {e}")
