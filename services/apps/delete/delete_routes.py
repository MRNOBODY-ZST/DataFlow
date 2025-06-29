from fastapi import APIRouter,HTTPException
from core.service import delete_image

router = APIRouter(
    prefix="/delete",
    tags=["delete"],
)
@router.delete("/{image_id}",summary="删除影像：包含MinIO 对象与数据库记录")
def delete_img(image_id: str):
    """
    入口：DELETE /delete/{image_id}
    说明：调用 service.delete_image 执行：
            1. 从 MinIO 删除对应对象
            2. 从数据库删除记录
    """
    try:
        delete_image(image_id)
        return {"detail": "影像删除成功"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))