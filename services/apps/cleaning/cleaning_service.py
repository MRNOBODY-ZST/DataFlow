from minio.commonconfig import CopySource
from sqlalchemy import text

from core.service import get_datasource

class MinioCleaning:
    def __init__(self, source_name: str, source_path: str, target_name=None):
        self.datasource = get_datasource(source_name)
        self.source_path = source_path
        # 如果传入了 target_name，则使用传入的值；
        # 如果未传入（即为 None），则使用默认格式：<源bucket名>-cleaned
        self.source_bucket, self.object_name = self.source_path.split("/", 1)
        self.target_name = target_name or f"{self.source_bucket}-cleaned"

    def clean(self):
        client = self.datasource.client  # MinIO SDK 实例
        """MinIO 数据源清洗逻辑"""
        if not client.bucket_exists(self.target_name):
            client.make_bucket(self.target_name)

        client.copy_object(
            bucket_name=self.target_name,
            object_name=self.object_name,
            source=CopySource(self.source_bucket, self.object_name)
        )

        return {
            "status": "success",
            "copied": True,
            "source_path": self.source_path,
            "target_name": self.target_name
        }


class PostgresqlCleaning:
    def __init__(self, source_name: str, table_name: str, condition: str):
        self.datasource = get_datasource(source_name)
        self.table_name = table_name
        self.condition = condition

    def clean(self):
        """PostgreSQL 数据源清洗逻辑"""
        db = self.datasource.client  # 获取数据库会话
        try:
            # 动态构建 SQL 查询进行清洗
            sql_query = f"DELETE FROM {self.table_name} WHERE {self.condition}"  # 清洗条件
            db.execute(text(sql_query))  # 使用 text() 包装查询语句
            db.commit()
            return {"status": "success", "message": "数据库清洗成功"}
        except Exception as e:
            db.rollback()
            return {"status": "failed", "message": str(e)}

