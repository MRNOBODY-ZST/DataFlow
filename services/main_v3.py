import os
# 如果需要全局代理，可以在这里设置
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 数据源注册（确保在应用启动时完成）
from core.data_sources import register_minio_datasource, register_postgresql_datasource
register_minio_datasource('minio')
register_postgresql_datasource('postgresql', 'postgresql://postgres:123456@localhost:5432/postgres')

app = FastAPI(
    title="数据源管理模块 - API",
    version="1.0.0",
    description="后端只负责 JSON 接口，供前端调用"
)

# ----------------------------------------------------------------
# 1. CORS 配置：允许来自前端开发服务器的跨域请求
origins = [
    "http://localhost:5174",
    "http://localhost:5173",
    # 线上部署后，如果有自定义域名，也可以加在这里
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # 允许的源（域名）
    allow_credentials=True,
    allow_methods=["*"],           # 允许所有 HTTP 方法
    allow_headers=["*"],           # 允许所有 Header
)
# ----------------------------------------------------------------

# ----------------------------------------------------------------
# 2. 引入并注册各子路由模块
from apps.gee.gee_routes import router as gee_router
from apps.upload.upload_routes import router as upload_router
from apps.metadata.metadata_routes import router as metadata_router
from apps.delete.delete_routes import router as delete_router
from apps.cleaning.cleaning_routes import router as cleaning_router




app.include_router(gee_router)
app.include_router(upload_router)
app.include_router(metadata_router)
app.include_router(delete_router)
app.include_router(cleaning_router)

@app.get("/", summary="健康检查")
def health_check():

    return {"status": "OK", "message": "服务正常运行"}

# 打印已注册的数据源
from core.data_sources import DATA_SOURCES
print("已注册的数据源：")
for name, datasource in DATA_SOURCES.items():
    print(f"数据源名称: {name}, 类型: {datasource.type}")
