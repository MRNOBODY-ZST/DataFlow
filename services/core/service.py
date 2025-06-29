r'''
这段代码是整个数据源管理模块的业务逻辑层（也就是 service 层）的核心，
它协调了 Google Drive、MinIO 和 PostgreSQL 三者之间的操作，
作用是封装影像数据的完整生命周期管理。
'''
from core import crud
from apps.gee.google_drive_manager import batch_process_folder
from apps.upload.local_data_manager import add_local_image
from core.crud import get_metadata, delete_metadata
from core.database import SessionLocal
from core.minio_client import delete_object
from datetime import datetime
from core.data_sources import DATA_SOURCES

def get_datasource(name: str):
    """获取注册的数据源实例"""
    if name not in DATA_SOURCES:
        raise ValueError(f"数据源 {name} 未注册")
    return DATA_SOURCES[name]


r'''
# 功能：从 Google Drive 指定文件夹批量导入 .tif 影像数据。
# 内部调用：google_drive_manager.py 中的 batch_process_folder()，它：
            下载 GEE 影像；
            上传至 MinIO；
            写入数据库元数据。
'''



# def import_gee_data(folder_name: str) -> list[str]:
#     """
#     返回：导入的文件名列表
#     """
#     return batch_process_folder(folder_name)

def import_gee_data(folder_name: str):
    """
    导入 GEE 文件夹中的文件,并返回批次id
    :param folder_name: 文件夹名称
    :return: 批次 ID
    """
    batch_id = batch_process_folder(folder_name)  # 获取批次 ID
    return batch_id

r'''
# 功能：从本地导入 .tif 影像数据。
# 内部调用：local_data_manager.py 中的 add_local_image()，它：
            上传至 MinIO；
            写入数据库元数据。
'''


# def add_local_file(local_path: str, datasource_name='minio'):
#     """使用指定数据源上传本地文件
#     Args:
#         local_path: 本地文件路径
#         datasource_name: 数据源名称（默认'minio'）
#     """
#     datasource = get_datasource(datasource_name)
#     if datasource.type == 'minio':
#         return add_local_image(local_path, datasource.client)
#     raise NotImplementedError(f"不支持的数据源类型: {datasource.type}")
def add_local_file(local_path: str):
    return add_local_image(local_path)

# def batch_add_local_files(folder_path: str):
#     """
#     批量上传本地文件夹下的所有影像文件
#     """
#     return batch_add_local_images(folder_path)

r"""
# 功能：
"""
def add_multiple_local_files(local_paths: list[str]) -> list[str]:
    """
    批量调用 add_local_image，返回所有成功的 image_id 列表
    """
    image_ids = []
    for p in local_paths:
        image_id = add_local_image(p)
        image_ids.append(image_id)
    return image_ids


r'''
# 功能：查询影像元数据。
# 内部调用：crud.py 中的 get_metadata()。
'''


def query_metadata(image_id: str):
    db = SessionLocal()
    try:
        meta = get_metadata(db, image_id)
        return meta
    finally:
        db.close()


r'''
功能：更新影像的分辨率或日期等元数据字段
内部调用：crud.py 中的 update_metadata()。
'''


def update_metadata(image_id: str, resolution=None, date=None):
    db = SessionLocal()
    try:
        if date and isinstance(date, str):
            date = datetime.fromisoformat(date)
        crud.update_metadata(db, image_id, resolution, date)
    finally:
        db.close()


r'''
功能：删除影像，包括：
        删除 MinIO 中的对象（调用 minio_client.py中的 delete_object()）；
        删除 PostgreSQL 中的元数据（调用 crud.py中的 delete_metadata()）。
'''


def delete_image(image_id: str):
    db = SessionLocal()
    try:
        meta = get_metadata(db, image_id)
        if not meta:
            raise Exception("影像不存在")

        delete_object(meta.file_path)
        delete_metadata(db, image_id)
    finally:
        db.close()



