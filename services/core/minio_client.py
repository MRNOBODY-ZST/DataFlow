r'''
1、这段代码以函数式风格封装了MinIO最常用的操作，提供简洁易用的接口。
2、支持文件上传、流上传、删除、存在检测、生成临时访问URL和对象复制等核心功能。
3、采用全局客户端实例和默认bucket设计，便于快速集成和使用。
4、适合用在数据源管理模块中管理遥感影像文件。
'''
from minio import Minio
from minio.error import S3Error
from datetime import timedelta
import os

# 全局MinIO客户端实例
minio_client = None
# 当前操作的默认bucket
CURRENT_BUCKET = "images"

# minio_client = Minio(
#     "127.0.0.1:9000",  # 替换为你自己的 MinIO 服务地址
#     access_key="admin",
#     secret_key="password",
#     secure=False  # 如果使用 http，secure 设置为 False
# )
def init_minio_client(endpoint="127.0.0.1:9000", access_key="admin", secret_key="password", secure=False):
    global minio_client

    if minio_client is None:  # 如果没有初始化，则初始化
        print("Initializing MinIO client...")  # 打印初始化信息
        minio_client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        print(f"MinIO client initialized: {minio_client}")  # 打印初始化后的 minio_sdk 对象

    return minio_client

def ensure_bucket(bucket_name=CURRENT_BUCKET):
    """
    确保指定的bucket存在
    Args:
        bucket_name: 要检查或创建的bucket名称
    Raises:
        RuntimeError: 如果客户端未初始化
    """
    if minio_client is None:
        raise RuntimeError("MinIO客户端未初始化")
        
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

def switch_bucket(new_bucket):
    """
    切换当前操作的bucket
    Args:
        new_bucket: 新的bucket名称
    Raises:
        ValueError: 如果bucket不存在
        RuntimeError: 如果客户端未初始化
    """
    if minio_client is None:
        raise RuntimeError("MinIO客户端未初始化")
        
    if not minio_client.bucket_exists(new_bucket):
        raise ValueError(f"Bucket {new_bucket} 不存在")
    global CURRENT_BUCKET
    CURRENT_BUCKET = new_bucket

def upload_file(remote_path, local_path, bucket=CURRENT_BUCKET):
    """
    上传本地文件到MinIO
    Args:
        remote_path: 文件在MinIO中的存储路径
        local_path: 本地文件路径
        bucket: 目标bucket名称
    Returns:
        包含成功状态和路径的字典
    Raises:
        RuntimeError: 如果上传失败或客户端未初始化
    """
    if minio_client is None:
        raise RuntimeError("MinIO客户端未初始化")
        
    try:
        file_stat = os.stat(local_path)
        with open(local_path, 'rb') as f:
            minio_client.put_object(bucket, remote_path, f, file_stat.st_size)
        return {"status": "success", "path": remote_path}
    except Exception as e:
        raise RuntimeError(f"上传失败: {e}")

def upload_stream(remote_path, data_stream, length, bucket=CURRENT_BUCKET):
    """
    上传数据流到MinIO
    Args:
        remote_path: 文件在MinIO中的存储路径
        data_stream: 数据流对象
        length: 数据流长度
        bucket: 目标bucket名称
    Returns:
        包含成功状态和路径的字典
    Raises:
        RuntimeError: 如果上传失败或客户端未初始化
    """
    if minio_client is None:
        raise RuntimeError("MinIO客户端未初始化")
        
    try:
        minio_client.put_object(bucket, remote_path, data_stream, length)
        return {"status": "success", "path": remote_path}
    except Exception as e:
        raise RuntimeError(f"上传失败: {e}")

def delete_object(remote_path, bucket=CURRENT_BUCKET):
    """
    删除MinIO中的对象
    Args:
        remote_path: 文件在MinIO中的存储路径
        bucket: 目标bucket名称
    Returns:
        包含成功状态和删除路径的字典
    Raises:
        RuntimeError: 如果删除失败或客户端未初始化
    """
    if minio_client is None:
        raise RuntimeError("MinIO客户端未初始化")
        
    try:
        minio_client.remove_object(bucket, remote_path)
        return {"status": "success", "deleted": remote_path}
    except S3Error as e:
        raise RuntimeError(f"删除失败: {e}")

def object_exists(remote_path, bucket=CURRENT_BUCKET):
    """
    检查对象是否存在
    Args:
        remote_path: 文件在MinIO中的存储路径
        bucket: 目标bucket名称
    Returns:
        bool: 对象是否存在
    Raises:
        RuntimeError: 如果检查失败或客户端未初始化
    """
    if minio_client is None:
        raise RuntimeError("MinIO客户端未初始化")
        
    try:
        minio_client.stat_object(bucket, remote_path)
        return True
    except S3Error as e:
        if e.code == 'NoSuchKey':
            return False
        raise

def get_presigned_url(remote_path, expires=timedelta(hours=1), bucket=CURRENT_BUCKET):
    """
    生成预签名下载URL
    Args:
        remote_path: 文件在MinIO中的存储路径
        expires: 链接过期时间
        bucket: 目标bucket名称
    Returns:
        str: 预签名URL
    Raises:
        RuntimeError: 如果生成失败或客户端未初始化
    """
    if minio_client is None:
        raise RuntimeError("MinIO客户端未初始化")
        
    try:
        return minio_client.presigned_get_object(bucket, remote_path, expires=expires)
    except S3Error as e:
        raise RuntimeError(f"生成下载链接失败: {e}")

def copy_object(source_path, target_bucket, target_path=None, source_bucket=CURRENT_BUCKET):
    """
    复制对象到另一个bucket
    Args:
        source_path: 源对象路径
        target_bucket: 目标bucket名称
        target_path: 目标路径（可选）
        source_bucket: 源bucket名称
    Returns:
        dict: 包含成功状态和复制路径的字典
    Raises:
        RuntimeError: 如果复制失败或客户端未初始化
    """
    if minio_client is None:
        raise RuntimeError("MinIO客户端未初始化")
        
    try:
        if not target_path:
            target_path = source_path
            
        minio_client.copy_object(
            target_bucket,
            target_path,
            f"s3://{source_bucket}/{source_path}"
        )
        return {"status": "success", "copied": target_path}
    except S3Error as e:
        raise RuntimeError(f"复制失败: {e}")

if __name__ == "__main__":
    # 测试完整操作流程
    try:
        # 初始化MinIO客户端
        init_minio_client("127.0.0.1:9000", "admin", "password", secure=False)
        
        # 确保默认bucket存在
        ensure_bucket("images")
        
        # 上传测试文件
        upload_file("remote/path/image.jpg", "local/path/image.jpg")
        
        # 检查文件是否存在
        if object_exists("remote/path/image.jpg"):
            print("文件上传成功")
            
        # 生成下载链接
        url = get_presigned_url("remote/path/image.jpg")
        print(f"下载链接: {url}")
        
        # 切换bucket并复制文件
        switch_bucket("backup")
        copy_object("remote/path/image.jpg", "backup", "remote/path/image_backup.jpg")
        
        # 切换回原bucket并删除文件
        switch_bucket("images")
        delete_object("remote/path/image.jpg")
        
    except Exception as e:
        print(f"操作失败: {e}")