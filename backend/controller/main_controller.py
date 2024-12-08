# @Time  :2024/12/5 19:27
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from backend.configs.model_config import VERSION,OPEN_CROSS_DOMAIN
from utils.utils import BaseResponse
from backend.servers.chat.openai_chat_services import openai_chat_services # services的处理工具
from backend.servers.knowledge.knowledge_services import knowledge_services # services的处理工具
from typing import Dict,List
from backend.configs.model_config import VECTOR_SEARCH_TOP_K,EMBEDDING_DEVICE,PROMPT_TEMPLATE


# 后端请求入口
# GET 处理前端发送来的查询聊天历史记录
def get_history_chat(user_name:str,history_name:str="default"):
    messages = openai_chat_services.chatGetHistoryByUsernameAndHistoryName(user_name=user_name,history_name=history_name)
    return messages

# GET 处理前端发送来的大模型聊天请求
def get_chat(user_name:str,messages:List,model_name:str="glm-4-flash"):
    stream = openai_chat_services.chatGetChat(user_name=user_name,model_name=model_name,messages=messages)
    return stream

# GET 处理前端发送来的查询可用的大模型列表
def get_available_model_list(user_name:str):
    modele_list = openai_chat_services.chatGetAvailableModelList(user_name=user_name)
    return modele_list

# GET 处理前端发送来的查询历史聊天记录名称列表的请求
def get_history_name_list(user_name:str):
    history_name_list = openai_chat_services.chatGetHistoryNameList(user_name=user_name)
    return history_name_list

# GET 处理前端发送来的查询所有可用的向量化模型
def get_available_embedding_model_list(user_name:str):
    embedding_model_list = knowledge_services.knowledgeGetAvailableEmbeddingModelList(user_name=user_name)
    return embedding_model_list

# GET 处理前端发送来的查询所有已经向量化后的知识库列表
def get_knowledge_name_list(user_name:str):
    knowledge_name_list = knowledge_services.knowledgeGetKnowledgeNameList(user_name=user_name)
    return knowledge_name_list

# GET 处理前端发送来的知识向量库问答聊天
def get_knowledge_chat(user_name:str,
                       model_name:str,
                       embedding_model_name:str,
                       knowledge_name:str,
                       msgs:list):
    stream = knowledge_services.knowledgeChat(user_name=user_name,
                                  model_name=model_name,
                                  embedding_model_name=embedding_model_name,
                                  knowledge_name=knowledge_name,
                                              msgs=msgs,
                                  top_k=VECTOR_SEARCH_TOP_K,
                                  device=EMBEDDING_DEVICE,
                                  prompt_template=PROMPT_TEMPLATE)
    return stream