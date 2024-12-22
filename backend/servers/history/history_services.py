# @Time  :2024/12/5 20:14
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import datetime
from backend.dao.history_dao import history_dao



class history_services:
    # 处理查询聊天历史记录的逻辑
    def chatGetHistoryByUsernameAndHistoryName(user_id:str,user_name:str,history_name:str):
        messages = history_dao.chatGetHistoryByUseridAndHistoryName(user_id=user_id,user_name=user_name,history_name=history_name)
        return messages

    # 根据user id 创建新的聊天会话名称
    def chatCreateNewDialogueByUserId(user_id:str,messages:list):
        history_name = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"会话"
        history_dao.chatCreateNewDialogueByUserId(user_id=user_id,history_name=history_name,messages=messages)
        return history_name

    # 查询所有历史记录的名字列表
    def chatGetHistoryNameList(user_id:str):
        history_name_list = history_dao.chatGetHistoryNameList(user_id=user_id)
        return history_name_list

    # 保存历史记录
    def chatSetHistoryByUseridAndHistoryName(user_id:str,history_name:str,messages:list):
        response = history_services.chatGetHistoryByUsernameAndHistoryName(user_id=user_id,history_name=history_name,user_name="")
        if response is not None:#该历史记录存在，只更新 history_content
            flag = history_dao.chatUpdateHistoryByUseridAndHistoryName(user_id=user_id,history_name=history_name,messages=messages)
        else:# 该历史记录不存在，保存 history_content
            flag = history_dao.chatSetHistoryByUseridAndHistoryName(user_id=user_id,history_name=history_name,messages=messages)
        return flag

