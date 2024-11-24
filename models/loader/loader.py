# @Time  :2024/11/20 23:36
# @Author: yutian.li
# @Email : lyutian2020@qq.com

import configs.model_config as local_file_model_config
from typing import Optional, List, Dict, Tuple, Union,Any
from utils.utils import torch_gc
from utils.logger import logger
import sys
from pathlib import Path
from transformers import (AutoConfig, AutoModel, AutoModelForCausalLM,LlamaForCausalLM,
                            AutoTokenizer, LlamaTokenizer)
import time
import torch


class LoaderCheckPoint:
    '''
    model checkpoint加载类
    '''
    def __init__(self,params:dict=None):
        """
        模型初始化
        :param params:
        """
        self.model_path = None #某个大模型的本地路径
        self.model = None
        self.tokenizer = None
        self.params = params or {}
        self.no_remote_model = params.get('no_remote_model', False)
        self.model_name = params.get('model', '')
        self.vs_path = params.get('vs_path',local_file_model_config.VS_ROOT_PATH)
        self.lora = ""#params.get('lora', '')
        self.model_dir = params.get('model_dir', '') #本地大模型列表的目录路径
        self.lora_dir = ""#params.get('lora_dir', '')
        self.llm_model_info = local_file_model_config.llm_model_dict[self.model_name]
        # p tuning微调位置#TODO:待续
        self.ptuning_dir: str = ""
        # 是否使用p tuning v2#TODO:待续
        self.use_ptuning_v2: bool = False
        # 自定义设备网络
        self.device_map: Optional[Dict[str, int]] = None
        # 默认 cuda ，如果不支持cuda使用多卡， 如果不支持多卡 使用cpu
        self.llm_device = local_file_model_config.LLM_DEVICE

    def _load_model_config(self,model_name):
        checkpoint_dir = Path(f'{self.model_dir}/{model_name}')
        if self.model_path:
            checkpoint_dir = Path(f'{self.model_path}')
        model_config = AutoConfig.from_pretrained(checkpoint_dir, trust_remote_code=True)
        return model_config

    def _load_model(self,model_name):
        """
        加载自定义位置的model
        :param model_name:
        :return:
        """
        logger.info(f"Loading {model_name}...")
        t0 = time.time()
        checkpoint_dir = Path(f'{self.model_dir}/{model_name}')
        if self.model_path:
            checkpoint_dir = Path(f'{self.model_path}')
        #
        if 'chatglm' in model_name.lower():
            LoaderClass = AutoModel
        else:
            LoaderClass = AutoModelForCausalLM
        #
        # Load the model in Custom by default
        model = LoaderClass.from_pretrained(checkpoint_dir,
                                            low_cpu_mem_usage=True,
                                            trust_remote_code=True,
                                            torch_dtype=torch.float16,
                                            device_map="auto",
                                            offload_folder="D:/05_tmp")#.to(self.llm_device)
        # Loading the tokenizer
        if type(model) is LlamaForCausalLM:
            tokenizer = LlamaTokenizer.from_pretrained(checkpoint_dir, clean_up_tokenization_spaces=True)
            # Leaving this here until the LLaMA tokenizer gets figured out.
            # For some people this fixes things, for others it causes an error.
            try:
                tokenizer.eos_token_id = 2
                tokenizer.bos_token_id = 1
                tokenizer.pad_token_id = 0
            except Exception as e:
                print(e)
                pass
        else:
            tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir, trust_remote_code=True)
        logger.info(f"Loaded the model in {(time.time() - t0):.2f} seconds.")
        return model, tokenizer

    def set_model_path(self, model_path):
        self.model_path = model_path

    def unload_model(self):#删掉模型
        del self.model
        del self.tokenizer
        self.model = self.tokenizer = None
        torch_gc()

    def reload_model(self):
        self.unload_model()
        self.model_config = self._load_model_config(self.model_name)
        self.model, self.tokenizer = self._load_model(self.model_name)
        self.model = self.model.eval()

    def loaderLLM(self,llm_model: str = None, no_remote_model: bool = True) -> Any:#TODO:待完成
        if no_remote_model:
            self.no_remote_model = no_remote_model
            self.model_name=llm_model
            '''
            llm_model_dict = {
                    "chatglm-6b-int4-qe": {
                        "name": "chatglm-6b-int4-qe",
                        "pretrained_model_name": "THUDM/chatglm-6b-int4-qe",
                        "local_model_path": None,
                        "provides": "ChatGLM"
                    },..}
            '''
            self.llm_model_info = local_file_model_config.llm_model_dict[llm_model]
            self.model_path = self.llm_model_info["local_model_path"]
            #加载模型checkpoint（autoConfig、tokenizer、model）
            self.reload_model()
            #初始化模型
            provides_class = getattr(sys.modules['models'], self.llm_model_info['provides'])
            modelInsLLM = provides_class(checkPoint=self)
            return modelInsLLM
        else:#在线大模型api接口
            self.no_remote_model = no_remote_model
            self.model_name=llm_model
            self.llm_model_info = local_file_model_config.llm_model_dict[llm_model]
            logger.info(f"#### 使用在线大模型API接口, 使用的大模型bot={llm_model}")
            print(f"使用在线大模型API接口, 使用的大模型bot={llm_model}")
            #初始化模型
            #logger.info(f"sys.modules['models']={sys.modules['models']}")
            provides_class = getattr(sys.modules['models'], self.llm_model_info['provides'])
            modelInsLLM = provides_class(checkPoint=self)
            return modelInsLLM



loaderCheckPoint:LoaderCheckPoint=None