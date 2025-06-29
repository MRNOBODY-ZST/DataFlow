from fastapi import APIRouter, HTTPException
from apps.cleaning.cleaning_service import MinioCleaning, PostgresqlCleaning

router = APIRouter(prefix="/cleaning", tags=["data cleaning"])

# MinIO 数据源清洗路由
@router.post("/minio/start")
async def start_minio_cleaning(source_name: str, source_path: str, target_name=None):
    """触发 MinIO 数据源清洗任务"""
    try:
        # 使用 MinioCleaning 类来执行清洗
        cleaner = MinioCleaning(source_name, source_path, target_name)
        result = cleaner.clean()
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PostgreSQL 数据源清洗路由
@router.post("/postgresql/start")
async def start_postgresql_cleaning(source_name: str, table_name: str, condition: str):
    """触发 PostgreSQL 数据源清洗任务"""
    try:
        # 使用 PostgresqlCleaning 类来执行清洗
        cleaner = PostgresqlCleaning(source_name, table_name, condition)
        result = cleaner.clean()
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
