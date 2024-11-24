# @Time  :2024/11/20 22:43
# @Author: yutian.li
# @Email : lyutian2020@qq.com

import torch

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