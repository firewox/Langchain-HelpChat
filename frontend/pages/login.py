# @Time  :2024/12/16 11:53
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import streamlit as st
from frontend.api.api_login import api_login

api_login_instance:api_login = api_login()

# 登录界面
class login:
    def login_pae(self):
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
            else:
                st.warning("请输入用户名和密码！")