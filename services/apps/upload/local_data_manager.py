r'''
功能：
1、单个文件上传：本地影像文件上传到 MinIO，生成唯一路径并写入元数据。
2、批量文件上传：批量处理指定文件夹下所有影像文件。
'''

import os
import uuid
from datetime import datetime

from core.minio_client import upload_file
from core.crud import create_metadata
from core.schemas import ImageMetadataCreate
from core.database import SessionLocal


# ✅ 单个本地影像文件上传
def add_local_image(local_path: str):
    """上传本地文件到指定客户端
    Args:
        local_path: 本地文件路径
    """
    if not os.path.isfile(local_path):
        raise FileNotFoundError(f"{local_path} 文件不存在")

    file_name = os.path.basename(local_path)
    object_name = f"local/{uuid.uuid4().hex}_{file_name}"  # 避免重名覆盖

    # 上传文件至 MinIO
    upload_file(object_name, local_path)

    # 写入数据库元数据
    db = SessionLocal()
    try:
        image_id = str(uuid.uuid4())
        metadata_obj = ImageMetadataCreate(
            image_id=image_id,
            file_name=file_name,
            file_path=object_name,
            resolution="未知",
            date=datetime.now(),
            # batch_id=""
        )
        create_metadata(db, metadata_obj)
        print(f"文件上传并写入元数据成功：{file_name}")
        return image_id
    finally:
        db.close()


# # ✅ 批量上传文件夹下所有影像文件
# def batch_add_local_images(folder_path: str):
#     if not os.path.isdir(folder_path):
#         raise NotADirectoryError(f"{folder_path} 不是有效的文件夹路径")
#
#     print(f"开始批量上传文件夹：{folder_path}")
#     for file_name in os.listdir(folder_path):
#         file_path = os.path.join(folder_path, file_name)
#         if os.path.isfile(file_path):
#             try:
#                 image_id = add_local_image(file_path)
#                 print(f"成功：{file_name}（image_id={image_id}）")
#             except Exception as e:
#                 print(f"失败：{file_name}（错误：{e}）")
