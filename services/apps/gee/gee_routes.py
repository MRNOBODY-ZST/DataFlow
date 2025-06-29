from fastapi import APIRouter, HTTPException
from core.service import import_gee_data
from apps.gee.gee_export_manager import export_monthly_images, export_one_day_image

router = APIRouter(
    prefix="/gee",
    tags=["gee"]
)

@router.post("/import/{folder_name}", summary="从 Google Drive 指定文件夹批量导入影像")
def import_gee_folder(folder_name: str):
    """
    入口：POST /gee/import/{folder_name}
    说明：调用 service.import_gee_data，将 Google Drive 上名为 folder_name 的文件夹下的 TIFF 批量下载、
         上传到 MinIO，并写入数据库元数据。
    """
    try:
        processed = import_gee_data(folder_name)
        count = len(processed)
        return {
            "detail": f"GEE 文件夹 '{folder_name}' 导入完成，共 {count} 个文件",
            "files": processed
        }
    except Exception as e:
        # 如果抛出错误，向客户端返回 500
        raise HTTPException(status_code=500, detail=str(e))






@router.post("/export/", summary="导出 GEE 月度影像")
def export_monthly_route(start_year: int, end_year: int):
    """
    入口：POST /gee/export/?start_year=2022&end_year=2023
    说明：调用 gee_export_manager.export_monthly_images，将指定年份范围内的影像导出到 Drive。
    """
    try:
        export_monthly_images(start_year, end_year)
        return {"detail": f"GEE 月度导出任务已提交：{start_year} ~ {end_year}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export_one_day/", summary="导出 GEE 单日影像")
def export_one_day_route(year: int, month: int, day: int):
    """
    入口：POST /gee/export_one_day/?year=2022&month=3&day=16
    说明：调用 gee_export_manager.export_one_day_image，将指定日期的中位数合成影像导出到 Drive。
    """
    try:
        export_one_day_image(year, month, day)
        return {"detail": f"GEE 单日导出任务已触发：{year}-{month}-{day}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
