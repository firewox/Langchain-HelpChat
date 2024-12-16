# @Time  :2024/12/15 17:53
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import requests
import frontend.configs.frontend_config as config
from utils.logger import logger

class api_login:
    def __init__(self):
        self.requests=requests
        self.backend_url = str(config.BACKEND_SERVER.get("host","127.0.0.1"))+":"+str(config.BACKEND_SERVER.get("port","8601"))
        self.user_id:str = "100"
        self.user_name:str = "lyt"

    # POST 请求，用户登录
    def login(self,user_name:str,password:str):
        data={"user_name":user_name,"password":password}
        response = self.requests.post(self.backend_url+"/login",json=data)
        logger.info(f"\nself.backend_url={self.backend_url}")
        if response.status_code==200:
            resu = response.json()
            logger.info(f"resu={resu}")
            self.user_id=resu.get("msg").get("user_id")
            self.user_name=resu.get("msg").get("user_name")
            return {"user_id":self.user_id,"user_name":self.user_name}
        else:
            logger.info(f"\n请求错误={response}")
            return None