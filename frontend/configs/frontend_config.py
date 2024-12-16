# @Time  :2024/12/5 23:36
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import os
from dotenv import load_dotenv
from utils.logger import logger

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),".env_front")
logger.info(f"\ndotenv_path={dotenv_path}")
load_dotenv(dotenv_path, override=True)

VERSION="v2.0.0"
LOGO_IMG = "D:/03_PyCharmProjects/Langchain-HolaChat/imgs/chat_assistant_logo.png"
USER_LOGO_IMG = "D:/03_PyCharmProjects/Langchain-HolaChat/imgs/chat_assistant_icon4.png"
ASSISTANT_LOGO_IMG = "D:/03_PyCharmProjects/Langchain-HolaChat/imgs/chat_assistant_icon5.png"
HTTPX_DEFAULT_TIMEOUT=300

# 各服务器默认绑定host。如改为"0.0.0.0"需要修改下方所有XX_SERVER的host
# api.py server
BACKEND_SERVER = {
    "host": "http://127.0.0.1",
    "port": 8601,
}

# webui.py server
WEBUI_SERVER = {
    "host": "127.0.0.1",
    "port": 8501,
}

MODEL_LIST={
    "glm-4-flash":{
        "model_name":"glm-4-flash",
        "api_key":os.getenv("CHATGLM_API_KEY",""),
        "base_url":os.getenv("CHATGLM_URL",""),
    },
    "qwen-plus":{
        "model_name":"qwen-plus",
        "api_key":os.getenv("ALIBABA_API_KEY",""),
        "base_url":os.getenv("ALIBABA_URL",""),
    },
    "qwen-turbo":{
        "model_name":"qwen-turbo",
        "api_key":os.getenv("ALIBABA_API_KEY",""),
        "base_url":os.getenv("ALIBABA_URL",""),
    },
    "qwen2.5-72b-instruct":{
        "model_name":"qwen2.5-72b-instruct",
        "api_key":os.getenv("ALIBABA_API_KEY",""),
        "base_url":os.getenv("ALIBABA_URL",""),
    },
    "qwen2-0.5b-instruct":{
        "model_name":"qwen2-0.5b-instruct",
        "api_key":os.getenv("ALIBABA_API_KEY",""),
        "base_url":os.getenv("ALIBABA_URL",""),
    },
}
