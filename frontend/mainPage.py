# @Time  :2024/12/5 23:19
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import streamlit as st
import pages.dialogue as dialogue
import pages.dialogue_knowledge as dialogue_knowledge
from streamlit_option_menu import option_menu
import os
from frontend.api.api_login import api_login
from frontend.configs.frontend_config import VERSION,LOGO_IMG

api_login_instance:api_login = api_login()

def mainPage():

    pages = {
        "大模型对话": {
            "icon": os.path.join("imgs", "chat_assistant_icon.png"),
            "func": dialogue.dialogue_page,
        },
        "知识库助手": {
            "icon": os.path.join("imgs", "chat_assistant_icon2.png"),
            "func": dialogue_knowledge.dialogue_knowledge_page,
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


# 登录界面
def login_page():
    st.title("登录")

    # 输入框
    user_name = st.text_input("用户名", "")
    password = st.text_input("密码", "", type="password")
    # 登录按钮
    if st.button("登录"):
        if user_name!="" and password!="":
            resu = api_login_instance.login(user_name=user_name, password=password)
            if resu:
                st.success("登录成功！")
                st.session_state.user_id = resu.get("user_id")
                st.session_state.user_name = resu.get("user_name")
                # 刷新页面，使主页面显示
                st.rerun()  # 刷新页面
            else:
                st.warning("用户名或密码错误！")

def main():
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

    # 检查用户登录状态
    if "user_id" not in st.session_state or "user_name" not in st.session_state:
        login_page()  # 显示登录界面
    else:
        mainPage()  # 显示主界面

if __name__ == "__main__":
    main()
