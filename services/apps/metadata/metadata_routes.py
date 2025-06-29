from fastapi import APIRouter, HTTPException
from core.service import query_metadata, update_metadata

router = APIRouter(
    prefix="/metadata",
    tags=["metadata"],
)

@router.get("/{image_id}", summary="根据image_id查询影像元数据")
def get_meta(image_id: str):
    """
    入口：GET /metadata/{image_id}
    说明：使用 service.query_metadata 查询数据库并返回元数据信息
    """
    meta = query_metadata(image_id)
    if not meta:
        raise HTTPException(status_code=404, detail="影像不存在")
    return {
        "image_id": meta.image_id,
        "file_name": meta.file_name,
        "file_path": meta.file_path,
        "resolution": meta.resolution,
        "date": meta.date
    }

@router.put("/{image_id}", summary="更新影像分辨率、日期等元数据")
def put_meta(image_id: str, resolution: str = None, date: str = None):
    """
    入口：PUT /metadata/{image_id}?resolution=10m&date=2024-10-01
    说明：使用 service.update_metadata 更新数据库中的分辨率或日期字段
    """
    try:
        update_metadata(image_id, resolution, date)
        return {"detail": "元数据更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))