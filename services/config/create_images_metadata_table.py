from sqlalchemy import Table, Column, String, DateTime
from core.database import metadata, engine

images_metadata = Table(
    "images_metadata",
    metadata,
    Column("image_id", String, primary_key=True),
    Column("file_name", String),
    Column("file_path", String),
    Column("resolution", String),
    Column("date", DateTime),
    Column("batch_id", String),
)

try:
    metadata.create_all(engine)  # 创建缺失的表
    print("数据库表 images_metadata 创建成功或已存在。")
except Exception as e:
    print(f"创建数据库表时发生错误: {e}")
