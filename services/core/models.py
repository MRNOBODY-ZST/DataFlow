r'''
这段代码定义了一个关系型数据库中用于保存遥感影像元数据的表结构，
字段包括唯一ID、文件名、存储路径、分辨率和日期，
方便程序后续执行增删查改操作。
'''
from sqlalchemy import Table, Column, String, DateTime
from core.database import metadata

images_metadata = Table(
    "images_metadata",          # 表名
    metadata,                  # 绑定到数据库元数据容器
    Column("image_id", String, primary_key=True, index=True),  # 主键字段，字符串类型，建立索引
    Column("file_name", String),     # 字符串类型字段，存影像文件名
    Column("file_path", String),     # 字符串类型字段，存影像文件在MinIO的路径
    Column("resolution", String),    # 字符串类型字段，存影像分辨率
    Column("date", DateTime),        # 日期时间类型字段，存影像采集或上传时间
    Column("batch_id", String),      # 字符串类型字段，存影像所属批次号
)

