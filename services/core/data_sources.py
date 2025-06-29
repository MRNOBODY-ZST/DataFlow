import os  # 已有导入

# 新增环境变量检查
IS_TEST_ENV = os.getenv('APP_ENV') == 'test'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.crud import insert_data, update_data, delete_data, query_data
from core.minio_client import init_minio_client
from core.database import SessionLocal

# 定义数据源基类
class DataSource:
    """数据源基类"""

    def __init__(self, name: str, type_: str, client: object, operations: dict):
        self.name = name  # 数据源唯一标识
        self.type = type_  # 'minio' 或 'postgresql'
        self.client = client  # 底层客户端实例（如 MinIO SDK、PostgreSQL连接）
        self.operations = operations  # 数据源操作函数集合

    def __repr__(self):
        return f"DataSource(name='{self.name}', type='{self.type}', client={self.client} , operations={self.operations})"


# 数据源注册表DATA_SOURCES是一个全局字典, 键为数据源名称name，值为数据源DataSource对象
DATA_SOURCES = {}

r"""
DATA_SOURCES = {
    "minio": DataSource(name="minio", type_="minio", client=minio_sdk, operations={
        "switch_bucket": minio_switch,
        "upload_file": minio_upload,
        "copy_object": minio_copy,
        "object_exists": minio_exists
    }),
    "postgresql": DataSource(name="postgresql", type_="postgresql", client=SessionLocal(), operations={
        "insert": insert_data,
        "update": update_data,
        "delete": delete_data,
        "query": query_data
    })
}

"""

def register_datasource(name: str, type_: str, client: object, operations: dict):
    """通用的数据源注册函数"""
    # 注册数据源到全局字典中，键为数据源名称，值为数据源对象
    DATA_SOURCES[name] = DataSource(name=name, type_=type_, client=client, operations=operations)


# 注册MinIO数据源
def register_minio_datasource(name: str):
    from core.minio_client import (
        switch_bucket as minio_switch,
        upload_file as minio_upload,
        copy_object as minio_copy,
        object_exists as minio_exists
    )

    minio_client = init_minio_client()
    print(f"minio_client after initialization: {minio_client}")

    operations = {
        "switch_bucket": minio_switch,
        "upload_file": minio_upload,
        "copy_object": minio_copy,
        "object_exists": minio_exists
    }
    
    # 仅在测试环境执行验证逻辑
    if IS_TEST_ENV:
        try:
            buckets = minio_client.list_buckets()
            print(f"MinIO client initialized successfully. Buckets: {buckets}")
        except Exception as e:
            print(f"Error initializing MinIO client: {e}")
    
    # 注册 MinIO 数据源
    register_datasource(name, 'minio', minio_client, operations)


# 注册PostgreSQL数据源, 调用 register_datasource() 将 PostgreSQL 数据源注册到 DATA_SOURCES 中
def register_postgresql_datasource(name: str, database_url: str):
    operations = {
        "insert": insert_data,
        "update": update_data,
        "delete": delete_data,
        "query": query_data
    }
    # 使用数据库 URL 创建 SQLAlchemy 引擎
    engine = create_engine(database_url)

    # 创建 SessionLocal，绑定到指定的引擎
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 使用 SQLAlchemy 创建 PostgreSQL 客户端
    client = SessionLocal()

    # 注册 PostgreSQL 数据源
    register_datasource(name, 'postgresql', client, operations)

if __name__ == '__main__':
    register_minio_datasource('minio')
    print(DATA_SOURCES)
    # register_postgresql_datasource('postgresql', 'postgresql://postgres:123456@localhost:5432/postgres')
    # print(DATA_SOURCES)