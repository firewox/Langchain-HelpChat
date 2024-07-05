from models.base.base import BaseAnswer
import configs.model_config as model_config
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.document_loaders import UnstructuredFileLoader, TextLoader
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from langchain.document_loaders.text import TextLoader
from typing import List
import os
from textsplitter.chinese_text_splitter import ChineseTextSplitter


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
        if isinstance(filepath, str):
            if not os.path.exists(filepath):
                print("路径不存在")
                return None
            elif os.path.isfile(filepath):
                file = os.path.split(filepath)[-1]
                try:
                    docs = load_file(filepath, sentence_size)

