# @Time  :2024/12/15 23:29
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from backend.utils.database import get_db_session
from backend.beans.model_beans import *
from typing import List
from sqlmodel import select

class knowledge_dao:

    # 根据user_id 查询所有的知识向量库列表
    def knowledgeGetKnowledgeNameList(user_id:str):
        with get_db_session() as session:
            # 创建查询，选择所有符合条件的 knowledge_vector_name
            statement = select(Knowledge).where(Knowledge.user_id == user_id)
            results = session.exec(statement).all()  # 执行查询并获取所有结果
            # 提取 knowledge_vector_name
            knowledge_vector_names: List[str] = [result.knowledge_vector_name for result in results]
            return knowledge_vector_names

    # 根据 user_id 和 knowledge_vector_name 查询 knowledge_vector_path
    def knowledgeGetKnowledgeVectorPath(user_id:str,knowledge_vector_name:str):
        with get_db_session() as session:
            # 创建查询，选择所有符合条件的 knowledge_vector_name
            statement = select(Knowledge).where(
                Knowledge.user_id == user_id,
                Knowledge.knowledge_vector_name == knowledge_vector_name
            )
            result = session.exec(statement).first()  # 执行查询并获取所有结果
            # 提取 knowledge_vector_path
            knowledge_vector_path = result.knowledge_vector_path
            return knowledge_vector_path
