# @Time  :2024/11/21 0:58
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import configs.model_config as local_file_model_config
from models.base.base import BaseAnswer
from typing import List,Tuple
from langchain.docstore.document import Document
import os
from utils.logger import logger
from tqdm import tqdm
from utils.utils import torch_gc
from datetime import datetime
from langchain.vectorstores import FAISS
from langchain.document_loaders.text import TextLoader
from utils.chinese_text_splitter import ChineseTextSplitter
from utils.pdf_loader import UnstructuredPaddlePDFLoader
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from utils.image_loader import UnstructuredPaddleImageLoader
from functools import lru_cache
from pypinyin import lazy_pinyin
import numpy as np


# patch HuggingFaceEmbeddings to make it hashable
def _embeddings_hash(self):
    return hash(self.model_name)
HuggingFaceEmbeddings.__hash__ = _embeddings_hash

def seperate_list(ls: List[int]) -> List[List[int]]:
    lists = []
    ls1 = [ls[0]]
    for i in range(1, len(ls)):
        if ls[i - 1] + 1 == ls[i]:
            ls1.append(ls[i])
        else:
            lists.append(ls1)
            ls1 = [ls[i]]
    lists.append(ls1)
    return lists

# TODO，这个是本地定义的相似度匹配的函数，后续可以换成 langchain 官方默认的 similarity_search_with_score_by_vector函数
# 用户问题和本地知识向量库中的知识向量做相似度匹配
## from langchain.vectorstores import FAISS中默认使用的是欧几里得距离（L2距离）计算query向量和知识向量之间的相似度
def similarity_search_with_score_by_vector(self,
                                           embedding: List[float],
                                           k: int = 4) -> List[Tuple[Document, float]]:
    scores, indices = self.index.search(np.array([embedding], dtype=np.float32), k)
    docs = []
    id_set = set()
    store_len = len(self.index_to_docstore_id)
    for j, i in enumerate(indices[0]):
        if i == -1 or 0 < self.score_threshold < scores[0][j]:
            # This happens when not enough docs are returned.
            continue
        _id = self.index_to_docstore_id[i]
        doc = self.docstore.search(_id)
        if not self.chunk_content:
            if not isinstance(doc, Document):
                raise ValueError(f"Could not find document for id {_id}, got {doc}")
            doc.metadata["score"] = int(scores[0][j])
            docs.append(doc)
            continue
        id_set.add(i)
        docs_len = len(doc.page_content)
        for k in range(1, max(i, store_len - i)):
            break_flag = False
            for l in [i + k, i - k]:
                if 0 <= l < len(self.index_to_docstore_id):
                    _id0 = self.index_to_docstore_id[l]
                    doc0 = self.docstore.search(_id0)
                    if docs_len + len(doc0.page_content) > self.chunk_size:
                        break_flag = True
                        break
                    elif doc0.metadata["source"] == doc.metadata["source"]:
                        docs_len += len(doc0.page_content)
                        id_set.add(l)
            if break_flag:
                break
    if not self.chunk_content:
        return docs
    if len(id_set) == 0 and self.score_threshold > 0:
        return []
    id_list = sorted(list(id_set))
    id_lists = seperate_list(id_list)
    for id_seq in id_lists:
        for id in id_seq:
            if id == id_seq[0]:
                _id = self.index_to_docstore_id[id]
                doc = self.docstore.search(_id)
            else:
                _id0 = self.index_to_docstore_id[id]
                doc0 = self.docstore.search(_id0)
                doc.page_content += " " + doc0.page_content
        if not isinstance(doc, Document):
            raise ValueError(f"Could not find document for id {_id}, got {doc}")
        doc_score = min([scores[0][id] for id in [indices[0].tolist().index(i) for i in id_seq if i in indices[0]]])
        doc.metadata["score"] = int(doc_score)
        docs.append(doc)
    torch_gc()
    return docs

def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
) -> List[Tuple[Document, float]]:
    embedding = self._embed_query(query)
    docs = self.similarity_search_with_score_by_vector(
        embedding,
        k,
    )
    return docs


class LocalDocQA:
    def __init__(self):
        self.llm: BaseAnswer = None
        self.embeddings: object = None
        self.top_k: int = local_file_model_config.VECTOR_SEARCH_TOP_K
        self.chunk_size: int = local_file_model_config.CHUNK_SIZE
        self.chunk_content: bool = local_file_model_config.chunk_content
        self.score_threshold: int = local_file_model_config.VECTOR_SEARCH_SCORE_THRESHOLD

    def init_config(self,
                    llm_model: BaseAnswer = None,
                    embedding_model:str=local_file_model_config.EMBEDDING_MODEL,
                    embedding_device:str=local_file_model_config.EMBEDDING_DEVICE,
                    top_k:int=local_file_model_config.VECTOR_SEARCH_TOP_K):
        self.llm=llm_model
        self.embeddings=HuggingFaceEmbeddings(model_name=local_file_model_config.embedding_model_dict[embedding_model],
                                              model_kwargs={"device":embedding_device})
        self.top_k=top_k

    def load_file(self,filepath,sentence_size:int=local_file_model_config.SENTENCE_SIZE):
        if filepath.lower().endswith(".txt"):
            loader = TextLoader(filepath, autodetect_encoding=True)
            textsplitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
            docs = loader.load_and_split(textsplitter)
        elif filepath.lower().endswith(".md"):
            loader = UnstructuredFileLoader(filepath, mode="elements")
            docs = loader.load()
        elif filepath.lower.endswith(".pdf"):
            loader = UnstructuredPaddlePDFLoader(filepath)
            textsplitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
            docs = loader.load_and_split(textsplitter)
        elif filepath.lower().endswith(".jpg") or filepath.lower().endswith(".png"):
            loader = UnstructuredPaddleImageLoader(filepath, mode="elements")
            textsplitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
            docs = loader.load_and_split(text_splitter=textsplitter)
        self.write_check_file(filepath, docs)
        return docs

    def write_check_file(self,filepath, docs):
        folder_path = os.path.join(os.path.dirname(filepath), "tmp_files")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        fp = os.path.join(folder_path, 'load_file.txt')
        with open(fp, 'a+', encoding='utf-8') as fout:
            fout.write("filepath=%s,len=%s" % (filepath, len(docs)))
        fout.write('\n')
        for i in docs:
            fout.write(str(i))
            fout.write('\n')
        fout.close()

    def tree(self,filepath, ignore_dir_names=None, ignore_file_names=None):
        """返回两个列表，第一个列表为 filepath 下全部文件的完整路径, 第二个为对应的文件名"""
        if ignore_dir_names is None:
            ignore_dir_names = []
        if ignore_file_names is None:
            ignore_file_names = []
        ret_list = []
        if isinstance(filepath, str):
            if not os.path.exists(filepath):
                print("路径不存在")
                return None, None
            elif os.path.isfile(filepath) and os.path.basename(filepath) not in ignore_file_names:
                return [filepath], [os.path.basename(filepath)]
            elif os.path.isdir(filepath) and os.path.basename(filepath) not in ignore_dir_names:
                for file in os.listdir(filepath):
                    fullfilepath = os.path.join(filepath, file)
                    if os.path.isfile(fullfilepath) and os.path.basename(fullfilepath) not in ignore_file_names:
                        ret_list.append(fullfilepath)
                    if os.path.isdir(fullfilepath) and os.path.basename(fullfilepath) not in ignore_dir_names:
                        ret_list.extend(self.tree(fullfilepath, ignore_dir_names, ignore_file_names)[0])
        return ret_list, [os.path.basename(p) for p in ret_list]

    def generate_prompt(self,
                        related_docs: List[str],
                        query: str,
                        prompt_template: str = local_file_model_config.PROMPT_TEMPLATE) -> str:
        #logger.info(f"#### related_docs={related_docs}")
        context = "\n".join([doc.page_content for doc in related_docs])
        prompt = prompt_template.replace("{question}", query).replace("{context}", context)
        return prompt

    # will keep CACHED_VS_NUM of vector store caches
    @lru_cache(local_file_model_config.CACHED_VS_NUM)
    def load_vector_store(self,vs_path, embeddings):
        '''
        ①lru_cache 是 Python 标准库 functools 中的一个装饰器，
        用于实现一个带有固定大小缓存的函数。LRU 代表“最近最少使用”（Least Recently Used），
        这意味着缓存会保留最近使用的结果，并在缓存满时删除最少使用的结果。
        ②当你调用一个使用 @lru_cache 装饰的函数时，函数的参数和返回值会被缓存。
        如果你再次调用该函数，并且传入相同的参数，装饰器会直接返回缓存中的结果，而不需要重新计算。
        这样可以显著提高性能，特别是对于计算成本高的函数。

        from functools import lru_cache
        @lru_cache(maxsize=3)
        def fibonacci(n):
            if n < 2:
                return n
            return fibonacci(n - 1) + fibonacci(n - 2)

        print(fibonacci(5))  # 5
        print(fibonacci.cache_info())  # 显示缓存的信息
        #在这个例子中，fibonacci 函数计算斐波那契数值，
        #并使用 lru_cache 来缓存其结果，以提高效率。
        #使用 fibonacci.cache_info() 可以查看缓存的状态，包括缓存的命中次数和缺失次数等信息。
        '''
        return FAISS.load_local(vs_path, embeddings,allow_dangerous_deserialization=True)

    def init_knowledge_vector_store(self,filepath:str or List[str],
                                    vs_path: str or os.PathLike = None,
                                    sentence_size=local_file_model_config.SENTENCE_SIZE):
        loaded_files = []
        failed_files = []
        docs = None
        # 1.加载本地知识库文件内容
        if isinstance(filepath, str):
            if not os.path.exists(filepath):
                logger.error("路径不存在!")
                return None
            elif os.path.isfile(filepath):
                file = os.path.split(filepath)[-1]
                try:
                    docs = self.load_file(filepath,sentence_size)
                    logger.info(f"加载本地知识库文件——{file} 文件已加载")
                    loaded_files.append(filepath)
                except Exception as e:
                    logger.error(f"加载本地知识库文件——{file} 文件加载失败！\ne={e}")
                    failed_files.append(file)
                    return None
            elif os.path.isdir(filepath):
                docs = []
                for fullfilepath,file in tqdm(zip(*self.tree(filepath,ignore_dir_names=['tmp_files'])),desc="加载文件"):
                    try:
                        docs += self.load_file(fullfilepath,sentence_size)
                        loaded_files.append(fullfilepath)
                        logger.info(f"加载本地知识库文件——{file} 文件已加载")
                    except Exception as e:
                        logger.error(f"加载本地知识库文件——{file} 文件加载失败！\ne={e}")
                        failed_files.append(file)
                        return None
                if len(failed_files)>0:
                    logger.warning(f"以下知识库文件加载失败：")
                    for index,file in enumerate(failed_files):
                        logger.warning(f"{index}-文件：{file}")
        else:#文件目录列表
            #TODO 后续改进
            logger.warning(f"加载本地知识库文件内容,filepath是个文件列表{filepath}")
            return None
        # 2.文件加载完毕，正在生成知识向量库，然后将知识向量库保存到 vs_path
        vector_store=None
        if len(docs)>0:
            logger.info(f"文件加载完毕，正在生成向量库")
            # 加载已有的向量模型（已经初始化好的的本地知识向量库checkpoint）
            if vs_path and os.path.isdir(vs_path) and "index.faiss" in os.listdir(vs_path):
                vector_store = self.load_vector_store(vs_path, self.embeddings)
                vector_store.add_documents(docs)
                torch_gc()
            # 初始化向量模型，将文本转换为知识向量库
            elif not vs_path:
                '''
                os.path.splitext(file)[0]：从文件路径 file 中提取文件名（去掉扩展名）。
                lazy_pinyin(...)：将文件名转换为拼音的列表。
                "".join(...)：将拼音列表中的字符串拼接为一个单一的字符串。
                datetime.datetime.now().strftime("%Y%m%d_%H%M%S")：获取当前时间并将其格式化为 YYYYMMDD_HHMMSS 的字符串。
                最终的字符串格式为 "{拼音}_FAISS_{当前时间}"。
                '''
                vs_path = os.path.join(local_file_model_config.VS_ROOT_PATH, f"""{"".join(lazy_pinyin(os.path.splitext(file)[0]))}_FAISS_{datetime.now().strftime("%Y%m%d_%H%M%S")}""")
                logger.info(f"初始化知识向量库，将知识向量库信息保存到vs_path={vs_path}")
                # 使用向量化模型将 知识文档 向量化
                vector_store = FAISS.from_documents(docs, self.embeddings)
                torch_gc()
            vector_store.save_local(vs_path)
            return vs_path, loaded_files
        else:
            logger.info("文件均未成功加载，请检查依赖包或替换为其他文件再次上传。")
            return None, loaded_files

    def get_knowledge_based_answer(self,query,
                                   vs_path,
                                   chat_history=[],
                                   streaming: bool = local_file_model_config.STREAMING):
        # 加载知识向量库
        vector_store = self.load_vector_store(vs_path, self.embeddings)
        FAISS.similarity_search_with_score_by_vector = similarity_search_with_score_by_vector#
        FAISS.similarity_search_with_score = similarity_search_with_score#
        vector_store.chunk_size = self.chunk_size
        vector_store.chunk_content = self.chunk_content
        vector_store.score_threshold = self.score_threshold
        # 计算用户问题和知识向量库中知识向量的相似度匹配
        related_docs_with_score = vector_store.similarity_search_with_score(query, k=self.top_k)
        torch_gc()
        prompt = self.generate_prompt(related_docs_with_score, query)
        #logger.info(f"prompt==={prompt}")
        for answer_result in self.llm.generatorAnswer(prompt=prompt, history=chat_history,streaming=streaming):
            resp = answer_result.llm_output["answer"]
            history = answer_result.history
            history[-1][0] = query
            #logger.warning(f"related_docs_with_score===={related_docs_with_score}")
            response = {"query": query,
                        "result": resp,
                        "source_documents": related_docs_with_score}
            yield response, history

