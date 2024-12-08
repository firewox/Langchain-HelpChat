# @Time  :2024/12/5 23:19
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import streamlit as st
from webui_pages.dialogue import dialogue_knowledge_page,dialogue_page_v1
from streamlit_option_menu import option_menu
import os
from backend.configs.model_config import VERSION
from configs.project_configs import LOGO_IMG
from utils.utils import api_address
from frontend.api_frontend.api_frontend_chat import api_frontend_chat
from frontend.api_frontend.api_frontend_knowledge_chat import api_frontend_knowledge_chat


if __name__ == "__main__":

    st.set_page_config(
        "Langchain-HelpChat WebUI",
        os.path.join("imgs", "icon_v1.png"),
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/firewox/Langchain-HelpChat',
            'Report a bug': "https://github.com/firewox/Langchain-HelpChat/issues",
            'About': f"""欢迎使用 Langchain-HelpChat WebUI {VERSION}！"""
        }
    )

    pages = {
        "大模型对话": {
            "icon": os.path.join("imgs", "chat_assistant_icon.png"),#"chat",
            #"func": dialogue_page,
            "func": dialogue_page_v1,
        },
        "知识库助手": {
            "icon": os.path.join("imgs", "chat_assistant_icon2.png"),#"chat",
            #"func": dialogue_page,
            "func": dialogue_knowledge_page,
        }
    }

    with st.sidebar:
        st.image(LOGO_IMG,use_column_width=True)
        st.caption(f"""<p align="right">当前版本：{VERSION}</p>""",unsafe_allow_html=True,)
        options = list(pages)
        icons = [x["icon"] for x in pages.values()]

        default_index = 0
        selected_page = option_menu(
            "",
            options=options,
            icons=icons,
            # menu_icon="chat-quote",
            default_index=default_index,
        )

    if selected_page in pages:
        if pages[selected_page]["func"]==dialogue_page_v1:
            dialogue_page_v1()
        elif pages[selected_page]["func"]==dialogue_knowledge_page:
            dialogue_knowledge_page()
        else:
            pages[selected_page]["func"]()
