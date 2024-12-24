# @Time  :2024/12/7 14:57
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import os
from backend.configs.backend_config import (EMBEDDING_MODEL,
                                            embedding_model_dict,
                                            PROMPT_TEMPLATE,
                                            CHUNK_SIZE,
                                            EMBEDDING_DEVICE,
                                            VECTOR_SEARCH_TOP_K,
                                            VECTOR_SEARCH_SCORE_THRESHOLD,
                                            UPLOAD_ROOT_PATH,
                                            SENTENCE_SIZE,
                                            VS_ROOT_PATH)
from typing import Dict,List,Tuple
from langchain_core.documents import Document
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from backend.beans.embedding_model_bean import (embedding_model_bean,#类
                                                similarity_search_with_score_by_vector,#函数
                                                similarity_search_with_score)#函数
from utils.logger import logger
from utils.utils import torch_gc
from openai import OpenAI
from backend.dao.knowledge_dao import knowledge_dao
from backend.utils_backend.chinese_text_splitter import ChineseTextSplitter
from backend.utils_backend.pdf_loader import UnstructuredPaddlePDFLoader
from backend.utils_backend.image_loader import UnstructuredPaddleImageLoader
from langchain.document_loaders import UnstructuredFileLoader, TextLoader
from functools import lru_cache


HuggingFaceEmbeddings.__hash__= embedding_model_bean._embeddings_hash

class knowledge_services:
    embeddings_model_bean_instance:embedding_model_bean = embedding_model_bean()

    @classmethod
    def load_file(cls,filepath, sentence_size=250):
        if filepath.lower().endswith(".md"):
            loader = UnstructuredFileLoader(filepath, mode="elements")
            docs = loader.load()
        elif filepath.lower().endswith(".txt"):
            logger.info(f"\n加载txt文件")
            loader = TextLoader(filepath, autodetect_encoding=True)
            textsplitter = ChineseTextSplitter(pdf=False, sentence_size=sentence_size)
            logger.info(f"\n加载txt文件111")
            docs = loader.load_and_split(textsplitter)
            logger.info(f"\n加载txt文件222")
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
        cls.write_check_file(filepath, docs)
        return docs

    @classmethod
    def write_check_file(cls,filepath, docs):
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

    @classmethod
    def read_check_file(cls,filepath):
        fp = filepath
        documents=[]
        with open(fp, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # 跳过第一行
            for line in lines[1:]:
                # 提取 page_content 和 metadata
                if "page_content=" in line and "metadata=" in line:
                    # 分割 line，提取出 page_content 和 metadata 部分
                    page_content_part, metadata_part = line.split(" metadata=")

                    # 提取 page_content 的内容
                    page_content = page_content_part.split("page_content=")[1].strip().strip("'")

                    # 提取 metadata 的内容
                    metadata = eval(metadata_part.strip())

                    # 创建 Document 对象
                    document = Document(page_content=page_content, metadata=metadata)

                    # 添加到列表中
                    documents.append(document)
        return documents

    @classmethod
    def knowledgeInsertFileDir(cls,user_id,dir_name):
        content_path = os.path.join(UPLOAD_ROOT_PATH,user_id,dir_name)
        file_dir_id = knowledge_dao.knowledgeGetFileDirByUserIdAndFileDirName(user_id=user_id,file_dir_name=os.path.join(user_id,dir_name))
        if file_dir_id is None:#不存在记录，则插入记录
            file_dir_id = knowledge_dao.knowledgeInsertFileDirToFileDirTable(file_dir_name=os.path.join(user_id,dir_name),
                                                                             file_dir_path=content_path,
                                                                             user_id=user_id)
        return file_dir_id


    @classmethod
    def knowledgeInsertFile(cls,user_id,dir_name,file_name):
        # 将这批文件集的信息保存到 数据库 file_dir 表
        # 如果 file_dir 表 中没有 file_dir_name=file_dir_name and user_id=user_id的信息，则保存新的记录,返回file_dir_id
        # 如果file_dir 表已经有了file_dir_name=file_dir_name and user_id=user_id的数据，则返回file_dir_id，给下一步处理
        file_dir_id = cls.knowledgeInsertFileDir(user_id=user_id,dir_name=dir_name)
        # 将单个文件的路径保存到 数据库 file 表
        file_path = os.path.join(UPLOAD_ROOT_PATH, user_id, dir_name,file_name)
        knowledge_dao.knowledgeInsertFileToFileTable(file_name=file_name,file_path=file_path,
                                                     file_dir_id=file_dir_id,)

    @classmethod
    def create_knowledge(cls,user_id:str,dir_name:str):
        # 遍历 dir_name 文件（包括：pdf、txt、txt、jpg、png）
        content_path = os.path.join(UPLOAD_ROOT_PATH,user_id,dir_name)
        content_docs = []
        if os.path.exists(content_path) and "tmp_files" not in os.listdir(content_path):
            for fle in os.listdir(content_path):
                logger.info(f"\n加载向量模型os.path.join(content_path,fle)={os.path.join(content_path,fle)}")
                doc=cls.load_file(filepath=os.path.join(content_path,fle),sentence_size=SENTENCE_SIZE)
                content_docs=content_docs+doc
        else:
            content_docs=cls.read_check_file(filepath=os.path.join(content_path,"tmp_files","load_file.txt"))
        # 加载向量模型
        if cls.embeddings_model_bean_instance.embeddings==None:
            logger.info(f"\n加载向量模型knowledgeInitEmbeddingModel")
            f1 = cls.knowledgeInitEmbeddingModel(embedding_model_name=EMBEDDING_MODEL,device=EMBEDDING_DEVICE,top_k=VECTOR_SEARCH_TOP_K)
            if len(content_docs) > 0:
                logger.info("文件加载完毕，正在生成向量库")
                # 检查知识向量库文件路径
                from pypinyin import lazy_pinyin
                vector_path = os.path.join(VS_ROOT_PATH,user_id, "_".join(lazy_pinyin(dir_name)))
                logger.info(f"\n检查知识向量库文件路径vector_path={vector_path}")
                if os.path.exists(vector_path):
                    # 加载知识向量库
                    cls.knowledgeLoadVectorStore(knowledge_vector_path=vector_path, embeddings=cls.embeddings_model_bean_instance.embeddings)
                    logger.info(f"\n加载知识向量库knowledgeLoadVectorStore")
                else:
                    # 将文档内容向量化
                    print(content_docs)
                    cls.knowledgeInitVectorStore(docs=content_docs)
                    logger.info(f"\n保存向量化知识库vector_path=")
                    # 保存向量化知识库
                    while not os.path.exists(vector_path):
                        os.makedirs(vector_path,exist_ok=True)
                    logger.error(f"\n保存向量化知识库vector_path=1")
                    cls.embeddings_model_bean_instance.vector_store.save_local(vector_path)
                    # 将知识库的路径保存到数据库中
                    knowledge_dao.knowledgeInsertKnowledge(knowledge_vector_name=dir_name,user_id=user_id,
                                                           knowledge_vector_path=vector_path,
                                                           embedding_model_name=EMBEDDING_MODEL,
                                                           remark="")
                    logger.info(f"\n保存向量化知识库vector_path={vector_path}")
        logger.info(f"\n加载知识向量库成功！")
        return 1
        # except Exception as e:
        #     logger.error(f"create_knowledge错误，错误原因e={e}")
        #     return None


    @classmethod
    def knowledgeInitVectorStore(cls,docs):
        cls.embeddings_model_bean_instance.vector_store = FAISS.from_documents(docs, cls.embeddings_model_bean_instance.embeddings)  # docs 为Document列表
        #torch_gc()

    # 查询所有已经向量化后知识向量库列表
    @classmethod
    def knowledgeGetKnowledgeNameList(cls,user_id:str):
        knowledge_name_list = knowledge_dao.knowledgeGetKnowledgeNameList(user_id=user_id)
        return knowledge_name_list

    # 初始化加载向量化模型
    @classmethod
    def knowledgeInitEmbeddingModel(cls,embedding_model_name:str,device:str,top_k:int):
        if cls.embeddings_model_bean_instance.embeddings is not None:
            return True
        logger.info(f"向量化模型：{embedding_model_name}")
        try:
            cls.embeddings_model_bean_instance.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[embedding_model_name],model_kwargs={"device":device})
            cls.embeddings_model_bean_instance.top_k=top_k
            return True
        except Exception as e:
            logger.error(f"初始向量模型出现错误，原因e={e}")
            return False

    # 加载知识向量库
    @classmethod
    # will keep CACHED_VS_NUM of vector store caches
    @lru_cache(3)
    def knowledgeLoadVectorStore(cls,embeddings:HuggingFaceEmbeddings,knowledge_name:str,knowledge_vector_path:str):
        if cls.embeddings_model_bean_instance.vector_store is not None:
            return True
        try:
            if os.path.exists(knowledge_vector_path):
                cls.embeddings_model_bean_instance.vector_store = FAISS.load_local(folder_path=knowledge_vector_path,embeddings=embeddings,allow_dangerous_deserialization=True)
                return True
            else:
                logger.error("选择的知识向量库路径不存在")
                return False
        except Exception as e:
            logger.info(f"加载知识向量库出现错误，原因e={e}")
            return False

    # Intent Recognition 意图识别操作，判断用户的query和知识向量库检索出来的片段的关联性大不大
    # 如果用户的问题和知识向量库相关，则返回 “rag”；如果不相关，则返回 “none”
    @classmethod
    def knowledgeIntentRecognition(cls,query:str,knowledge_rag:List[Tuple[Document, float]]):
        return "rag"

    # 将query和检索的知识片段注入prompt
    @classmethod
    def knowledgeGeneratePrompt(cls,related_docs:List[Tuple[Document, float]],
                                query:str,
                                prompt_template:str):
        context = "\n".join([doc.page_content for doc in related_docs])
        return prompt_template.replace("{question}", query).replace("{context}", context)

    # 处理知识向量库聊天的逻辑
    @classmethod
    def knowledgeChat(cls,user_id:str,
                      knowledge_vector_name:str,
                      prompt:str):
        knowledge_vector_path = knowledge_dao.knowledgeGetKnowledgeVectorPath(user_id=user_id,
                                                                              knowledge_vector_name=knowledge_vector_name)
        flag1 = cls.knowledgeInitEmbeddingModel(embedding_model_name=EMBEDDING_MODEL,
                                                               device=EMBEDDING_DEVICE,
                                                               top_k=VECTOR_SEARCH_TOP_K)
        logger.info(f"\n知识向量对话knowledge_vector_path={knowledge_vector_path}")
        logger.info(f"\n知识向量对话 knowledge_vector_name={knowledge_vector_name}")
        flag2 = cls.knowledgeLoadVectorStore(embeddings=cls.embeddings_model_bean_instance.embeddings,
                                                            knowledge_name=knowledge_vector_name,
                                                            knowledge_vector_path=knowledge_vector_path)
        if not (flag1 and flag2):
            logger.info(f"##########not (flag1 and flag2)={not (flag1 and flag2)}")
            return None
        FAISS.similarity_search_with_score_by_vector = similarity_search_with_score_by_vector#
        FAISS.similarity_search_with_score = similarity_search_with_score#
        cls.embeddings_model_bean_instance.vector_store.chunk_size = CHUNK_SIZE # 匹配后单段上下文长度
        cls.embeddings_model_bean_instance.vector_store.chunk_content = True
        cls.embeddings_model_bean_instance.vector_store.score_threshold = VECTOR_SEARCH_SCORE_THRESHOLD # 知识检索内容相关度 Score, 数值范围约为0-1100，如果为0，则不生效

        # 计算用户问题和知识向量库中知识向量的相似度匹配
        related_docs_with_score = cls.embeddings_model_bean_instance.vector_store.similarity_search_with_score(
            query=prompt,
            k=cls.embeddings_model_bean_instance.top_k)
        torch_gc()
        # query的意图识别
        flag3 = cls.knowledgeIntentRecognition(query=prompt,knowledge_rag=related_docs_with_score)
        if "rag".lower() != flag3.lower():
            pass
        prompt_new = cls.knowledgeGeneratePrompt(query=prompt,
                                                   related_docs=related_docs_with_score,
                                                   prompt_template=PROMPT_TEMPLATE)
        return prompt_new,related_docs_with_score