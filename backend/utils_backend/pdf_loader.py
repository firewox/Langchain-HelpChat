# @Time  :2024/11/21 14:01
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from langchain.document_loaders.unstructured import UnstructuredFileLoader
import nltk
from typing import List
import backend.configs.backend_config as local_file_model_config
from paddleocr import PaddleOCR
import os
import fitz
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

nltk.data.path = [local_file_model_config.NLTK_DATA_PATH] + nltk.data.path

class UnstructuredPaddlePDFLoader(UnstructuredFileLoader):
    def _get_elements(self) -> List:
        def pdf_ocr_txt(filepath, dir_path="tmp_files"):
            full_dir_path = os.path.join(os.path.dirname(filepath), dir_path)
            if not os.path.exists(full_dir_path):
                os.makedirs(full_dir_path)
            ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False, show_log=False)
            doc = fitz.open(filepath)
            txt_file_path = os.path.join(full_dir_path, f"{os.path.split(filepath)[-1]}.txt")
            img_name = os.path.join(full_dir_path, 'tmp.png')
            with open(txt_file_path, 'w', encoding='utf-8') as fout:
                for i in range(doc.page_count):
                    page = doc[i]
                    text = page.get_text("")
                    fout.write(text)
                    fout.write("\n")

                    img_list = page.get_images()
                    for img in img_list:
                        pix = fitz.Pixmap(doc, img[0])
                        if pix.n - pix.alpha >= 4:
                            pix = fitz.Pixmap(fitz.csRGB, pix)
                        pix.save(img_name)
                        result = ocr.ocr(img_name)
                        ocr_result = [i[1][0] for line in result for i in line]
                        fout.write("\n".join(ocr_result))
            if os.path.exists(img_name):
                os.remove(img_name)
            return txt_file_path

        txt_file_path = pdf_ocr_txt(self.file_path)
        # 下载NLTK库中的punkt模型，这个模型用于句子和单词的分割。
        #nltk.download('punkt')
        with open(txt_file_path,"r",encoding="utf-8") as file:
            con = file.read()
        sentences = nltk.tokenize.sent_tokenize(con)
        return [nltk.tokenize.word_tokenize(sentence) for sentence in sentences]
