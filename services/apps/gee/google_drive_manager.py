import os
import io
import uuid
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from core.minio_client import upload_stream, object_exists
from core.crud import create_metadata
from core.schemas import ImageMetadataCreate
from core.database import SessionLocal

r'''
1. Google Drive 认证相关
 SCOPES：只读访问 Google Drive。

 token.json：保存认证后的用户访问令牌。

 client_secrets.json：你从 Google Cloud Console 下载的 OAuth 客户端密钥文件。
'''
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# 配置文件路径基于当前文件位置定义
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config"))
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.json")
CLIENT_SECRETS = os.path.join(CONFIG_DIR, "client_secrets.json")

# 自动认证并创建 Google Drive API 的客户端实例 drive_service。
def authenticate_drive():
    import requests
    from google.auth.transport.requests import Request

    session = requests.Session()
    session.proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
    request_with_proxy = Request(session=session)

    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(request_with_proxy)  # 注意用 proxy 的 Request# ，🚀 用代理刷新
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    # return build("drive", "v3", credentials=creds, requestBuilder=lambda *args, **kwargs: request_with_proxy)
 # 取消自定义 requestBuilder，使用默认 HTTP 传输
    return build("drive", "v3", credentials=creds)

drive_service = authenticate_drive()

r'''
 2. 下载并上传单个文件：process_drive_file(file)
'''
def process_drive_file(file: dict , batch_id: str):
    db = SessionLocal()

    try:
        # 1、获取文件信息
        file_id = file["id"]
        file_name = file["name"]
        file_size = int(file.get("size", 0))

        # 2、跳过空文件
        if file_size == 0:
            print(f"跳过空文件：{file_name}")
            return

        # 定义对象名
        object_name = f"gee/{file_name}"

        # 先检查 MinIO 中是否已有该对象
        if object_exists(object_name):
            print(f"[跳过] MinIO 中已存在文件：{object_name}")
            return
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        # 3、文件被下载到内存中的 BytesIO() 对象 fh 中。
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"{file_name} 下载进度：{int(status.progress()*100)}%",flush=True)
        fh.seek(0)  # 这一步很关键！下载完成后重置流指针

        # 4、上传文件到 MinIO
        # object_name = f"gee/{file_name}"
        upload_stream(object_name, fh, file_size)
        # 5、写入数据库元数据
        image_id = str(uuid.uuid4())
        metadata_obj = ImageMetadataCreate(
            image_id=image_id,
            file_name=file_name,
            file_path=object_name,
            resolution="10m",
            date=datetime.now(),
            batch_id=batch_id # 直接添加批次 ID
        )
        create_metadata(db, metadata_obj)
        print(f"元数据写入成功: {file_name}",flush=True)

    except Exception as e:
        print(f"处理文件 {file.get('name')} 失败: {e}")
    finally:
        db.close()

r'''
3. 📂批量处理一个文件夹：batch_process_folder(folder_name) -----> 不分页
'''
def batch_process_folder(folder_name: str):
    """
    返回：成功处理的文件名列表
    """
    db = SessionLocal()
    batch_id = str(uuid.uuid4())  # 生成批次 ID
    try:
        # 查询文件
        response = drive_service.files().list(
            q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false",
            spaces="drive",
            fields="files(id, name)"
        ).execute()

        folders = response.get("files", [])
        if not folders:
            print(f"文件夹 {folder_name} 未找到")
            return []

        folder_id = folders[0]["id"]

        files_resp = drive_service.files().list(
            q=f"'{folder_id}' in parents and mimeType='image/tiff' and trashed=false",
            fields='files(id, name, size)',
            pageSize=1000
        ).execute()

        files = files_resp.get("files", [])
        print(f"共找到 {len(files)} 个文件")

        for file in files:
            process_drive_file(file, batch_id)  # 传递 batch_id

        return batch_id

    finally:
        db.close()
