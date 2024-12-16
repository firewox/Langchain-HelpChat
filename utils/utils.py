# @Time  :2024/11/20 22:43
# @Author: yutian.li
# @Email : lyutian2020@qq.com

import torch
from typing import Literal,Union,Dict,Any
import pydantic
from pydantic import BaseModel

def torch_gc():
    if torch.cuda.is_available():
        # with torch.cuda.device(DEVICE):
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    elif torch.backends.mps.is_available():
        try:
            from torch.mps import empty_cache
            empty_cache()
        except Exception as e:
            print(e)
            print("清理 torch 产生的内存占用失败！")

# 自动检查torch可用的设备。分布式部署时，不运行LLM的机器上可以不装torch
def detect_device() -> Literal["cuda", "mps", "cpu"]:
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
    except:
        pass
    return "cpu"

def llm_device(device: str = None):
    if device is None or device not in ['cuda','cpu','mps']:
        return detect_device()
    return device

def embedding_device(device: str = None) -> Literal["cuda", "mps", "cpu"]:
    if device is None or device not in ['cuda','cpu','mps']:
        return detect_device()
    return device

def fschat_openai_api_address() -> str:
    #TODO 待续
    #from backend.configs.model_config import FSCHAT_OPENAI_API
    FSCHAT_OPENAI_API = {
        "host": "127.0.0.1",
        "port": 20000,
    }
    host = FSCHAT_OPENAI_API["host"]
    if host == "0.0.0.0":
        host = "127.0.0.1"
    port = FSCHAT_OPENAI_API["port"]
    return f"http://{host}:{port}/v1"

def api_address() -> str:
    #TODO 待续
    #from backend.configs.model_config import API_SERVER
    API_SERVER = {
        "host": "127.0.0.1",
        "port": 7861,
    }
    host = API_SERVER["host"]
    if host == "0.0.0.0":
        host = "127.0.0.1"
    port = API_SERVER["port"]
    return f"http://{host}:{port}"

def webui_address() -> str:
    #TODO 待续
    #from backend.configs.model_config import WEBUI_SERVER
    WEBUI_SERVER = {
        "host": "127.0.0.1",
        "port": 8501,
    }
    host = WEBUI_SERVER["host"]
    port = WEBUI_SERVER["port"]
    return f"http://{host}:{port}"




class BaseResponse(BaseModel):
    code: int = pydantic.Field(200, description="API status code")
    msg: str = pydantic.Field("success", description="API status message")
    data: Any = pydantic.Field(None, description="API data")

    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
            }
        }

