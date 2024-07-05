import argparse
from configs.model_config import *

parser = argparse.ArgumentParser(prog='langchina-HelpChat',
                                 description='About langchain-HelpChat, local knowledge based LLM with langchain ｜ '
                                    '基于本地知识库的 LLM 问答')
parser.add_argument('--no-remote-model', default=NO_REMOTE_MODEL, help='whether turn on remote model api')
parser.add_argument('--model', type=str, default=LLM_MODEL, help='Name of the model to load by default.')
parser.add_argument('--lora', type=str, help='Name of the LoRA to apply to the model by default.')
parser.add_argument("--model-dir", type=str, default=MODEL_DIR, help="Path to directory with all the models")
parser.add_argument("--lora-dir", type=str, default=LORA_DIR, help="Path to directory with all the loras")

args = parser.parse_args([])
# Generares dict with a default value for each argument
DEFAULT_ARGS = vars(args)
print(DEFAULT_ARGS)