from sqlalchemy import text
from core.database import engine, SessionLocal  # 假设你的代码文件叫 database.py

def test_connection():
    try:
        # 测试用engine直接执行简单SQL查询版本
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()
            print(f"数据库版本: {version[0]}")

        # 测试Session是否能正常创建并关闭
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("数据库连接测试成功！")
    except Exception as e:
        print(f"数据库连接失败: {e}")

if __name__ == "__main__":
    test_connection()
