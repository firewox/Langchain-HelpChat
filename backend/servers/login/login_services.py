# @Time  :2024/12/15 18:03
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from backend.dao.login_dao import login_dao


class login_services:
    # 处理登录逻辑
    def login(user_name:str,password:str):
        resu = login_dao.login(user_name=user_name, password=password)
        if resu:
            return resu
        return None
