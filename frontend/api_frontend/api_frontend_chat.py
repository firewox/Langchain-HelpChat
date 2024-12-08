# @Time  :2024/12/5 23:43
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from typing import Dict,List
import backend.controller.main_controller as api_server


# 处理关于 chat 的逻辑请求，分发请求
class api_frontend_chat:
    def __init__(self):
        self._model_name = "glm-4-flash"
        self._user_name = "test"
        self._password = "1"
        self._history_name = "default"
        self._model_list = []
        self._history_name_list = []
        self._messages = []


    # GET请求：请求获取历史聊天记录
    def get_history_chat(self,history_name:str="default"):
        #messages = [{"role":"user","content":"你是谁"},{"role":"assistant","content":"我是小助帮手"}]
        # 向后端发送请求
        messages = api_server.get_history_chat(user_name=self.user_name,history_name=history_name)
        self.messages = messages
        return messages

    # GET请求：大模型聊天数据请求
    def get_chat(self,model_name:str,messages:list):
        #stream = openai_chat_v2(model_name=self.model_name,messages=messages)
        # 向后端发送请求
        stream = api_server.get_chat(user_name=self.user_name,model_name=model_name,messages=[i for i in messages])
        return stream

    # GET请求：进行知识向量库助手问答，
    def get_knowledge_chat(self,model_name:str,embedding_model_name:str,knowledge_name:str,msgs:list):
        # 向后端发送请求
        stream = api_server.get_knowledge_chat(user_name=self.user_name,
                                               model_name=model_name,
                                               embedding_model_name=embedding_model_name,
                                               knowledge_name=knowledge_name,
                                               msgs=msgs)
        return stream

    # GET请求：input：bean_chat={ "messages":[]}
    def set_history_chat(self,messages):
        #保存聊天记录
        return "success"

    # GET请求：返回可用的llm接口
    def get_model_list(self):
        # 向后端发送请求
        model_list = api_server.get_available_model_list(user_name=self.user_name)
        self.model_list = model_list
        return model_list

    # GET请求：返回该用户的历史聊天记录名称的列表
    def get_history_name_list(self):
        # 向后端发送请求
        history_name_list = api_server.get_history_name_list(user_name=self.user_name)
        self.history_name_list = history_name_list
        self.history_name = history_name_list[0]
        return history_name_list


    @property # java里的getting方法，访问成员变量
    def model_name(self):
        return self._model_name

    @model_name.setter # java里的setting方法，赋值成员变量
    def model_name(self,model_name:str):
        self._model_name = model_name

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
    def history_name(self):
        return self._history_name

    @history_name.setter # java里的setting方法，赋值成员变量
    def history_name(self,history_name:str):
        self._history_name = history_name

    @property
    def model_list(self):
        return self._model_list

    @model_list.setter
    def model_list(self,model_list):
        self._model_list = model_list

    @property
    def history_name_list(self):
        return self._history_name_list

    @history_name_list.setter
    def history_name_list(self,history_name_list):
        self._history_name_list = history_name_list

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self,messages):
        self._messages = messages