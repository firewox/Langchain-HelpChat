# @Time  :2024/11/24 19:46
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from abc import ABC
from langchain.llms.base import LLM
from typing import Optional, List
from backend.models.loader.loader import LoaderCheckPoint
from backend.models.base.base import (BaseAnswer,
                                      AnswerResult)
from openai import OpenAI
import json

class OpenAI_Qwen(BaseAnswer,LLM,ABC):
    checkPoint: LoaderCheckPoint = None
    temperature:float=0.95
    max_tokens:int=2048
    api_key:str=""
    client_1: OpenAI=None
    stream_1:bool=False
    history_message: List[dict]=[]
    history_len:int=10
    base_url_1:str=""
    def __init__(self, checkPoint: LoaderCheckPoint = None):
        super().__init__()
        self.checkPoint = checkPoint
        # 流式对话开关
        self.stream_1=False
        # 采样温度，控制输出的随机性，必须为正数取值范围是：[0.0, 1.0]，默认值为0.95。
        self.temperature=0.95
        # 模型输出的最大token数，最大输出为 4095，默认值为 1024。
        self.max_tokens=2048
        # 模型遇到stop指定的字符时会停止生成。目前仅支持单个stop词，格式为["stop_word1"]。
        # self.stop=None
        # 连接大模型的api
        self.api_key=checkPoint.llm_model_info['api_key']
        #logger.info(f"self.api_key={self.api_key}")
        self.base_url_1 = checkPoint.llm_model_info['base_url']
        self.client_1=OpenAI(api_key=self.api_key,
                             base_url=self.base_url_1)
        # 历史记录
        '''
        history_message=[
            {"role": "system", "content": "你是一个乐于回答各种问题的小助手，你的任务是提供专业、准确、有洞察力的建议。"},
            {"role": "user", "content": "神印王座里的龙皓晨喜欢什么？"},
            {"role": "assistant", "content": "神印王座里的龙皓晨喜欢电脑游戏"},
            {"role": "user", "content": "神印王座里的龙皓晨喜欢什么"}]
        '''
        self.history_message=[{"role": "system", "content": "你是一个乐于回答各种问题的小助手，你的任务是提供专业、准确、有洞察力的建议。当用户问你是谁的时候，需要回答：我是一个乐于回答各种问题的小助手，我的任务是提供专业、准确、有洞察力的建议。"},
                              {"role": "user", "content": "你是谁"},
                              {"role": "assistant", "content": "我是一个乐于回答各种问题的小助手，我的任务是提供专业、准确、有洞察力的建议。"}]
    @property
    def _llm_type(self) -> str:
        return "ChatGLM-4-Flash"

    @property
    def _check_point(self) -> LoaderCheckPoint:
        return self.checkPoint

    @property
    def _history_len(self) -> int:
        return self.history_len

    def set_history_len(self, history_len: int = 10) -> None:
        self.history_len = history_len

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        if self.stream_1==False:
            response = self.client_1.chat.completions.create(
                model=self.checkPoint.model_name,  # 请填写您要调用的模型名称
                messages=self.history_message.append({"role": "user", "content": prompt}),
                stream=False,
            )
            '''
            response结构：
                {
                  "created": 1703487403,
                  "id": "8239375684858666781",
                  "model": "glm-4-plus",
                  "request_id": "8239375684858666781",
                  "choices": [
                      {
                          "finish_reason": "stop",
                          "index": 0,
                          "message": {
                              "content": "以AI绘蓝图 — 智谱AI，让创新的每一刻成为可能。",
                              "role": "assistant"
                          }
                      }
                  ],
                  "usage": {
                      "completion_tokens": 217,
                      "prompt_tokens": 31,
                      "total_tokens": 248
                  }
                }
            '''
            self.history_message.append({"role": "assistant", "content": response.choices[0].message.content})
            content=json.loads(response.model_dump_json())['choices'][0]['message'].get('content') #response.choices[0].message.content
            return content

    def generatorAnswer(self, prompt: str,
                        history: List[List[str]] = [],
                        streaming: bool = False):

        if self.stream_1:
            history += [[]]
            for inum, (stream_resp, _) in enumerate(self.checkPoint.model.stream_chat(
                    self.checkPoint.tokenizer,
                    prompt,
                    history=history[-self.history_len:-1] if self.history_len > 0 else [],
                    max_length=self.max_token,
                    temperature=self.temperature
            )):
                # self.checkPoint.clear_torch_cache()
                history[-1] = [prompt, stream_resp]
                answer_result = AnswerResult()
                answer_result.history = history
                answer_result.llm_output = {"answer": stream_resp}
                yield answer_result
        else:
            #logger.info(f"self.checkPoint.model_name=={self.checkPoint.model_name}")
            self.history_message.append({"role": "user", "content": prompt})
            #logger.info(f"self.history_message==={self.history_message}")
            response = self.client_1.chat.completions.create(
                model=self.checkPoint.model_name,  # 请填写您要调用的模型名称
                messages=self.history_message,
                stream=False,
            )
            '''
            response结构：
                {
                  "created": 1703487403,
                  "id": "8239375684858666781",
                  "model": "glm-4-plus",
                  "request_id": "8239375684858666781",
                  "choices": [
                      {
                          "finish_reason": "stop",
                          "index": 0,
                          "message": {
                              "content": "以AI绘蓝图 — 智谱AI，让创新的每一刻成为可能。",
                              "role": "assistant"
                          }
                      }
                  ],
                  "usage": {
                      "completion_tokens": 217,
                      "prompt_tokens": 31,
                      "total_tokens": 248
                  }
                }
            '''
            content = json.loads(response.model_dump_json())['choices'][0]['message'].get('content')
            self.history_message.append({"role": "assistant", "content": content})
            answer_result = AnswerResult()
            answer_result.history = self.history_message
            answer_result.llm_output = {"answer": content}
            #logger.info(f"content==={content}")
            yield answer_result

