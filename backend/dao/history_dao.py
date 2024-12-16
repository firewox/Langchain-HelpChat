# @Time  :2024/12/15 15:47
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import datetime

from backend.utils.database import get_db_session
from backend.beans.model_beans import History
from sqlmodel import select
from utils.logger import logger
import json

class history_dao:

    # 查找历史记录
    def chatGetHistoryByUseridAndHistoryName(user_id:str,user_name:str,history_name:str):
        with get_db_session() as session:
            # 使用 SQLModel 的 select 查询
            statement = select(History).where(
                History.user_id == user_id,
                History.history_name == history_name
            )
            # 执行查询
            results = session.exec(statement).first()  # 使用 .first() 如果只想要一条记录
            logger.info(f"\n查询history历史记录results={results}")
            if results:
                return json.loads(results.history_content)
            else:
                logger.error(f"\n查找历史记录出错，没有在数据库中找到数据")
                return None

    # 查找所有的历史记录名称
    def chatGetHistoryNameList(user_id:str):
        with get_db_session() as session:
            # 使用 SQLModel 的 select 查询
            statement = select(History).where(
                History.user_id == user_id
            )
            # 执行查询
            results = session.exec(statement).all()  # 获取所有符合条件的记录
            # 处理查询结果
            resu=[]
            if results:
                for history_item in results:
                   resu.append(history_item.history_name)
                return resu
            else:
                return None

    # 保存历史聊天记录
    def chatSetHistoryByUseridAndHistoryName(user_id:str,history_name:str,messages:list):
        with get_db_session() as session:
            # 创建新的 History 实例
            new_history = History(
                user_id=user_id,
                history_name=history_name,
                history_content=str(json.dumps(messages,ensure_ascii=False)),
                created_time=datetime.datetime.now(),
                updated_time=datetime.datetime.now(),
                is_del=0,
            )

            # 添加实例到会话
            session.add(new_history)

            # 提交会话以保存到数据库
            try:
                session.commit()
                logger.info(f"\nHistory saved with ID: {new_history.hid}")
                return 1
            except Exception as e:
                session.rollback()  # 如果出现异常，回滚会话
                logger.info(f"\nError saving history: {e}")
                return 0

    # 根据user_id history_name 更新历史聊天记录 history_content，
    def chatUpdateHistoryByUseridAndHistoryName(user_id:str,history_name:str,messages:list):
        with get_db_session() as session:
            # 查询要更新的记录
            statement = select(History).where(
                History.user_id == user_id,
                History.history_name == history_name
            )

            # 执行查询
            result = session.exec(statement)
            history_record = result.first()  # 获取第一个匹配的记录

            # 提交会话以保存到数据库
            try:
                # 更新历史内容
                history_record.history_content = str(json.dumps(messages,ensure_ascii=False))
                # 提交事务
                session.add(history_record)  # 可以选择性地添加，更新已存在的记录不需要 add
                session.commit()  # 提交更改
                return 1
            except Exception as e:
                session.rollback()  # 如果出现异常，回滚会话
                logger.info(f"\nError saving history: {e}")
                return 0