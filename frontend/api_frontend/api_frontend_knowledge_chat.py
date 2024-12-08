# @Time  :2024/12/7 11:36
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from typing import Dict,List
import backend.controller.main_controller as api_server


# 处理关于 chat 的逻辑请求，分发请求
class api_frontend_knowledge_chat:
    def __init__(self):
        self._embedding_model_name = "text2vec-base-chinese-paraphrase" #选中的向量化模型
        self._embedding_model_list = [] #所有的向量化模型集合
        self._user_name = "test"
        self._password = "1"
        self._knowledge_name_list = [] #知识向量库的文件集合
        self._knowledge_name = "" #选中的知识向量库的文件名
        self._upload_file_name = "" #上传的文件夹的文件名称
        self._upload_files_list = [] #上传的文件集合

        self._file_name = "" #选中的文件名
        self._file_name_list = [] #所有的文件集合


    # GET请求：向后台发送请求，挂载向量化模型
    def set_embedding_model(self,embedding_model_name):
        #保存聊天记录
        msg = api_server.set_embedding_model(embedding_model_name=embedding_model_name)
        return "success"

    # GET请求：返回embedding_model_list
    def get_embedding_model_list(self):
        # 向后端发送请求
        embedding_model_list = api_server.get_available_embedding_model_list(user_name=self.user_name)
        self.embedding_model_name = embedding_model_list[0]
        return embedding_model_list

    # GET请求：进行向量化操作
    def get_embedding_operate(self,embedding_model_name,file_name):
        # 向后端发送请求
        msg = api_server.get_embedding_operate(user_name=self.user_name,embedding_model_name=embedding_model_name,file_name=file_name)
        return "success"

    # GET请求：返回knowledge_name_list
    def get_knowledge_name_list(self):
        # 向后端发送请求
        knowledge_name_list = api_server.get_knowledge_name_list(user_name=self.user_name)
        self.knowledge_name = knowledge_name_list[0]
        self.knowledge_name_list = knowledge_name_list
        return knowledge_name_list




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