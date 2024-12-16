# @Time  :2024/12/15 18:04
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import datetime

from backend.utils.database import get_db_session
from backend.beans.model_beans import History,User
from sqlmodel import select
from utils.logger import logger
import json

class login_dao:
    #登录
    def login(user_name:str,password:str):
        with get_db_session() as session:
            statement = select(User).where(
                User.user_name==user_name,
                User.password==password,
            )
            results = session.exec(statement).first()
            if results:
                return results
            else:
                return None