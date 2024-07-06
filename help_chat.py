import configs.model_config as model_config
from models.loader.args import parser
from models.loader.loader import LoaderCheckPoint
import models.shared as shared
from chains.local_doc_qa import LocalDocQA
import os

def main():
    args = parser.parse_args()
    args_dict = vars(args)
    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    llm_model_ins = shared.loaderLLM()
    llm_model_ins.history_len = model_config.LLM_HISTORY_LEN

    # 初始化LLM模型、向量模型
    local_doc_qa = LocalDocQA()
    local_doc_qa.init_cfg(llm_model=llm_model_ins,
                          embedding_model=model_config.EMBEDDING_MODEL,
                          embedding_device=model_config.EMBEDDING_DEVICE,
                          top_k=model_config.VECTOR_SEARCH_TOP_K)
    vs_path = None
    while not vs_path:
        filepath = input("请输入本地知识文件路径：")
        if not filepath:
            continue
        # 初始化知识向量库
        vs_path, _ = local_doc_qa.init_knowledge_vector_store(filepath)
    history = []
    while True:
        query = input("输入问题：")
        last_print_len = 0
        for resp, history in local_doc_qa.get_knowledge_based_answer(query=query, vs_path=vs_path, chat_history=history,streaming=model_config.STREAMING):
            if model_config.STREAMING:
                print(resp["result"][last_print_len:], end="", flush=True)
                last_print_len = len(resp["result"])
            else:
                print(resp["result"])
        if model_config.REPLY_WITH_SOURCE:
            source_text = [f"""出处 [{inum + 1}] {os.path.split(doc.metadata['source'])[-1]}：\n\n{doc.page_content}\n\n""" 
                           f"""相关度：{doc.metadata['score']}\n\n""" for inum, doc in enumerate(resp["source_documents"])]
            print("\n\n" + "\n\n".join(source_text))


if __name__ == '__main__':
    main()

