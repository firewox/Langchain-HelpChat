from models.base.base import BaseAnswer
import configs.model_config as model_config
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.document_loaders import UnstructuredFileLoader, TextLoader
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from langchain.document_loaders.text import TextLoader
from typing import List,Tuple
import os
from textsplitter.chinese_text_splitter import ChineseTextSplitter
from fileloader.pdf_loader import UnstructuredPaddlePDFLoader
from fileloader.image_loader import UnstructuredPaddleImageLoader
from tqdm import tqdm
from langchain.vectorstores import FAISS
from functools import lru_cache
from utils.utils import torch_gc
from pypinyin import lazy_pinyin
import datetime
from langchain.docstore.document import Document
import numpy as np

# patch HuggingFaceEmbeddings to make it hashable
def _embeddings_hash(self):
    return hash(self.model_name)
HuggingFaceEmbeddings.__hash__ = _embeddings_hash

def load_file(filepath, sentence_size = model_config.SENTENCE_SIZE):
    if filepath.lower().endswith(".md"):
        loader = UnstructuredFileLoader(filepath, mode="elements")
        docs = loader.load()
    elif filepath.lower().endswith(".txt"):
        loader = TextLoader(filepath, autodetect_encoding=True)
        textsplitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
        docs = loader.load_and_split(textsplitter)
    elif filepath.lower().endswith(".pdf"):
        loader = UnstructuredPaddlePDFLoader(filepath)
        textsplitter = ChineseTextSplitter(pdf=True, sentence_size=sentence_size)
        docs = loader.load_and_split(textsplitter)
    elif filepath.lower().endswith(".jpg") or filepath.lower().endswith(".png"):
        loader = UnstructuredPaddleImageLoader(filepath, mode="elements")
        textsplitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
        docs = loader.load_and_split(text_splitter=textsplitter)
    else:
        loader = UnstructuredFileLoader(filepath, mode="elements")
        textsplitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
        docs = loader.load_and_split(text_splitter=textsplitter)
    write_check_file(filepath, docs)
    return docs

def write_check_file(filepath, docs):
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

def tree(filepath, ignore_dir_names=None, ignore_file_names=None):
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
                    ret_list.extend(tree(fullfilepath, ignore_dir_names, ignore_file_names)[0])
    return ret_list, [os.path.basename(p) for p in ret_list]

# will keep CACHED_VS_NUM of vector store caches
@lru_cache(model_config.CACHED_VS_NUM)
def load_vector_store(vs_path, embeddings):
    return FAISS.load_local(vs_path, embeddings)

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

def similarity_search_with_score_by_vector(self, embedding: List[float], k: int = 4) -> List[Tuple[Document, float]]:
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
        if not self.chunk_conent:
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
    if not self.chunk_conent:
        return docs
    if len(id_set) == 0 and self.score_threshold > 0:
        return []
    id_list = sorted(list(id_set))
    id_lists = seperate_list(id_list)

def generate_prompt(related_docs: List[str], query: str, prompt_template: str = model_config.PROMPT_TEMPLATE) -> str:
    context = "\n".join([doc.page_content for doc in related_docs])
    prompt = prompt_template.replace("{question}", query).replace("{context}", context)
    return prompt

class LocalDocQA:
    llm: BaseAnswer = None
    embeddings: object = None
    top_k: int = model_config.VECTOR_SEARCH_TOP_K
    chunk_size: int = model_config.CHUNK_SIZE
    chunk_conent: bool = True
    score_threshold: int = model_config.VECTOR_SEARCH_SCORE_THRESHOLD

    def init_cfg(self,
                 embedding_model: str = model_config.EMBEDDING_MODEL,
                 embedding_device=model_config.EMBEDDING_DEVICE,
                 llm_model: BaseAnswer = None,
                 top_k=model_config.VECTOR_SEARCH_TOP_K,
                 ):
        self.llm = llm_model
        self.embeddings = HuggingFaceEmbeddings(model_name=model_config.embedding_model_dict[embedding_model],
                                                model_kwargs={'device': embedding_device})
        self.top_k = top_k

    def init_knowledge_vector_store(self,filepath:str or List[str],
                                    vs_path: str or os.PathLike = None,
                                    sentence_size=model_config.SENTENCE_SIZE):
        loaded_files = []
        failed_files = []
        # 1.加载本地知识库文件内容
        if isinstance(filepath, str):
            if not os.path.exists(filepath):
                print("路径不存在!")
                return None
            elif os.path.isfile(filepath):
                file = os.path.split(filepath)[-1]
                try:
                    docs = load_file(filepath, sentence_size)
                    model_config.logger.info(f"{file} 已成功加载")
                    loaded_files.append(filepath)
                except Exception as e:
                    model_config.logger.error(e)
                    model_config.logger.info(f"{file} 未能成功加载")
                    return None
            elif os.path.isdir(filepath):
                docs = []
                for fullfilepath, file in tqdm(zip(*tree(filepath, ignore_dir_names=['tmp_files'])), desc="加载文件"):
                    try:
                        docs += load_file(fullfilepath, sentence_size)
                        loaded_files.append(fullfilepath)
                    except Exception as e:
                        model_config.logger.error(e)
                        failed_files.append(file)

                if len(failed_files) > 0:
                    model_config.logger.info("以下文件未能成功加载：")
                    for file in failed_files:
                        model_config.logger.info(f"{file}\n")
        else:
            docs = []
            for file in filepath:
                try:
                    docs += load_file(file)
                    model_config.logger.info(f"{file} 已成功加载")
                    loaded_files.append(file)
                except Exception as e:
                    model_config.logger.error(e)
                    model_config.logger.info(f"{file} 未能成功加载")
        # 2.文件加载完毕，正在生成向量库
        if len(docs) > 0:
            model_config.logger.info("文件加载完毕，正在生成向量库")
            # 加载已有的向量模型
            if vs_path and os.path.isdir(vs_path) and "index.faiss" in os.listdir(vs_path):
                vector_store = load_vector_store(vs_path, self.embeddings)
                vector_store.add_documents(docs)
                torch_gc()
            # 初始化向量模型，将文本转换为向量库
            elif not vs_path:
                vs_path = os.path.join(model_config.VS_ROOT_PATH, f"""{"".join(lazy_pinyin(os.path.splitext(file)[0]))}_FAISS_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}""")
                vector_store = FAISS.from_documents(docs, self.embeddings)  # docs 为Document列表
                torch_gc()
            vector_store.save_local(vs_path)
            return vs_path, loaded_files
        else:
            model_config.logger.info("文件均未成功加载，请检查依赖包或替换为其他文件再次上传。")
            return None, loaded_files

    def get_knowledge_based_answer(self, query, vs_path, chat_history=[], streaming: bool = model_config.STREAMING):
        vector_store = load_vector_store(vs_path, self.embeddings)
        FAISS.similarity_search_with_score_by_vector = similarity_search_with_score_by_vector
        vector_store.chunk_size = self.chunk_size
        vector_store.chunk_conent = self.chunk_conent
        vector_store.score_threshold = self.score_threshold
        related_docs_with_score = vector_store.similarity_search_with_score(query, k=self.top_k)
        torch_gc()
        prompt = generate_prompt(related_docs_with_score, query)

        for answer_result in self.llm.generatorAnswer(prompt=prompt, history=chat_history,streaming=streaming):
            resp = answer_result.llm_output["answer"]
            history = answer_result.history
            history[-1][0] = query
            response = {"query": query,
                        "result": resp,
                        "source_documents": related_docs_with_score}
            yield response, history