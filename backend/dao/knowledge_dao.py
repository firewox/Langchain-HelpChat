# @Time  :2024/12/15 23:29
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from backend.utils_backend.database import get_db_session
from backend.beans.model_beans import *
from typing import List
from sqlmodel import select
from datetime import datetime
from utils.logger import logger

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

    # 插入一条知识向量库路径数据
    @classmethod
    def knowledgeInsertKnowledge(cls,
                                 knowledge_vector_name:str,
                                 user_id:str,
                                 knowledge_vector_path:str,
                                 embedding_model_name:str,
                                 remark:str,
                                 is_del=0,
                                 created_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                 updated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),):
        with get_db_session() as session:
            knowledge_data = Knowledge(user_id=user_id,
                                       knowledge_vector_name=knowledge_vector_name,
                                       knowledge_vector_path=knowledge_vector_path,
                                       embedding_model_name=embedding_model_name,
                                       remark=remark,
                                       is_del=is_del,
                                       created_time=created_time,
                                       updated_time=updated_time)
            session.add(knowledge_data)
            # 提交会话以保存到数据库
            try:
                session.commit()
                logger.info(f"\nknowledge_data saved with ID: {knowledge_data.klid}")
                return 1
            except Exception as e:
                session.rollback()  # 如果出现异常，回滚会话
                logger.info(f"\nError saving knowledge_data: {e}")
                return 0

    # 保存文件集
    @classmethod
    def knowledgeInsertFileDirToFileDirTable(cls,
                                             file_dir_path:str,
                                             file_dir_name:str,
                                             user_id:str,
                                             remark:str="",
                                             is_del:int=0,
                                             created_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                             updated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                       ):
        with get_db_session() as session:
            fd = FileToDir(file_dir_path=file_dir_path,
                          file_dir_name=file_dir_name,
                          user_id=user_id,
                          remark=remark,
                          is_del=is_del,
                          created_time=created_time,
                          updated_time=updated_time)
            session.add(fd)
            try:
                session.commit()
                logger.info(f"\n保存file_dir成功")
                return fd.file_dir_id
            except Exception as e:
                session.rollback()
                logger.error(f"\n保存file_dir出现错误，错误信息e={e}")
                return None

    # 根据 user_id and file_dir_name查询是否有对应的数据记录
    @classmethod
    def knowledgeGetFileDirByUserIdAndFileDirName(cls,user_id:str,file_dir_name:str):
        with get_db_session() as session:
            statement = select(FileToDir).where(
                FileToDir.user_id==user_id,
                FileToDir.file_dir_name==file_dir_name
            )
            result = session.exec(statement).first()  # 执行查询并获取所有结果
            if result:
                return result.file_dir_id
            return None

    # 插入文件信息
    @classmethod
    def knowledgeInsertFileToFileTable(cls,
                                       file_name:str,
                                       file_path:str,
                                       file_dir_id:int,
                                       remark="",
                                       is_del=0,
                                       created_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                       updated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
        with get_db_session() as session:
            fle = File(file_path=file_path,
                      file_name=file_name,
                      file_dir_id=file_dir_id,
                      remark=remark,
                      is_del=is_del,
                      created_time=created_time,
                      updated_time=updated_time)
            session.add(fle)
            try:
                session.commit()
                logger.info(f"\n保存file成功，file_name={file_name}")
                return fle
            except Exception as e:
                session.rollback()
                logger.error(f"\n保存file出现错误，错误信息e={e}")
                return None