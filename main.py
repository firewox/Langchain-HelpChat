import configs.model_config as model_config
from models.loader.args import parser
from models.loader.loader import LoaderCheckPoint
import models.shared as shared


def main():
    args = parser.parse_args()
    args_dict = vars(args)
    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    llm_model_ins = shared.loaderLLM()
    llm_model_ins.history_len = model_config.LLM_HISTORY_LEN

    #加载
    local_doc_qa = shared.LocalDocQA()
    local_doc_qa.init_cfg(llm_model=llm_model_ins,
                          embedding_model=model_config.EMBEDDING_MODEL,
                          embedding_device=model_config.EMBEDDING_DEVICE,
                          top_k=model_config.VECTOR_SEARCH_TOP_K)
    vs_path = None
    while not vs_path:
        filepath = input("请输入本地知识文件路径：")
        if not filepath:
            continue
        vs_path, _ = local_doc_qa.init_knowledge_vector_store(filepath)







if __name__ == '__main__':
    main()

