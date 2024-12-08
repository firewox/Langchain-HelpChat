# @Time  :2024/11/20 23:03
# @Author: yutian.li
# @Email : lyutian2020@qq.com


import torch
import os
from dotenv import load_dotenv
from utils.logger import logger

VERSION="v0.0.3"

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
dotenv_path = os.path.join(current_directory, ".env")
#logger.info(f"current_directory=={current_directory}")
load_dotenv(dotenv_path)


#文本向量模型
embedding_model_dict = {
    "text2vec-base-chinese-paraphrase": "D:/LargeModel_checkpoints/4_models/2_tet2vector/shibing624/text2vec-base-chinese-paraphrase",
    "text2vec-base-chinese": "D:/LargeModel_checkpoints/4_models/2_tet2vector/shibing624/text2vec-base-chinese",#"shibing624/text2vec-base-chinese",
    "text2vec-large-chinese": "GanymedeNil/text2vec-large-chinese",
}

# Embedding model name
EMBEDDING_MODEL = "text2vec-base-chinese-paraphrase"#"text2vec-base"

# Embedding running device
EMBEDDING_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

#LLM大模型
# llm_model_dict 处理了loader的一些预设行为，如加载位置，模型名称，模型处理器实例
# 目前加入了chatglm-6b系列的模型，@TODO:加入Qwen系列的模型，加入glm-4-falsh api
llm_model_dict = {
    "glm-4-flash": {
        "name": "glm-4-flash",
        "pretrained_model_name": os.getenv("GLM_4_FLASH_API_KEY",""),
        "local_model_path": os.getenv("GLM_4_FLASH_API_KEY",""),
        "api_key":os.getenv("GLM_4_FLASH_API_KEY",""),
        "base_url":os.getenv("CHATGLM_BASE_URL",""),
        "provides": "ChatGLM_Flash"
    },
    "qwen-turbo": {
        "name": "qwen-turbo",
        "pretrained_model_name": os.getenv("QWEN_API_KEY",""),
        "local_model_path": os.getenv("QWEN_API_KEY",""),
        "api_key":os.getenv("QWEN_API_KEY",""),
        "base_url":os.getenv("QWEN_BASE_URL",""),
        "provides": "OpenAI_Qwen"
    },
    "qwen2-0.5b-instruct": {
        "name": "qwen2-0.5b-instruct",
        "pretrained_model_name": os.getenv("QWEN_API_KEY",""),
        "local_model_path": os.getenv("QWEN_API_KEY",""),
        "api_key":os.getenv("QWEN_API_KEY",""),
        "base_url":os.getenv("QWEN_BASE_URL",""),
        "provides": "OpenAI_Qwen"
    },
    "qwen-plus": {
        "name": "qwen-plus",
        "pretrained_model_name": os.getenv("QWEN_API_KEY",""),
        "local_model_path": os.getenv("QWEN_API_KEY",""),
        "api_key":os.getenv("QWEN_API_KEY",""),
        "base_url":os.getenv("QWEN_BASE_URL",""),
        "provides": "OpenAI_Qwen"
    },
    "qwen2.5-72b-instruct": {
        "name": "qwen2.5-72b-instruct",
        "pretrained_model_name": os.getenv("QWEN_API_KEY",""),
        "local_model_path": os.getenv("QWEN_API_KEY",""),
        "api_key":os.getenv("QWEN_API_KEY",""),
        "base_url":os.getenv("QWEN_BASE_URL",""),
        "provides": "OpenAI_Qwen"
    },
    "chatglm-6b-int4": {
        "name": "chatglm-6b-int4",
        "pretrained_model_name": "THUDM/chatglm-6b-int4",
        "local_model_path": None,
        "provides": "ChatGLM"
    },
    "chatglm-6b": {
        "name": "chatglm-6b",
        "pretrained_model_name": "THUDM/chatglm-6b",
        "local_model_path": "D:\\LargeModel_checkpoints\\4_models\\0_chatglm\\chatglm2-6b",
        "provides": "ChatGLM"
    },
}

# LLM 名称
LLM_MODEL = "glm-4-flash"#"qwen-plus"#
#模型使用本地模型
NO_REMOTE_MODEL = False
# 本地模型存放的位置#TODO:修改模型位置
MODEL_DIR = "D:\\LargeModel_checkpoints\\4_models\\0_chatglm\\"#"model/"
# 本地lora存放的位置#TODO:修改lora权重位置
LORA_DIR = ""#"loras/"
# LLM lora path，默认为空，如果有请直接指定文件夹路径
LLM_LORA_PATH = ""
USE_LORA = "False"#True if LLM_LORA_PATH else False
# Use p-tuning-v2 PrefixEncoder#TODO:后续加入
#USE_PTUNING_V2 = False


# LLM running device
LLM_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# LLM streaming reponse默认不开启
STREAMING = False
# LLM 上下文历史对话长度history length
LLM_HISTORY_LEN = 3
# 基于上下文的prompt模版
PROMPT_TEMPLATE = """已知信息：
{context} 

根据上述已知信息，简洁和专业的来回答用户的问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题” 或 “没有提供足够的相关信息”，不允许在答案中添加编造成分，答案请使用中文。 问题是：{question}"""
PROMPT_TEMPLATE_FLAG="""根据上述已知信息，简洁和专业的来回答用户的问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题” 或 “没有提供足够的相关信息”，不允许在答案中添加编造成分，答案请使用中文。 问题是："""


# vector_store路径

# __file__ = "d:\\lyt\\"
# 初始化知识向量库，将知识向量库信息保存到 VS_ROOT_PATH
VS_ROOT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vector_store")
#知识库原始文件内容路径
UPLOAD_ROOT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "content")



# 缓存知识库数量
CACHED_VS_NUM = 1
# 文本分句长度
SENTENCE_SIZE = 100
# 匹配后单段上下文长度
CHUNK_SIZE = 100
# return top-k text chunk from vector store
VECTOR_SEARCH_TOP_K = 5
# 知识检索内容相关度 Score, 数值范围约为0-1100，如果为0，则不生效
VECTOR_SEARCH_SCORE_THRESHOLD = 300
chunk_content=True

# 分词器的选择
TEXT_SPLITTER_NAME="nltk"
# nltk_data 是 Natural Language Toolkit (NLTK) 的一个数据包
NLTK_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nltk_data")


# 是否开启跨域，默认为False，如果需要开启，请设置为True
OPEN_CROSS_DOMAIN = False

# Bing 搜索必备变量
# 使用 Bing 搜索需要使用 Bing Subscription Key
# 具体申请方式请见 https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/quickstarts/rest/python
BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"
BING_SUBSCRIPTION_KEY = ""

# Show reply with source text from input document
REPLY_WITH_SOURCE = False#True

# httpx 请求默认超时时间（秒）。如果加载模型或对话较慢，出现超时错误，可以适当加大该值。
HTTPX_DEFAULT_TIMEOUT = 300.0

LOCAL_MODEL_PATH = {
    "chatglm-6b-int4": {
    "name": "chatglm-6b-int4",
    "pretrained_model_name": "THUDM/chatglm-6b-int4",
    "local_model_path": None,
    "provides": "ChatGLM"
    },
    "chatglm-6b": {
        "name": "chatglm-6b",
        "pretrained_model_name": "THUDM/chatglm-6b",
        "local_model_path": "D:\\LargeModel_checkpoints\\4_models\\0_chatglm\\chatglm2-6b",
        "provides": "ChatGLM"
    },
}

ONLINE_LLM_MODEL = {
    # 线上模型。请在server_config中为每个在线API设置不同的端口
    # 具体注册及api key获取请前往 http://open.bigmodel.cn
    "glm-4-flash": {
        "api_key":os.getenv("GLM_4_FLASH_API_KEY",""),
        "version": "glm-4-flash",  # 可选包括 "chatglm_lite", "chatglm_std", "chatglm_pro"
        "base_url":os.getenv("CHATGLM_BASE_URL",""),
        "provider": "ChatGLMWorker",
    },
    # 阿里云通义千问 API，文档参考 https://help.aliyun.com/zh/dashscope/developer-reference/api-details
    "qwen-turbo": {
        "version": "qwen-turbo",  # 可选包括 "qwen-turbo", "qwen-plus"
        "api_key":os.getenv("QWEN_API_KEY",""),
        "base_url":os.getenv("QWEN_BASE_URL",""),
        "provider": "QwenWorker",
    }#，qwen-plus，qwen2.5-72b-instruct
    ,
    # 阿里云通义千问 API，文档参考 https://help.aliyun.com/zh/dashscope/developer-reference/api-details
    "qwen2-0.5b-instruct": {
        "version": "qwen2-0.5b-instruct",  # 可选包括 "qwen-turbo", "qwen-plus"
        "api_key":os.getenv("QWEN_API_KEY",""),
        "base_url":os.getenv("QWEN_BASE_URL",""),
        "provider": "QwenWorker",
    }#qwen2-0.5b-instruct，qwen-plus，qwen2.5-72b-instruct
    ,
    # 阿里云通义千问 API，文档参考 https://help.aliyun.com/zh/dashscope/developer-reference/api-details
    "qwen-plus": {
        "version": "qwen-plus",  # 可选包括 "qwen-turbo", "qwen-plus"
        "api_key":os.getenv("QWEN_API_KEY",""),
        "base_url":os.getenv("QWEN_BASE_URL",""),
        "provider": "QwenWorker",
    }#
    ,
    # 阿里云通义千问 API，文档参考 https://help.aliyun.com/zh/dashscope/developer-reference/api-details
    "qwen2.5-72b-instruct": {
        "version": "qwen2.5-72b-instruct",  # 可选包括 "qwen-turbo", "qwen-plus"
        "api_key":os.getenv("QWEN_API_KEY",""),
        "base_url":os.getenv("QWEN_BASE_URL",""),
        "provider": "QwenWorker",
    }#
}

# 各服务器默认绑定host。如改为"0.0.0.0"需要修改下方所有XX_SERVER的host
DEFAULT_BIND_HOST = "127.0.0.1"

# api.py server
API_SERVER = {
    "host": DEFAULT_BIND_HOST,
    "port": 8080,
}

# webui.py server
WEBUI_SERVER = {
    "host": DEFAULT_BIND_HOST,
    "port": 8501,
}