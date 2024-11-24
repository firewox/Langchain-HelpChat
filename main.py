import configs.model_config as local_file_model_config
from models.loader.args import parser
from utils.logger import logger
import models.loader.loader as loader
from chains.local_doc_qa import LocalDocQA
import os

def main():
    args = parser.parse_args([])
    args_dict = vars(args)
    loader.loaderCheckPoint = loader.LoaderCheckPoint(args_dict)
    # 初始化LLM模型：qwen-turbo、glm-4-flash、qwen2-0.5b-instruct、qwen-plus
    llm_model_ins = loader.loaderCheckPoint.loaderLLM(llm_model="qwen-plus",no_remote_model=False)
    llm_model_ins.history_len = local_file_model_config.LLM_HISTORY_LEN

    # 初始化向量模型
    local_doc_qa = LocalDocQA()
    local_doc_qa.init_config(llm_model=llm_model_ins,
                          embedding_model=local_file_model_config.EMBEDDING_MODEL,
                          embedding_device=local_file_model_config.EMBEDDING_DEVICE,
                          top_k=local_file_model_config.VECTOR_SEARCH_TOP_K)

    vs_path = args.vs_path
    while not vs_path:
        filepath = input("请输入本地知识文件路径：")
        if not os.path.exists(filepath):
            print(f"本地知识文件路径不存在，请重新输入...")
            continue
        # 初始化知识向量库
        vs_path, _ = local_doc_qa.init_knowledge_vector_store(filepath,vs_path=vs_path)
    history = []
    while True:
        query = input("输入问题：")
        last_print_len = 0
        for resp, history in local_doc_qa.get_knowledge_based_answer(query=query,
                                                                     vs_path=vs_path,
                                                                     chat_history=history,
                                                                     streaming=local_file_model_config.STREAMING):
            if local_file_model_config.STREAMING:
                print(resp["result"][last_print_len:], end="", flush=True)
                last_print_len = len(resp["result"])
            else:
                print(resp["result"])
        if local_file_model_config.REPLY_WITH_SOURCE:
            #logger.info(f'resp["source_documents"]=={resp["source_documents"]}')
            source_text = [f"出处 [{inum + 1}] {os.path.split(doc.metadata['source'])[-1]}：{doc.page_content}\t"
                           f"相关度：{doc.metadata['score']}" for inum, doc in enumerate(resp["source_documents"])]
            print("\n" + "\n".join(source_text)) #resp["source_documents"]



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


