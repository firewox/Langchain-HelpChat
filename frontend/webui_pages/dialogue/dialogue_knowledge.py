# @Time  :2024/12/7 11:33
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import streamlit as st
from frontend.api_frontend.api_frontend_knowledge_chat import api_frontend_knowledge_chat
from frontend.api_frontend.api_frontend_chat import api_frontend_chat
from utils.logger import logger
from backend.configs.model_config import PROMPT_TEMPLATE_FLAG
from configs.project_configs import ASSISTANT_LOGO_IMG,USER_LOGO_IMG


# 用户第一次进到页面，设falg=True，将历史聊天记录挂载到 st.session_state.all_messages 里
class dialogue_knowledge_util:
    FLAG=True
    COUNT=0

# 实例化api请求接口
api_frontend_chat_instance:api_frontend_chat = api_frontend_chat()
api_frontend_knowledge_chat_instance:api_frontend_knowledge_chat = api_frontend_knowledge_chat()

# new UI layout
def dialogue_knowledge_page():
    # 使用 session_state 来存储当前的选择
    if 'model_name' not in st.session_state or "model_list" not in st.session_state:
        # 给后端发请求，查询可用的大模型
        model_list = api_frontend_chat_instance.get_model_list()
        st.session_state.model_name = model_list[0]
        st.session_state.model_list = model_list
    if "history_name" not in st.session_state or "history_name_list" not in st.session_state:
        # 给后端发送请求，挂载历史聊天记录的名称列表
        history_name_list = api_frontend_chat_instance.get_history_name_list()
        st.session_state.history_name = history_name_list[0]
        st.session_state.history_name_list = history_name_list
        # Initialize chat history
        # # 给后端发请求，挂载历史聊天记录
        messages = api_frontend_chat_instance.get_history_chat(history_name=st.session_state.history_name)
        logger.info(f"\n\n挂载历史聊天记录A={messages}")
        #st.session_state.messages = messages
    if "knowledge_name" not in st.session_state or "knowledge_name_list" not in st.session_state:
        knowledge_name_list = api_frontend_knowledge_chat_instance.get_knowledge_name_list()
        st.session_state.knowledge_name = knowledge_name_list[0]
        st.session_state.knowledge_name_list = knowledge_name_list
    if "embedding_model_name" not in st.session_state or "embedding_model_name_list" not in st.session_state:
        embedding_model_name_list = api_frontend_knowledge_chat_instance.get_embedding_model_list()
        st.session_state.embedding_model_name = embedding_model_name_list[0]
        st.session_state.embedding_model_name_list = embedding_model_name_list
    if len(api_frontend_chat_instance.messages)==0:
        # # 给后端发请求，挂载历史聊天记录
        messages = api_frontend_chat_instance.get_history_chat(history_name=st.session_state.history_name)
        #st.session_state.messages = messages

    col1,col2,col3,col4,col5 = st.columns([1,1,1,1,1])
    col1_placeholder = col1.empty()
    col2_placeholder = col2.empty()
    col3_placeholder = col3.empty()
    col4_placeholder = col4.empty()
    col5_placeholder = col5.empty()
    #
    #dialogue_knowledge_util.COUNT+=1
    # col1
    genre = col1_placeholder.selectbox(
        ":rainbow[LLM Select]",
        (f"{ml}" for ml in st.session_state.model_list),
    )
    api_frontend_chat_instance.model_name = genre
    # col2
    genre2 = col2_placeholder.selectbox(":rainbow[History Select]",(hnl for hnl in st.session_state.history_name_list),)
    if genre2!=st.session_state.history_name:
        api_frontend_chat_instance.history_name = genre2
        st.session_state.history_name = genre2
        # # 给后端发请求，挂载历史聊天记录
        messages = api_frontend_chat_instance.get_history_chat(history_name=st.session_state.history_name)
        #st.session_state.messages=messages
        logger.info(f"\n\n挂载历史聊天记录B={messages}")
    # col3
    # col4
    genre4 = col4_placeholder.selectbox(":rainbow[Knowledge Books]",(i for i in st.session_state.knowledge_name_list),)
    api_frontend_knowledge_chat_instance.knowledge_name = genre4
    st.session_state.knowledge_name = genre4
    # col5
    genre5 = col5_placeholder.selectbox(":rainbow[Embedding Models]",(i for i in st.session_state.embedding_model_name_list),)
    api_frontend_knowledge_chat_instance.embedding_model_name = genre5
    st.session_state.embedding_model_name = genre5


    st.title("🦜🔗 HelpChat App")
    # Display chat messages from history on app rerun
    if len(api_frontend_chat_instance.messages)>=2:
        # TODO 处理 streamlit 的bug问题：在本脚本中，关于messages数据的增加和显示被干扰，后端会对query进行处理：进行 prompt = query+rag 的操作，
        # TODO 但是前端 streamlit页面的 messages会被自动注入 prompt=query+rag。
        #  例如：本来的query为messages={“role”:user,"content":"你好"}，经过后端处理后，前端的messages自动变为 messages={“role”:user,"content":"已知信息：RAG知识，问题是：你好"}
        # TODO 经过多种尝试解决，暂时解决不了
        for i in api_frontend_chat_instance.messages:
            if i.get("role") == "user" and PROMPT_TEMPLATE_FLAG in i.get("content"):
                index = i.get("content").rfind(PROMPT_TEMPLATE_FLAG)
                i["content"] = i.get("content")[index+len(PROMPT_TEMPLATE_FLAG):]
        dialogue_knowledge_util.COUNT+=1
        #logger.info(F"\ndialogue_knowledge_util.COUNT={dialogue_knowledge_util.COUNT}\nmessages={st.session_state.messages}")
        #st.info(f"st.session_state.all_messages={st.session_state.all_messages}")
        logger.info(f"\n\nA count={dialogue_knowledge_util.COUNT},\nmessages={api_frontend_chat_instance.messages}")
        for index,message in enumerate(api_frontend_chat_instance.messages[2:]):#(st.session_state.messages):
            with st.chat_message(name=message['role'],avatar=":material/face:"):
                st.markdown(message["content"])

    # Accept user input
    prompt = st.chat_input("最近怎么样？")
    if prompt:
        #st.session_state.messages.append({"role": "user", "content": prompt})
        logger.info(f"\n\n###query测试A={prompt}")
        api_frontend_chat_instance.messages = api_frontend_chat_instance.messages + [{"role": "user", "content": prompt}]
        logger.info(f"\n\n###query测试B={api_frontend_chat_instance.messages}")
        # Display user message in chat message container
        with st.chat_message(name="user",avatar=":material/face:"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message(name="assistant",avatar=":material/smart_toy:"):
            if len(api_frontend_chat_instance.messages)==0:
                pass
            else:
                # 给后端发请求，发送消息
                stream = api_frontend_chat_instance.get_knowledge_chat(model_name=st.session_state.model_name,
                                                                       embedding_model_name=st.session_state.embedding_model_name,
                                                                       knowledge_name=st.session_state.knowledge_name,
                                                                       msgs=api_frontend_chat_instance.messages.copy())
                response = st.write_stream(stream)
                
                # 保存返回的聊天响应
                #st.info(f"messages={get_history_chat.messages}")
                #st.session_state.messages.append({"role":"assistant","content":response})
                api_frontend_chat_instance.messages = api_frontend_chat_instance.messages + [{"role": "assistant", "content": response}]
                #st.session_state.messages.append({"role":"assistant","content":response})
                # 给后端发请求，实时保存聊天记录
                api_frontend_chat_instance.set_history_chat(messages=api_frontend_chat_instance.messages)

