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
        bucket = ctx.config.get("bucket", ctx.input_bucket)
        batch = ctx.config.get("batch", False)
        if isinstance(batch, str):
            batch = batch.lower() in ("true", "1", "yes")

        prefix = ctx.config.get("prefix", "")
        key = ctx.config.get("key", "")

        if not batch and (prefix or key.endswith("/")):
            batch = True

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
            return items

        obj_key = key or ctx.config.get("input_key")
        response = ctx.minio_client.get_object(bucket, obj_key)
        try:
            data = response.read()
        finally:
            response.close()
            response.release_conn()
        return data
