# HelpChat，基于本地知识库的 LLM 实现
## 介绍

🤖️ 利用 [langchain](https://github.com/hwchase17/langchain) 思想实现，基于本地知识库建立一套对中文场景与开源模型支持友好、可离线运行的知识库问答解决方案。

💡 受 [Langchain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat) 项目启发，采建立了全流程可使用 LLM 模型实现的本地知识库问答应用。目前支持了chatGLM 、Qwen 等开源大模型。

🚩 本项目中 Embedding 默认选用的是 [GanymedeNil/text2vec-base-chinese](https://huggingface.co/GanymedeNil/text2vec-base-chinese/tree/main) ，LLM 默认选用的是 [ChatGLM-6B](https://github.com/THUDM/ChatGLM-6B) 。依托上述模型，本项目可实现使用**开源**模型**离线私有部署**。

🖥️ 本项目主要有以下过程:
- **读取文本** 
    - [X] 读取md文档。
    - [X] 读取txt。
    - [X] 读取pdf文档
        - 使用 PaddleOCR识别文档内容。
    - [X] 读取jpg、png文件
        - 使用 PaddleOCR识别图片内容。
    - [X] 读取其他类型文档。
        - 使用 Langchain 读取其他非结构化文件内容。
- **文本分割**
      - 按照中文常见的分割符分割文本内容。
- **文本向量化**
    - **知识库文件内容向量化**
        - 使用加载向量模型，将doc知识文档内容转为向量存放库中。
    - **问句向量化**
        - 使用向量模型将query也向量化。
- **在文本向量中匹配出与问句向量最相似的`top k`个。**
- **匹配出的文本作为上下文和问题一起添加到`prompt`中。**
- **提交给`LLM`生成回答。**

## 硬件需求

- ChatGLM-6B 模型硬件需求

    | **量化等级**   | **最低 GPU 显存**（推理） | **最低 GPU 显存**（高效参数微调） |
    | -------------- | ------------------------- | --------------------------------- |
    | FP16（无量化） | 13 GB                     | 14 GB                             |
    | INT8           | 8 GB                     | 9 GB                             |
    | INT4           | 6 GB                      | 7 GB                              |

- Embedding 模型硬件需求
  
  本项目中选用的 Embedding 模型 [GanymedeNil/text2vec-base-chinese](https://huggingface.co/GanymedeNil/text2vec-base-chinese/tree/main) 可修改为在 CPU 中运行。


## 开发部署
### 1. 使用命令行交互
执行 [cli_demo.py](cli_demo.py) 脚本体验**命令行交互**：
```shell
$ python help_chat.py
```


## 路线图

- [ ] Langchain 应用
    - [x] 接入非结构化文档（已支持 md、pdf、docx、txt 文件格式）
    - [x] jpg 与 png 格式图片的 OCR 文字识别
    - [x] 搜索引擎接入
    - [ ] 本地网页接入
    - [ ] 结构化数据接入（如 csv、Excel、SQL 等）
    - [ ] 知识图谱/图数据库接入
    - [ ] Agent 实现
- [x] 增加更多 LLM 模型支持
    - [x] [THUDM/chatglm-6b](https://huggingface.co/THUDM/chatglm-6b)
    - [x] [THUDM/chatglm-6b-int4](https://huggingface.co/THUDM/chatglm-6b-int4)
    - [x] [THUDM/chatglm-6b-int4-qe](https://huggingface.co/THUDM/chatglm-6b-int4-qe)
- [ ] 增加更多 Embedding 模型支持
    - [x] [shibing624/text2vec-base-chinese](https://huggingface.co/shibing624/text2vec-base-chinese)
    - [x] [GanymedeNil/text2vec-large-chinese](https://huggingface.co/GanymedeNil/text2vec-large-chinese)
- [ ] Web UI
    - [ ] 基于 gradio 实现 Web UI DEMO
    - [ ] 基于 streamlit 实现 Web UI DEMO
    - [ ] 引用标注
    - [ ] 增加知识库管理
        - [ ] 选择知识库开始问答
        - [ ] 上传文件/文件夹至知识库
        - [ ] 知识库测试
        - [ ] 删除知识库中文件
    - [ ] 支持搜索引擎问答
- [ ] 增加 API 支持
    - [ ] 利用 fastapi 实现 API 部署方式
    - [ ] 实现调用 API 的 Web UI Demo

