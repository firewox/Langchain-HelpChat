# @Time  :2024/11/22 0:14
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from langchain.document_loaders import UnstructuredFileLoader
from paddleocr import PaddleOCR
import os
import nltk
from configs.model_config import NLTK_DATA_PATH
from typing import List
from nltk.tokenize import sent_tokenize, word_tokenize


nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

class UnstructuredPaddleImageLoader(UnstructuredFileLoader):
    """Loader that uses unstructured to load image files, such as PNGs and JPGs."""
    def _get_elements(self) -> List:
        def image_ocr_txt(filepath, dir_path="tmp_files"):
            full_dir_path = os.path.join(os.path.dirname(filepath), dir_path)
            if not os.path.exists(full_dir_path):
                os.makedirs(full_dir_path)
            filename = os.path.split(filepath)[-1]
            ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False, show_log=False)
            result = ocr.ocr(img=filepath)
            #
            ocr_result = [i[1][0] for line in result for i in line]
            txt_file_path = os.path.join(full_dir_path, "%s.txt" % (filename))
            with open(txt_file_path, 'w', encoding='utf-8') as fout:
                fout.write("\n".join(ocr_result))
            return txt_file_path

        txt_file_path = image_ocr_txt(self.file_path)
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        sentences = sent_tokenize(text)
        return [word_tokenize(sentence) for sentence in sentences]
