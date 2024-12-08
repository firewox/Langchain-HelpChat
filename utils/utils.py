# @Time  :2024/11/20 22:43
# @Author: yutian.li
# @Email : lyutian2020@qq.com

import torch
from typing import Literal,Union,Dict,Any
import pydantic
from pydantic import BaseModel
from starlette.responses import RedirectResponse
from backend.configs.model_config import HTTPX_DEFAULT_TIMEOUT,LLM_DEVICE

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


def set_httpx_config(
        timeout: float = HTTPX_DEFAULT_TIMEOUT,
        proxy: Union[str, Dict] = None,
):
    '''
    设置httpx默认timeout。httpx默认timeout是5秒，在请求LLM回答时不够用。
    将本项目相关服务加入无代理列表，避免fastchat的服务器请求错误。(windows下无效)
    对于chatgpt等在线API，如要使用代理需要手动配置。搜索引擎的代理如何处置还需考虑。
    '''

    import httpx
    import os

    httpx._config.DEFAULT_TIMEOUT_CONFIG.connect = timeout
    httpx._config.DEFAULT_TIMEOUT_CONFIG.read = timeout
    httpx._config.DEFAULT_TIMEOUT_CONFIG.write = timeout

    # 在进程范围内设置系统级代理
    proxies = {}
    if isinstance(proxy, str):
        for n in ["http", "https", "all"]:
            proxies[n + "_proxy"] = proxy
    elif isinstance(proxy, dict):
        for n in ["http", "https", "all"]:
            if p := proxy.get(n):
                proxies[n + "_proxy"] = p
            elif p := proxy.get(n + "_proxy"):
                proxies[n + "_proxy"] = p

    for k, v in proxies.items():
        os.environ[k] = v

    # set host to bypass proxy
    no_proxy = [x.strip() for x in os.environ.get("no_proxy", "").split(",") if x.strip()]
    no_proxy += [
        # do not use proxy for locahost
        "http://127.0.0.1",
        "http://localhost",
    ]
    # do not use proxy for user deployed fastchat servers
    for x in [
        #fschat_controller_address(),
        #fschat_model_worker_address(),
        fschat_openai_api_address(),
    ]:
        host = ":".join(x.split(":")[:2])
        if host not in no_proxy:
            no_proxy.append(host)
    os.environ["NO_PROXY"] = ",".join(no_proxy)

    # TODO: 简单的清除系统代理不是个好的选择，影响太多。似乎修改代理服务器的bypass列表更好。
    # patch requests to use custom proxies instead of system settings
    def _get_proxies():
        return proxies

    import urllib.request
    urllib.request.getproxies = _get_proxies


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

# 从server_config中获取服务信息
def get_model_worker_config(model_name: str = None) -> dict:
    '''
    加载model worker的配置项。
    优先级:FSCHAT_MODEL_WORKERS[model_name] > ONLINE_LLM_MODEL[model_name] > FSCHAT_MODEL_WORKERS["default"]
    '''
    from backend.configs.model_config import llm_model_dict,ONLINE_LLM_MODEL,LOCAL_MODEL_PATH
    config = llm_model_dict.copy()
    config.update(ONLINE_LLM_MODEL)
    # 在线模型API
    if model_name in ONLINE_LLM_MODEL:
        config["online_api"] = True
    # 本地模型 LOCAL_MODEL_PATH
    if model_name in LOCAL_MODEL_PATH:
        config["model_path"] = LOCAL_MODEL_PATH("local_model_path")
        config["device"] = llm_device(LLM_DEVICE)
    return config

