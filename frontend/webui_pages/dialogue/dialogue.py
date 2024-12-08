import streamlit as st
from streamlit_chatbox import *
from datetime import datetime
from configs.project_configs import LOGO_IMG
import asyncio
from backend.servers.chat.openai_chat_services import openai_chat_v1
from typing import List, Dict
from utils.logger import logger
from frontend.api_frontend.api_frontend_chat import api_frontend_chat
from backend.configs.model_config import PROMPT_TEMPLATE_FLAG
from configs.project_configs import ASSISTANT_LOGO_IMG,USER_LOGO_IMG



# 用户第一次进到页面，设falg=True，将历史聊天记录挂载到 st.session_state.messages 里
class dialogue_util:
    FLAG=True
    COUNT=0


# 实例化api请求接口
api_frontend_chat_instance:api_frontend_chat = api_frontend_chat()

# new UI layout
def dialogue_page_v1():
    # 使用 session_state 来存储当前的选择
    if 'model_name' not in st.session_state or "model_list" not in st.session_state:
        # 给后端发请求，查询可用的大模型
        model_list = api_frontend_chat_instance.get_model_list()
        st.session_state.model_name = model_list[0]
        st.session_state.model_list = [i for i in model_list]
    if "history_name" not in st.session_state or "history_name_list" not in st.session_state:
        # 给后端发送请求，挂载历史聊天记录的名称列表
        history_name_list = api_frontend_chat_instance.get_history_name_list()
        st.session_state.history_name = history_name_list[0]
        api_frontend_chat_instance.history_name = history_name_list[0]
        st.session_state.history_name_list = [i for i in history_name_list]
        # Initialize chat history
        # # 给后端发请求，挂载历史聊天记录
        messages = api_frontend_chat_instance.get_history_chat(history_name=st.session_state.history_name)
        #st.session_state.messages = messages
    if len(api_frontend_chat_instance.messages)==0:
        # # 给后端发请求，挂载历史聊天记录
        messages = api_frontend_chat_instance.get_history_chat(history_name=st.session_state.history_name)
        #st.session_state.messages = messages

    col1,col2 = st.columns([1,1])
    # col1
    dialogue_util.COUNT+=1
    genre = col1.selectbox(
        ":rainbow[LLM select]",
        (f"{ml}" for ml in st.session_state.model_list),
    )
    api_frontend_chat_instance.model_name = genre
    st.session_state.model_name = genre
    # col2
    col2_placeholder = col2.empty()
    genre2 = col2_placeholder.selectbox(":rainbow[History select]",
                                        (hnl for hnl in st.session_state.history_name_list),)
    if genre2!=st.session_state.history_name:
        api_frontend_chat_instance.history_name = genre2#match.group(1)
        st.session_state.history_name = genre2
        # # 给后端发请求，挂载历史聊天记录
        messages = api_frontend_chat_instance.get_history_chat(history_name=st.session_state.history_name)


    st.title("🦜🔗 HelpChat App")
    # Display chat messages from history on app rerun
    if len(api_frontend_chat_instance.messages)!=0:
        # TODO 处理 streamlit 的bug问题：在本脚本中，关于messages数据的增加和显示被干扰，后端会对query进行处理：进行 prompt = query+rag 的操作，
        # TODO 但是前端 streamlit页面的 messages会被自动注入 prompt=query+rag。
        #  例如：本来的query为messages={“role”:user,"content":"你好"}，经过后端处理后，前端的messages自动变为 messages={“role”:user,"content":"已知信息：RAG知识，问题是：你好"}
        # TODO 经过多种尝试解决，暂时解决不了
        for i in api_frontend_chat_instance.messages:
            if i.get("role") == "user" and PROMPT_TEMPLATE_FLAG in i.get("content"):
                index = i.get("content").rfind(PROMPT_TEMPLATE_FLAG)
                i["content"] = i.get("content")[index+len(PROMPT_TEMPLATE_FLAG):]
        #st.info(f"st.session_state.messages={st.session_state.messages}")
        for index,message in enumerate(api_frontend_chat_instance.messages):
            if index>=2:
                with st.chat_message(name=message['role'],avatar=":material/face:"):
                    st.markdown(message["content"])

    # Accept user input
    prompt = st.chat_input("最近怎么样？")
    if prompt:
        # Add user message to chat history
        logger.info(f"\n###query测试A={prompt}")
        api_frontend_chat_instance.messages = api_frontend_chat_instance.messages + [{"role": "user", "content": prompt}]
        logger.info(f"\n###query测试B={api_frontend_chat_instance.messages}")
        # Display user message in chat message container
        with st.chat_message(name="user",avatar=":material/face:"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message(name="assistant",avatar=":material/smart_toy:"):
            if len(api_frontend_chat_instance.messages)==0:
                pass
            else:
                # 给后端发请求，发送消息
                stream = api_frontend_chat_instance.get_chat(model_name=api_frontend_chat_instance.model_name,messages=api_frontend_chat_instance.messages.copy())
                response = st.write_stream(stream)

                # 保存返回的聊天响应
                api_frontend_chat_instance.messages = api_frontend_chat_instance.messages + [{"role":"assistant","content":response}]
                # 给后端发请求，实时保存聊天记录
                api_frontend_chat_instance.set_history_chat(messages=api_frontend_chat_instance.messages)






chat_box = ChatBox(
    assistant_avatar=LOGO_IMG
)
def get_messages_history(history_len: int, content_in_expander: bool = False) -> List[Dict]:
    '''
    返回消息历史。
    content_in_expander控制是否返回expander元素中的内容，一般导出的时候可以选上，传入LLM的history不需要
    '''

    def filter(msg):
        content = [x for x in msg["elements"] if x._output_method in ["markdown", "text"]]
        if not content_in_expander:
            content = [x for x in content if not x._in_expander]
        content = [x.content for x in content]

        return {
            "role": msg["role"],
            "content": "\n\n".join(content),
        }

    return chat_box.filter_history(history_len=history_len, filter=filter)

def chat_chat():
    pass

def dialogue_page():
    if not chat_box.chat_inited:
        default_model = "glm-4-flash"
        st.toast(
            f"欢迎使用 [`Langchain-HelpChat`](https://github.com/firewox/Langchain-HelpChat) ! \n\n"
            f"当前运行的模型`{default_model}`, 您可以开始提问了."
        )
        chat_box.init_session()

    chat_box.output_messages()
    dialogue_mode="LLM 对话"
    chat_input_placeholder = "请输入对话内容，换行请使用Shift+Enter "

    messages=[{"role":"user","content":"你是谁"},{"role":"assistant","content":"我是小助帮手"}]
    msg = {"model":"glm-4-flash",
           "messages":messages,
           "temperature":0.7,
           "max_tokens":None,
           "stream":True}
    if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
        chat_box.user_say(prompt)
        messages.append({"role":"user","content":f"{prompt}"})
        if dialogue_mode == "LLM 对话":
            chat_box.ai_say("正在思考...")

            def stream_chat(chat_box=chat_box):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                async def stream_chat1(chat_box=chat_box):
                    text = ""
                    # 获取异步生成器
                    response_generator = await openai_chat_v1(msg=msg)
                    # 使用 async for 遍历生成器
                    async for chunk in response_generator:
                        text += chunk
                        chat_box.update_msg(text)
                loop.run_until_complete(stream_chat1(chat_box=chat_box))
                loop.close()
            stream_chat(chat_box=chat_box)
            #logger.info(f"chat_box.context={text}")
            #chat_box.update_msg(streaming=False)  # 更新最终的字符串，去除光标

    now = datetime.now()
    with st.sidebar:

        cols = st.columns(2)
        export_btn = cols[0]
        if cols[1].button(
                "清空对话",
                use_container_width=True,
        ):
            chat_box.reset_history()
            st.experimental_rerun()

    export_btn.download_button(
        "导出记录",
        "".join(chat_box.export2md()),
        file_name=f"{now:%Y-%m-%d %H.%M}_对话记录.md",
        mime="text/markdown",
        use_container_width=True,
    )