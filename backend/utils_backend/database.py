# @Time  :2024/12/15 11:40
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from backend.beans.model_beans import *
from contextlib import contextmanager
import os
from utils.logger import logger
from dotenv import load_dotenv

# 加载环境变量
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env_backend")
load_dotenv(dotenv_path,override=True)


# 从环境变量中获取 MySQL 配置信息
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = int(os.getenv('MYSQL_PORT')) #type: ignore
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
# 创建数据库 URI
DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"


# 数据库创建连接
if os.getenv('Database_name')=='mysql':
    engine = create_engine(DATABASE_URI) # 创建数据库引擎
    SQLModel.metadata.create_all(engine) # 创建所有表
    logger.info("成功连接到 MySQL 数据库并创建表。")
else:
    #打印数据库连接失败异常日志
    logger.error("数据库连接失败!")
    raise Exception("数据库连接失败")


# 提供session对象
@contextmanager
def get_db_session():
    """Provide a transactional scope around a series of operations."""
    db = Session(engine)
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Session rollback because of exception: {e}")
        raise
    finally:
        if db:  # Check if db was successfully created before attempting to close
            db.close()