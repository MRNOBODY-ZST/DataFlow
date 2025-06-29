r'''
这段代码是用 Pydantic 来定义数据验证和序列化模型，
主要用于 FastAPI 这类框架中，用来验证请求数据和格式化响应数据。
'''
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ImageMetadataBase(BaseModel):
    file_name: str
    file_path: str
    resolution: str
    date: datetime
    batch_id: Optional[str] = None  # 修改为可选字段

class ImageMetadataCreate(ImageMetadataBase):
    image_id: str
    # batch_id: str  # 显式继承并声明必填字段

class ImageMetadata(ImageMetadataBase):
    image_id: str

    class Config:
        orm_mode = True
