from minio import Minio
from minio.error import S3Error
import traceback

def test_minio_connection():
    print("开始创建 MinIO 客户端...")
    try:
        client = Minio(
            "127.0.0.1:9000",
            access_key="admin",
            secret_key="password",
            secure=False
        )
        print("客户端创建成功，准备检查桶...")

        bucket_name = "images"

        if client.bucket_exists(bucket_name):
            print(f"桶 '{bucket_name}' 存在，连接成功！")
        else:
            print(f"桶 '{bucket_name}' 不存在，尝试创建桶...")
            client.make_bucket(bucket_name)
            print(f"桶 '{bucket_name}' 创建成功！")
    except S3Error as err:
        print(f"S3Error 连接失败，错误信息：{err}")
    except Exception as e:
        print("发生未知错误：")
        traceback.print_exc()

if __name__ == "__main__":
    test_minio_connection()
