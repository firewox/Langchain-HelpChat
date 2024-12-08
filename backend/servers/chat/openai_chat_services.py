# @Time  :2024/12/5 20:14
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from pydantic import BaseModel
from typing import List
from openai import AsyncOpenAI,OpenAI
from utils.logger import logger
from typing import Dict
from utils.utils import get_model_worker_config
from fastapi.responses import StreamingResponse
from backend.configs.model_config import LLM_MODEL,ONLINE_LLM_MODEL


class OpenAiMessage(BaseModel):
    role: str = "user"
    content: str = "你好"

class OpenAiChatMsgIn(BaseModel):
    model: str = LLM_MODEL
    messages: List[OpenAiMessage]
    temperature: float = 0.7
    n: int = 1
    max_tokens: int = None
    stop: List[str] = []
    stream: bool = False
    presence_penalty: int = 0
    frequency_penalty: int = 0

async def openai_chat(msg: OpenAiChatMsgIn):
    config = get_model_worker_config(msg.model)
    async def get_response(msg):
        data = msg.dict()
        try:
            client = AsyncOpenAI(api_key=config.get("api_key",""),base_url=config.get("base_url",""))
            response = await client.chat.completions.create(**data)
            if msg.stream:
                async for data in response:
                    if choices := data.choices:
                        if chunk := choices[0].delta.content:
                            print(chunk, end="", flush=True)
                            yield chunk
            else:
                if response.choices:
                    answer = response.choices[0].message.content
                    print(answer)
                    yield(answer)
        except Exception as e:
            msg = f"获取ChatCompletion时出错：{e}"
            logger.error(f'{e.__class__.__name__}: {msg}')
    return StreamingResponse(get_response(msg), media_type='text/event-stream',)

async def openai_chat_v1(msg:Dict):
    config = get_model_worker_config(msg.get("model"))
    async def get_response(msg):
        data = msg
        try:
            logger.info(data)
            logger.info(f"config={config}")
            client = AsyncOpenAI(api_key=config.get(msg.get("model")).get("api_key",""),base_url=config.get(msg.get("model")).get("base_url",""))
            response = await client.chat.completions.create(**data)
            #logger.info(f'msg.get("stream",True)={msg.get("stream")}')
            if msg.get("stream",True):
                #logger.info("测试")
                async for data in response:
                    if choices := data.choices:
                        if chunk := choices[0].delta.content:
                            #print(chunk, end="", flush=True)
                            yield chunk
            else:
                if response.choices:
                    answer = response.choices[0].message.content
                    #print(answer)
                    yield(answer)
        except Exception as e:
            msg = f"获取ChatCompletion时出错：{e}"
            logger.error(f'{e.__class__.__name__}: {msg}')
    return get_response(msg)

def openai_chat_v2(model_name:str, messages:List[Dict]):
    msg = {"model":model_name,
           "messages":messages,
           "temperature":0.7,
           "max_tokens":None,
           "stream":True}
    config = get_model_worker_config(msg.get("model"))
    # Set OpenAI API key
    client = OpenAI(api_key=config.get(msg.get("model")).get("api_key",""),base_url=config.get(msg.get("model")).get("base_url",""))
    stream = client.chat.completions.create(
        model=msg.get("model"),
        messages=messages,
        stream=True,
    )
    return stream



class openai_chat_services:
    # 处理查询聊天历史记录的逻辑
    def chatGetHistoryByUsernameAndHistoryName(user_name:str,history_name:str):
        if user_name and history_name:
            logger.info(f"根据username和history_name查询历史聊天记录")
        messages = [{"role":"user","content":"你是谁"},{"role":"assistant","content":"我是小助帮手"}]
        return messages

    # 处理大模型聊天的请求
    def chatGetChat(user_name:str,model_name:str,messages:List):
        msg = {"model":model_name,
               "messages":messages,
               "temperature":0.7,
               "max_tokens":None,
               "stream":True}
        config = get_model_worker_config(msg.get("model"))
        # Set OpenAI API key
        logger.info(f"config={config.get(msg.get('model'))}")
        logger.info(f"msg={msg.get('model')}")
        client = OpenAI(api_key=config.get(msg.get("model")).get("api_key",""), base_url=config.get(msg.get("model")).get("base_url",""))
        stream = client.chat.completions.create(
            model=msg.get("model"),
            messages=messages,
            stream=True,
        )
        return stream

    # 查询可用的大模型列表
    def chatGetAvailableModelList(user_name:str):
        model_dict = ONLINE_LLM_MODEL.copy()
        return list(model_dict.keys())

    # 查询所有历史记录的名字列表
    def chatGetHistoryNameList(user_name:str):
        history_name_list = ['default']
        return history_name_list

