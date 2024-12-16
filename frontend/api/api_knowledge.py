# @Time  :2024/12/7 11:36
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from typing import Dict,List
import frontend.configs.frontend_config as config
import requests
from utils.logger import logger


# 处理关于 chat 的逻辑请求，分发请求
class api_knowledge:
    def __init__(self):
        self._embedding_model_name = "text2vec-base-chinese-paraphrase" #选中的向量化模型
        self._embedding_model_list = [] #所有的向量化模型集合
        self._user_name = "test"
        self._password = "1"
        self._knowledge_name_list = [] #知识向量库的文件集合
        self._knowledge_name = "" #选中的知识向量库的文件名
        self._upload_file_name = "" #上传的文件夹的文件名称
        self._upload_files_list = [] #上传的文件集合
        self._backend_url = str(config.BACKEND_SERVER.get("host","127.0.0.1"))+":"+str(config.BACKEND_SERVER.get("port","8601"))
        self._requests = requests
        self._file_name = "" #选中的文件名
        self._file_name_list = [] #所有的文件集合


    # POST 请求：返回knowledge_name_list
    def get_knowledge_name_list(self,user_id:str):
        # TODO 假数据 向后端发送请求
        #knowledge_name_list = api_server.get_knowledge_name_list(user_name=self.user_name)
        knowledge_name_list = ["shen_yin_wang_zuo_FAISS_text2vec-base-chinese-paraphrase",
                               "shen_yin_wang_zuo_FAISS_text2vec-base-chinese"]
        self.knowledge_name = knowledge_name_list[0]
        self.knowledge_name_list = knowledge_name_list
        data = {"user_id":user_id}
        response = self.requests.get(self.backend_url+"/get_knowledge_name_list",params=data)
        logger.info(f"\n查询数据库response={response}")
        if response.status_code==200:
            resu = response.json()
            logger.info(f"\n查询知识向量库：resu={resu}")
            if resu.get("msg") is not None:
                self.knowledge_name_list = resu.get("msg")
                self.knowledge_name = self.knowledge_name_list[0]
        return self.knowledge_name_list




    @property # java里的getting方法，访问成员变量
    def embedding_model_name(self):
        return self._embedding_model_name

    @embedding_model_name.setter # java里的setting方法，赋值成员变量
    def embedding_model_name(self,embedding_model_name:str):
        self._embedding_model_name = embedding_model_name

    @property # java里的getting方法，访问成员变量
    def embedding_model_list(self):
        return self._embedding_model_list

    @embedding_model_list.setter # java里的setting方法，赋值成员变量
    def embedding_model_list(self,embedding_model_list:str):
        self._embedding_model_list = embedding_model_list

    @property # java里的getting方法，访问成员变量
    def user_name(self):
        return self._user_name

    @user_name.setter # java里的setting方法，赋值成员变量
    def user_name(self,user_name:str):
        self._user_name = user_name

    @property # java里的getting方法，访问成员变量
    def password(self):
        return self._password

    @password.setter # java里的setting方法，赋值成员变量
    def password(self,password:str):
        self._password = password

    @property # java里的getting方法，访问成员变量
    def knowledge_name_list(self):
        return self._knowledge_name_list

    @knowledge_name_list.setter # java里的setting方法，赋值成员变量
    def knowledge_name_list(self,knowledge_name_list:str):
        self._knowledge_name_list = knowledge_name_list

    @property
    def knowledge_name(self):
        return self._knowledge_name

    @knowledge_name.setter
    def knowledge_name(self,knowledge_name):
        self._knowledge_name = knowledge_name

    @property
    def upload_file_name(self):
        return self._upload_file_name

    @upload_file_name.setter
    def upload_file_name(self,upload_file_name):
        self._upload_file_name = upload_file_name

    @property
    def upload_files_list(self):
        return self._upload_files_list

    @upload_files_list.setter
    def upload_files_list(self,upload_files_list):
        self._upload_files_list = upload_files_list

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self,file_name):
        self._file_name = file_name

    @property
    def file_name_list(self):
        return self._file_name_list

    @file_name_list.setter
    def file_name_list(self,file_name_list):
        self._file_name_list = file_name_list

    @property
    def backend_url(self):
        return self._backend_url
    @backend_url.setter
    def backend_url(self,backend_url):
        self._backend_url = backend_url

    @property
    def requests(self):
        return self._requests
    @requests.setter
    def requests(self,requests):
        self._requests = requests