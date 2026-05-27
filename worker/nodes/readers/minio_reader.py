<<<<<<< HEAD
from minio.error import S3Error

from nodes.base import BaseNode, NodeContext
=======
from nodes.base import BaseNode, NodeContext, NodeSchema, FieldDef
>>>>>>> 878b7e2 (feat: auto parser for nodes)


class MinioReaderNode(BaseNode):
    """Read from MinIO — single file or batch (all files under a prefix).

    Config:
        key: str       — object key (single mode)
        prefix: str    — key prefix / folder (batch mode)
        bucket: str    — source bucket (default: input)
        batch: bool    — when true, read all files under prefix and return list
    """

    @classmethod
    def schema(cls) -> NodeSchema:
        return NodeSchema(
            type="minio_reader",
            label="MinIO 读取",
            category="readers",
            icon="CloudArrowDownIcon",
            fields=[
                FieldDef(key="key", label="文件或文件夹路径", type="file-picker",
                         placeholder="input/xxx/file", required=True, inline=True),
                FieldDef(key="bucket", label="源 Bucket（默认 dataflow-input）", type="text",
                         placeholder="dataflow-input"),
            ],
        )

    def execute(self, inputs: list, ctx: NodeContext):
        bucket = ctx.config.get("bucket", ctx.input_bucket)
        key = ctx.config.get("key", "")
        prefix = ctx.config.get("prefix", "")
        batch = bool(prefix) or key.endswith("/")

        if batch:
            folder = prefix or key
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
                raise FileNotFoundError(
                    f"No objects found under prefix '{folder}' in bucket '{bucket}'"
                )
            return items

        obj_key = key or ctx.config.get("input_key")
        if not obj_key:
            raise ValueError("minio_reader: no 'key' configured and no upstream input")
        try:
            response = ctx.minio_client.get_object(bucket, obj_key)
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise FileNotFoundError(
                    f"Object '{obj_key}' not found in bucket '{bucket}'. "
                    f"Verify the file exists and the path is correct."
                ) from e
            raise
        try:
            data = response.read()
        finally:
            response.close()
            response.release_conn()
        return data
