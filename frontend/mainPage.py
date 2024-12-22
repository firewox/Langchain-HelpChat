# @Time  :2024/12/5 23:19
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import streamlit as st
from pages.dialogue import dialogue
from pages.dialogue_knowledge import dialogue_knowledge
from pages.dialogue_knowledge_v2 import dialogue_knowledge_v2
from pages.login import login
from streamlit_option_menu import option_menu
import os
from frontend.api.api_login import api_login
from frontend.configs.frontend_config import VERSION,LOGO_IMG

api_login_instance:api_login = api_login()

def mainPage():

    pages = {
        "大模型对话": {
            "icon": os.path.join("imgs", "chat_assistant_icon.png"),
            "func": dialogue().dialogue_page,
        },
        "知识库助手": {
            "icon": os.path.join("imgs", "chat_assistant_icon2.png"),
            "func": dialogue_knowledge().dialogue_knowledge_page,
        },
        "知识库GPT": {
            "icon": os.path.join("imgs", "chat_assistant_icon2.png"),
            "func": dialogue_knowledge_v2().dialogue_knowledge_v2_page,
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
            default_index=default_index,
        )

    if selected_page in pages:
        pages[selected_page]["func"]()



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
    #检查用户登录状态
    if "user_id" not in st.session_state or "user_name" not in st.session_state:
        login().login_pae()  # 显示登录界面
    else:
        mainPage()  # 显示主界面
