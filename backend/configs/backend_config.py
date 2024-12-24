# @Time  :2024/11/20 23:03
# @Author: yutian.li
# @Email : lyutian2020@qq.com


import torch
import os
from dotenv import load_dotenv
from utils.logger import logger

VERSION="v2.0.0"

current_file_path = os.path.abspath(__file__)
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(current_file_path)), ".env_backend")
load_dotenv(dotenv_path,override=True)


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
SENTENCE_SIZE = 250
# 匹配后单段上下文长度
CHUNK_SIZE = 100
# return top-k text chunk from vector store
VECTOR_SEARCH_TOP_K = 50
# 知识检索内容相关度 Score, 数值范围约为0-1100，如果为0，则不生效
VECTOR_SEARCH_SCORE_THRESHOLD = 300
chunk_content=True

# 分词器的选择
TEXT_SPLITTER_NAME="nltk"
# nltk_data 是 Natural Language Toolkit (NLTK) 的一个数据包
NLTK_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nltk_data")


# Bing 搜索必备变量
# 使用 Bing 搜索需要使用 Bing Subscription Key
# 具体申请方式请见 https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/quickstarts/rest/python
BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"
BING_SUBSCRIPTION_KEY = ""

# Show reply with source text from input document
REPLY_WITH_SOURCE = False#True


# 后端运行在这个ip和端口上
BACKEND_SERVER = {
    "host": "127.0.0.1",
    "port": 8601,
}