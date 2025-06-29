from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, File
import os, shutil

from core.service import add_local_file, add_multiple_local_files

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

TEMP_UPLOAD_DIR = "./temp_uploads"
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)


@router.post("/local/single", summary="上传本地文件到 MinIO 并写入元数据")
async def upload_single_local(file: UploadFile = File(...)):
    """
    入口：POST /upload/local/single
    接收：表单文件 (UploadFile)
    步骤：
      1. 保存到本地 temp 目录 (TEMP_UPLOAD_DIR)
      2. 调用 service.add_local_file() 将它上传到 MinIO 并写入数据库
      3. 返回 image_id
    """
    # 构建临时存储文件的完整路径
    tmp_path = os.path.join(TEMP_UPLOAD_DIR, file.filename)
    # 将上传的文件保存到临时目录中
    with open(tmp_path, "wb") as f:
        # 复制上传文件的内容到目标文件
        shutil.copyfileobj(file.file, f)
    try:
        image_id = add_local_file(tmp_path)
        os.remove(tmp_path)  # 取消注释后，上传成功就会自动删掉本地临时文件
        return {"image_id": image_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/local/multiple", summary="前端可选批量多文件上传")
async def upload_multiple_local(files: List[UploadFile] = File(...)):
    """
    POST /upload/multiple/
    接收：form-data 多文件字段 'files'
    步骤：
      1. 将每个 UploadFile 写入 TEMP_UPLOAD_DIR
      2. 批量调用 Service 层 add_multiple_local_files
      3. 删除所有临时文件
      4. 返回 image_id 列表
    """
    tmp_paths = []
    try:
        # 1. 保存到本地临时文件夹
        for file in files:
            tmp_path = os.path.join(TEMP_UPLOAD_DIR, file.filename)
            with open(tmp_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            tmp_paths.append(tmp_path)

        # 2. Service 层批量上传
        image_ids = add_multiple_local_files(tmp_paths)

        # 3. 返回结果
        return {"image_ids": image_ids}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 4. 清理临时文件
        for p in tmp_paths:
            if os.path.exists(p):
                os.remove(p)

# @router.post("/local/batch", summary="批量上传本地文件夹下的所有文件")
# def upload_batch(folder_path: str = Form(..., description="服务器本地文件夹绝对或相对路径")):
#     """
#     批量上传文件夹：
#       1. 接收 form-data 字段 folder_path
#       2. 调用 local_data_manager.batch_add_local_images() 逐个上传
#       3. 返回上传结果摘要
#     """
#     try:
#         # 返回值可以是 None，函数里会打印每个文件的状态
#         batch_add_local_images(folder_path)
#         return {"detail": f"批量上传完成：{folder_path}"}
#     except NotADirectoryError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
