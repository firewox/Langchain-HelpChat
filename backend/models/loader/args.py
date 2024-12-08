# @Time  :2024/11/20 22:49
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import argparse
from backend.configs.model_config import *

parser = argparse.ArgumentParser(prog='Langchain-HolaChat',
                        description="About langchain-HolaChat, local knowledge based LLM with langchain ｜"
                                    "基于本地知识库的 LLM 问答")
parser.add_argument('--model', type=str, default=LLM_MODEL, help='Name of the model to load by default.')
parser.add_argument("--model-dir", type=str, default=MODEL_DIR, help="Path to directory with all the models")
# parser.add_argument("--vs_path", type=str, default="D:/03_PyCharmProjects/Langchain-HolaChat/vector_store/shen_yin_wang_zuo_FAISS_", help="Path to directory with vector db")
parser.add_argument("--vs_path", type=str, default="D:/03_PyCharmProjects/Langchain-HolaChat/vector_store/shen_yin_wang_zuo_FAISS_text2vec-base-chinese-paraphrase_", help="Path to directory with vector db")
parser.add_argument('--no-remote-model', default=NO_REMOTE_MODEL, help='whether turn on remote model api')
parser.add_argument(
    "-o",
    "--openai_api",
    action="store_true",
    help="run fastchat's controller/ servers",
    dest="llm_api",
)
parser.add_argument(
    "--chat_api",
    action="store_true",
    help="run api.py server",
    dest="api",
)
parser.add_argument(
    "-w",
    "--webui",
    action="store_true",
    help="run webui.py server",
    dest="webui",
)

args = parser.parse_args([])
DEFAULT_ARGS = vars(args)
#print(DEFAULT_ARGS)