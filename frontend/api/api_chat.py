# @Time  :2024/12/5 23:43
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from typing import Dict,List
import frontend.configs.frontend_config as config
import backend.configs.backend_config as backend_config
from utils.logger import logger
from openai import OpenAI
import requests
import datetime


# 处理关于 chat 的逻辑请求，分发请求
class api_chat:
    def __init__(self):
        self._model_name = "glm-4-flash"
        self._user_name = "test"
        self._password = "1"
        self._history_name = "default"
        self._model_list = []
        self._history_name_list = []
        self._messages = []
        self._backend_url = str(config.BACKEND_SERVER.get("host","127.0.0.1"))+":"+str(config.BACKEND_SERVER.get("port","8601"))
        self._requests = requests
        self._system_prompt = [{"role":"user","content":"你是谁"},{"role":"assistant","content":"我是小助帮手"}]


    # POST请求：请求获取历史聊天记录
    def get_history_chat(self,user_id:str,user_name:str,history_name:str="default"):
        messages = self.system_prompt
        data = {"user_id":user_id,"user_name":user_name,"history_name":history_name}
        #logger.info(f"\n请求获取历史聊天记录，参数data={data}")
        response = self.requests.post(self.backend_url+"/get_history_chat",json=data)
        #logger.info(f"\n请求获取历史聊天记录response.status_code={response.status_code}")
        if response.status_code == 200:
            result = response.json()
            logger.info(f"\n请求获取历史聊天记录result={result}")
            if result.get("msg") is not None and result.get("msg")!="":
                messages = result.get('msg')
        self.messages = messages
        return messages

    # POST请求：input：bean_chat={ "messages":[]}
    def set_history_chat(self,messages:list,user_id:str,user_name:str,history_name:str):
        #保存聊天记录
        messages = self.clean_messages(messages=messages)
        data={"user_id":user_id,"user_name":user_name,"messages":messages,"history_name":history_name}
        logger.info(f"\n保存聊天记录：data={data}")
        response = self.requests.post(self.backend_url+"/set_history_chat",json=data)
        if response.status_code==200:
            resu = response.json()
            if int(resu.get('msg'))==1:
                return "success"
            else:
                return "failure"
        else:
            return "failure"

    # POST 请求：返回该用户的历史聊天记录名称的列表
    def get_history_name_list(self,user_id:str):
        # 向后端发送请求
        #history_name_list = api_server.get_history_name_list(user_name=self.user_name)
        data={"user_id":user_id}
        response = self.requests.post(self.backend_url+"/get_history_name_list",json=data)
        if response.status_code==200:
            resu = response.json()
            if resu.get("msg") is None:
                logger.info(f"\n所有历史聊天记录列表是空的={resu}")
                self.history_name_list = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"会话"]
                self.history_name = self.history_name_list[0]
                return self.history_name_list
            else:
                logger.info(f"\n所有历史聊天记录列表={resu}")
                self.history_name_list = resu.get("msg")
                self.history_name = self.history_name_list[0]
                return self.history_name_list
        else:
            self.history_name_list = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"会话"]
            self.history_name = self.history_name_list[0]
            return self.history_name_list

    # GET 请求：新建大模型会话，返回创建的新的聊天会话名称，返回新的历史聊天记录名称
    def create_new_dialogue(self,user_id:str):
        data={"user_id":user_id,"messages":self.system_prompt}
        response = self.requests.get(self.backend_url+"/create_new_dialogue",params=data)
        if response.status_code==200:
            resu=response.json()
            if resu['msg'] is not None:
                history_name = resu["msg"]
                return history_name
            else:
                logger.error(f"\n新建聊天会话失败,请求失败")
                return "default"
        else:
            logger.error(f"\n新建聊天会话失败")
            return "default"

    # 本地处理：返回可用的llm接口
    def get_model_list(self):
        logger.info(f"\n config.MODEL_LIST.keys()={list(config.MODEL_LIST.keys())}")
        self.model_list = list(config.MODEL_LIST.keys())
        return self.model_list

    # 本地处理：大模型聊天数据请求
    def get_chat(self,model_name:str,messages:list):
        msg = {"model":model_name,
              "messages":messages,
              "temperature":0.7,
              "max_tokens":None,
              "stream":True}
        cfg = {
            "model":model_name,
            "base_url":config.MODEL_LIST.get(model_name).get("base_url"),
            "api_key":config.MODEL_LIST.get(model_name).get("api_key"),
        }
        # Set OpenAI API key
        #logger.info(f"\ncfg={cfg}")
        client = OpenAI(api_key=cfg.get("api_key",""), base_url=cfg.get("base_url",""))
        stream = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=msg.get("stream"),
            temperature=msg.get("temperature"),
        )
        return stream


    # POST 请求：进行知识向量库助手问答，
    def get_knowledge_chat(self,user_id:str,knowledge_vector_name:str,messages:list,model_name:str):
        # 向后端发送请求
        # stream = api_server.get_knowledge_chat(user_name=self.user_name,
        #                                        model_name=model_name,
        #                                        embedding_model_name=embedding_model_name,
        #                                        knowledge_name=knowledge_name,
        #                                        msgs=msgs)
        # 向后端发送请求，发送：知识向量库名称、用户query，返回构建好的prompt（prompt里包括：检索匹配的上下文信息+用户query）
        # TODO 这里设置假的 构建的prompt
        prompt_query = messages[-1].get("content")
        prompt_new = "基于以下信息：回答我的问题，我的问题是："+prompt_query
        data = {"user_id":user_id,"knowledge_vector_name":knowledge_vector_name,"prompt":prompt_query}
        response = self.requests.post(self.backend_url+"/get_knowledge_chat",json=data)
        if response.status_code==200:
            resu = response.json()
            if resu.get("msg") is not None:
                prompt_new = resu.get("msg")
        messages[-1]['content']=prompt_new
        stream = self.get_chat(model_name=model_name,messages=messages)
        return stream


    # 清洗 messages ，当使用rag，上下文知识向量和query重新拼接到一起组成新prompt时，
    # 会出现 st.session_state.messages 里的user信息自动被更新注入。推测这是streamlit的bug，尚解决不了此bug，用清洗手段暂时回避
    def clean_messages(self,messages):
        cleaned_messages = list()
        for i in messages:
            if i.get("role") == "user" and backend_config.PROMPT_TEMPLATE_FLAG in i.get("content"):
                index = i.get("content").rfind(backend_config.PROMPT_TEMPLATE_FLAG)
                i["content"] = i.get("content")[index+len(backend_config.PROMPT_TEMPLATE_FLAG):]
                logger.info(f"\n##### 清洗messages")
                cleaned_messages.append(i)
            else:
                cleaned_messages.append(i)
        return cleaned_messages



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

    @property
    def system_prompt(self):
        return self._system_prompt
    @system_prompt.setter
    def system_prompt(self,system_prompt):
        self._system_prompt = system_prompt

