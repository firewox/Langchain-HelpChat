from langchain.document_loaders.unstructured import UnstructuredFileLoader
from paddleocr import PaddleOCR
import os
import nltk
from configs.model_config import NLTK_DATA_PATH
from unstructured.partition.text import partition_text

nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

class UnstructuredPaddleImageLoader(UnstructuredFileLoader):
    """Loader that uses unstructured to load image files, such as PNGs and JPGs."""

