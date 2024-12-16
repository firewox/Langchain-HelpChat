# @Time  :2024/12/7 14:57
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import os
from backend.configs.backend_config import (EMBEDDING_MODEL,
                                            embedding_model_dict,
                                            PROMPT_TEMPLATE,
                                            CHUNK_SIZE,
                                            EMBEDDING_DEVICE,
                                            VECTOR_SEARCH_TOP_K,
                                            VECTOR_SEARCH_SCORE_THRESHOLD)
from typing import Dict,List,Tuple
from langchain_core.documents import Document
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from backend.beans.embedding_model_bean import (embedding_model_bean,#类
                                                similarity_search_with_score_by_vector,#函数
                                                similarity_search_with_score)#函数
from utils.logger import logger
from utils.utils import torch_gc
from openai import OpenAI
from backend.dao.knowledge_dao import knowledge_dao

class knowledge_services:
    embeddings_model_bean:embedding_model_bean = embedding_model_bean()


    # 查询所有已经向量化后知识向量库列表
    def knowledgeGetKnowledgeNameList(user_id:str):
        knowledge_name_list = knowledge_dao.knowledgeGetKnowledgeNameList(user_id=user_id)
        return knowledge_name_list

    # 初始化加载向量化模型
    def knowledgeInitEmbeddingModel(embedding_model_name:str,device:str,top_k:int):
        if knowledge_services.embeddings_model_bean.embeddings is not None:
            return True
        logger.info(f"向量化模型：{embedding_model_name}")
        try:
            knowledge_services.embeddings_model_bean.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[embedding_model_name],
                                                  model_kwargs={"device":device})
            knowledge_services.embeddings_model_bean.top_k=top_k
            return True
        except Exception as e:
            logger.error(f"初始向量模型出现错误，原因e={e}")
            return False

    # 加载知识向量库
    def knowledgeLoadVectorStore(embeddings:HuggingFaceEmbeddings,knowledge_name:str,knowledge_vector_path:str):
        if knowledge_services.embeddings_model_bean.vector_store is not None:
            return True
        try:
            if os.path.exists(knowledge_vector_path):
                knowledge_services.embeddings_model_bean.vector_store = FAISS.load_local(folder_path=knowledge_vector_path,embeddings=embeddings,allow_dangerous_deserialization=True)
                return True
            else:
                logger.error("选择的知识向量库路径不存在")
                return False
        except Exception as e:
            logger.info(f"加载知识向量库出现错误，原因e={e}")
            return False

    # Intent Recognition 意图识别操作，判断用户的query和知识向量库检索出来的片段的关联性大不大
    # 如果用户的问题和知识向量库相关，则返回 “rag”；如果不相关，则返回 “none”
    def knowledgeIntentRecognition(query:str,knowledge_rag:List[Tuple[Document, float]]):
        return "rag"

    # 将query和检索的知识片段注入prompt
    def knowledgeGeneratePrompt(related_docs:List[Tuple[Document, float]],
                                query:str,
                                prompt_template:str):
        context = "\n".join([doc.page_content for doc in related_docs])
        return prompt_template.replace("{question}", query).replace("{context}", context)

    # 处理知识向量库聊天的逻辑
    def knowledgeChat(user_id:str,
                      knowledge_vector_name:str,
                      prompt:str):
        knowledge_vector_path = knowledge_dao.knowledgeGetKnowledgeVectorPath(user_id=user_id,
                                                                              knowledge_vector_name=knowledge_vector_name)
        flag1 = knowledge_services.knowledgeInitEmbeddingModel(embedding_model_name=EMBEDDING_MODEL,
                                                               device=EMBEDDING_DEVICE,
                                                               top_k=VECTOR_SEARCH_TOP_K)
        flag2 = knowledge_services.knowledgeLoadVectorStore(embeddings=knowledge_services.embeddings_model_bean.embeddings,
                                                            knowledge_name=knowledge_vector_name,
                                                            knowledge_vector_path=knowledge_vector_path)
        if not (flag1 and flag2):
            logger.info(f"##########not (flag1 and flag2)={not (flag1 and flag2)}")
            return None
        FAISS.similarity_search_with_score_by_vector = similarity_search_with_score_by_vector#
        FAISS.similarity_search_with_score = similarity_search_with_score#
        knowledge_services.embeddings_model_bean.vector_store.chunk_size = CHUNK_SIZE # 匹配后单段上下文长度
        knowledge_services.embeddings_model_bean.vector_store.chunk_content = True
        knowledge_services.embeddings_model_bean.vector_store.score_threshold = VECTOR_SEARCH_SCORE_THRESHOLD # 知识检索内容相关度 Score, 数值范围约为0-1100，如果为0，则不生效

        # 计算用户问题和知识向量库中知识向量的相似度匹配
        related_docs_with_score = knowledge_services.embeddings_model_bean.vector_store.similarity_search_with_score(
            query=prompt,
            k=knowledge_services.embeddings_model_bean.top_k)
        torch_gc()
        # query的意图识别
        flag3 = knowledge_services.knowledgeIntentRecognition(query=prompt,knowledge_rag=related_docs_with_score)
        if "rag".lower() != flag3.lower():
            pass
        prompt_new = knowledge_services.knowledgeGeneratePrompt(query=prompt,
                                                   related_docs=related_docs_with_score,
                                                   prompt_template=PROMPT_TEMPLATE)
        return prompt_new,related_docs_with_score