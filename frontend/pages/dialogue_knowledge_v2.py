# @Time  :2024/12/21 1:44
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import streamlit as st

from frontend.components.knowledge_gpt.sidebar import sidebar

from frontend.components.knowledge_gpt.ui import (
    wrap_doc_in_html,
    is_query_valid,
    is_file_valid,
    is_open_ai_key_valid,
    display_file_read_error,
)

from frontend.components.knowledge_gpt.core.caching import bootstrap_caching

from frontend.components.knowledge_gpt.core.parsing import read_file
from frontend.components.knowledge_gpt.core.chunking import chunk_file
from frontend.components.knowledge_gpt.core.embedding import embed_files
from frontend.components.knowledge_gpt.core.qa import query_folder
from frontend.components.knowledge_gpt.core.utils import get_llm
from frontend.api.api_chat import api_chat
from frontend.api.api_knowledge import api_knowledge

api_chat_instance = api_chat()
api_knowledge_instance = api_knowledge()

class dialogue_knowledge_v2:
    @classmethod
    def dialogue_knowledge_v2_page(cls):
        #EMBEDDING = "openai"
        #VECTOR_STORE = "faiss"
        MODEL_LIST = api_chat_instance.get_model_list()

        # Uncomment to enable debug mode
        # MODEL_LIST.insert(0, "debug")

        #st.set_page_config(page_title="KnowledgeGPT", page_icon="📖", layout="wide")
        st.header("📖Knowledge-Chat")

        # Enable caching for expensive functions
        #bootstrap_caching()

        #sidebar()

        #openai_api_key = st.session_state.get("OPENAI_API_KEY")

        # if not openai_api_key:
        #     st.warning(
        #         "Enter your OpenAI API key in the sidebar. You can get a key at"
        #         " https://platform.openai.com/account/api-keys."
        #     )


        uploaded_file = st.file_uploader(
            "Upload a pdf, docx, or txt file",
            type=["pdf", "docx", "txt",'jpg','pbg'],
            help="Scanned documents are not supported yet!",
            accept_multiple_files=True,
        )

        model: str = st.selectbox("Model", options=MODEL_LIST)  # type: ignore

        # with st.expander("Advanced Options"):
        #     return_all_chunks = st.checkbox("Show all chunks retrieved from vector search")
        #     show_full_doc = st.checkbox("Show parsed contents of the document")

        dir_name = st.text_input("",placeholder="起一个知识库名称吧")
        if not dir_name:
            st.stop()

        if not uploaded_file:
            st.stop()

        # try:
        #     file = read_file(uploaded_file)
        # except Exception as e:
        #     display_file_read_error(e, file_name=uploaded_file.name)


        if st.button("合成知识库"):
            if not dir_name:
                st.stop()
            #TODO 上传文档到后端
            flag = api_knowledge_instance.upload_file(user_id=st.session_state.user_id,dir_name=dir_name,file=uploaded_file)
            api_knowledge_instance.create_knowledge(user_id=st.session_state.user_id,dir_name=dir_name)
            if flag==1:
                st.balloons()
            else:
                st.warning("合成知识库失败……")
        #chunked_file = chunk_file(file, chunk_size=300, chunk_overlap=0)

        # if not is_file_valid(file):
        #     st.stop()


        # with st.spinner("Indexing document... This may take a while⏳"):
        #     folder_index = embed_files(
        #         files=[chunked_file],
        #         embedding=EMBEDDING if model != "debug" else "debug",
        #         vector_store=VECTOR_STORE if model != "debug" else "debug",
        #         openai_api_key=openai_api_key,
        #     )




'''
        with st.form(key="qa_form"):
            query = st.text_area("Ask a question about the document")
            submit = st.form_submit_button("Submit")


        if show_full_doc:
            with st.expander("Document"):
                # Hack to get around st.markdown rendering LaTeX
                #st.markdown(f"<p>{wrap_doc_in_html(file.docs)}</p>", unsafe_allow_html=True)
                st.markdown(f"<p>Hello Help Bot</p>", unsafe_allow_html=True)


        if submit:
            if not is_query_valid(query):
                st.stop()

            # Output Columns
            answer_col, sources_col = st.columns(2)

            llm = get_llm(model=model, openai_api_key=openai_api_key, temperature=0)
            #api_chat_instance.get_chat(model_name=model,messages=)
            result = query_folder(
                folder_index=folder_index,
                query=query,
                return_all=return_all_chunks,
                llm=llm,
            )

            with answer_col:
                st.markdown("#### Answer")
                st.markdown(result.answer)

            with sources_col:
                st.markdown("#### Sources")
                for source in result.sources:
                    st.markdown(source.page_content)
                    st.markdown(source.metadata["source"])
                    st.markdown("---")


'''