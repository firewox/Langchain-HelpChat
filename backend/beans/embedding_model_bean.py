# @Time  :2024/12/7 16:39
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from typing import List,Tuple
from langchain.docstore.document import Document
from utils.utils import torch_gc
from langchain.vectorstores import FAISS

import numpy as np

class embedding_model_bean:
    def __init__(self):
        self._embeddings:HuggingFaceEmbeddings=None
        self._top_k = 50
        self._vector_store:FAISS=None



    @property
    def embeddings(self):
        return self._embeddings
    @embeddings.setter
    def embeddings(self,embeddings:HuggingFaceEmbeddings):
        self._embeddings=embeddings

    @property
    def top_k(self):
        return self._top_k
    @top_k.setter
    def top_k(self,top_k:int):
        self._top_k=top_k

    @property
    def vector_store(self):
        return self._vector_store
    @vector_store.setter
    def vector_store(self,vector_store:FAISS):
        self._vector_store=vector_store


# 分割匹配的一些工具方法
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