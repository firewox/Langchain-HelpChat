from typing import Optional, List, Dict, Tuple, Union
from configs.model_config import *
from pathlib import Path
from transformers import AutoConfig, AutoModel, AutoTokenizer, LlamaTokenizer, AutoModelForCausalLM, LlamaForCausalLM
import time
import gc
import json

class LoaderCheckPoint:
    '''
    model checkpoint加载类
    '''
    # 是否启动本地LLM
    no_remote_model: bool = False
    # 模型名称
    model_name: str = None
    tokenizer: object = None
    # 模型全路径
    model_path: str = None
    model: object = None
    model_config: object = None
    # lora名称
    lora_names: set = []
    # 本地模型存放的位置
    model_dir: str = None
    # lora存放位置
    lora_dir: str = None
    # p tuning微调位置
    ptuning_dir: str = None
    # 是否使用p tuning v2
    use_ptuning_v2: bool = False
    params: object = None
    # 自定义设备网络
    device_map: Optional[Dict[str, int]] = None
    # 默认 cuda ，如果不支持cuda使用多卡， 如果不支持多卡 使用cpu
    llm_device = LLM_DEVICE

    def __init__(self, params: dict=None):
        """
        模型初始化
        :param params:
        """
        self.model_path = None
        self.model = None
        self.tokenizer = None
        self.params = params or {}
        self.no_remote_model = params.get('no_remote_model', False)
        self.model_name = params.get('model', '')
        self.lora = params.get('lora', '')
        self.use_ptuning_v2 = params.get('use_ptuning_v2', False)
        self.model_dir = params.get('model_dir', '')
        self.lora_dir = params.get('lora_dir', '')
        self.ptuning_dir = params.get('ptuning_dir', 'ptuning-v2')

    def _load_model_config(self, model_name):
        checkpoint =Path(f"{self.model_dir}/{model_name}")
        if self.model_path:
            checkpoint=Path(f"{self.model_path}")
        elif not self.no_remote_model:
            checkpoint=model_name
        model_config = AutoConfig.from_pretrained(checkpoint, trust_remote_code=True)
        return model_config

    def _load_model(self, model_name):
        """
        加载自定义位置的model
        """
        print(f"Loading {model_name}...")
        t0 = time.time()
        checkpoint = Path(f'{self.model_dir}/{model_name}')
        if self.model_path:
            checkpoint = Path(f'{self.model_path}')
        elif not self.no_remote_model:
            checkpoint = model_name

        if 'chatglm' in model_name.lower():
            LoaderClass = AutoModel
        else:
            LoaderClass = AutoModelForCausalLM

        if not (self.llm_device.lower() == "cpu"): #使用显卡
            if torch.cuda.is_available() and self.llm_device.lower().startswith("cuda"):
                # 根据当前设备GPU数量决定是否进行多卡部署
                num_gpus = torch.cuda.device_count()
                if num_gpus < 2 and self.device_map is None:
                    model = (LoaderClass.from_pretrained(checkpoint,config=self.model_config,trust_remote_code=True).half().cuda())
                else:
                    from accelerate import dispatch_model
                    model = LoaderClass.from_pretrained(checkpoint,config=self.model_config,trust_remote_code=True).half()
                    # 可传入device_map自定义每张卡的部署情况
                    if self.device_map is None:
                        if 'chatglm' in model_name.lower():
                            self.device_map = self.chatglm_auto_configure_device_map(num_gpus)
                        else:
                            self.device_map = self.chatglm_auto_configure_device_map(num_gpus)
                    model = dispatch_model(model, device_map=self.device_map)
            else:
                model = (LoaderClass.from_pretrained(checkpoint,config=self.model_config,trust_remote_code=True)
                        .float()
                        .to(self.llm_device))
        else: #不使用显卡
            print("load CPU mode\n")
            params = {"low_cpu_mem_usage": True, "torch_dtype": torch.float32, "trust_remote_code": True}
            model = LoaderClass.from_pretrained(checkpoint, **params).to(self.llm_device, dtype=float)

        # Loading the tokenizer
        if type(model) is LlamaForCausalLM:
            tokenizer = LlamaTokenizer.from_pretrained(checkpoint, clean_up_tokenization_spaces=True)
            try:
                tokenizer.eos_token_id = 2
                tokenizer.bos_token_id = 1
                tokenizer.pad_token_id = 0
            except Exception as e:
                print(e)
                pass
        else:
            tokenizer = AutoTokenizer.from_pretrained(checkpoint, trust_remote_code=True)
        print(f"Loaded the model in {(time.time() - t0):.2f} seconds.")
        return model, tokenizer


    def chatglm_auto_configure_device_map(self, num_gpus:int) -> Dict[str,int]:
        # transformer.word_embeddings 占用1层
        # transformer.final_layernorm 和 lm_head 占用1层
        # transformer.layers 占用 28 层
        # 总共30层分配到num_gpus张卡上
        num_trans_layers = 28
        per_gpu_layers = 30 / num_gpus

        # bugfix: PEFT加载lora模型出现的层命名不同
        if self.lora:
            layer_prefix = 'base_model.model.transformer'
        else:
            layer_prefix = 'transformer'

        # bugfix: 在linux中调用torch.embedding传入的weight,input不在同一device上,导致RuntimeError
        # windows下 model.device 会被设置成 transformer.word_embeddings.device
        # linux下 model.device 会被设置成 lm_head.device
        # 在调用chat或者stream_chat时,input_ids会被放到model.device上
        # 如果transformer.word_embeddings.device和model.device不同,则会导致RuntimeError
        # 因此这里将transformer.word_embeddings,transformer.final_layernorm,lm_head都放到第一张卡上
        device_map = {f'{layer_prefix}.word_embeddings': 0,
                      f'{layer_prefix}.final_layernorm': 0, 'lm_head': 0,
                      f'base_model.model.lm_head': 0, }
        used = 2
        gpu_target = 0
        for i in range(num_trans_layers):
            if used >= per_gpu_layers:
                gpu_target += 1
                used = 0
            assert gpu_target < num_gpus
            device_map[f'{layer_prefix}.layers.{i}'] = gpu_target
            used += 1

        return device_map


    def _add_lora_to_model(self, lora_names):
        try:
            from peft import PeftModel
        except ImportError as exc:
            raise ValueError(
                "Could not import depend python package. "
                "Please install it with `pip install peft``pip install accelerate`."
            ) from exc
        # 目前加载的lora
        prior_set = set(self.lora_names)
        # 需要加载的
        added_set = set(lora_names) - prior_set
        # 删除的lora
        removed_set = prior_set - set(lora_names)
        self.lora_names = list(lora_names)

        # Nothing to do = skip.
        if len(added_set) == 0 and len(removed_set) == 0:
            return


    def clear_torch_cache(self):
        gc.collect()
        if self.llm_device.lower() != "cpu":
            if torch.has_mps:
                try:
                    from torch.mps import empty_cache
                    empty_cache()
                except Exception as e:
                    print(e)
            elif torch.has_cuda:
                device_id = "0" if torch.cuda.is_available() else None
                CUDA_DEVICE = f"{self.llm_device}:{device_id}" if device_id else self.llm_device
                with torch.cuda.device(CUDA_DEVICE):
                    torch.cuda.empty_cache()
                    torch.cuda.ipc_collect()
            else:
                print("未检测到 cuda，暂不支持清理显存")

    def unload_model(self):
        del self.model
        del self.tokenizer
        self.model = self.tokenizer = None
        self.clear_torch_cache()

    def set_model_path(self, model_path):
        self.model_path = model_path

    def reload_model(self):
        self.unload_model()
        self.model_config = self._load_model_config(self.model_name)
        if self.use_ptuning_v2:
            try:
                prefix_encoder_file = open(Path(f'{self.ptuning_dir}/config.json'), 'r')
                prefix_encoder_config = json.loads(prefix_encoder_file.read())
                prefix_encoder_file.close()
                self.model_config.pre_seq_len = prefix_encoder_config['pre_seq_len']
                self.model_config.prefix_projection = prefix_encoder_config['prefix_projection']
            except Exception as e:
                print("加载PrefixEncoder config.json失败")
        self.model, self.tokenizer = self._load_model(self.model_name)
        if self.lora:
            self._add_lora_to_model([self.lora])

        if self.use_ptuning_v2:
            try:
                prefix_state_dict = torch.load(Path(f'{self.ptuning_dir}/pytorch_model.bin'))
                new_prefix_state_dict = {}
                for k, v in prefix_state_dict.items():
                    if k.startswith("transformer.prefix_encoder."):
                        new_prefix_state_dict[k[len("transformer.prefix_encoder."):]] = v
                self.model.transformer.prefix_encoder.load_state_dict(new_prefix_state_dict)
                self.model.transformer.prefix_encoder.float()
            except Exception as e:
                print("加载PrefixEncoder模型参数失败")
        self.model = self.model.eval()