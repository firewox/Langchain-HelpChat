# @Time  :2024/12/7 11:33
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import streamlit as st
from frontend.api.api_knowledge import api_knowledge
from frontend.api.api_chat import api_chat
from utils.logger import logger


# 实例化api请求接口
api_chat_instance:api_chat = api_chat()
api_knowledge_instance:api_knowledge = api_knowledge()

# new UI layout
class dialogue_knowledge:

    def create_new_dialogue(self):
        # 创建新的聊天记录
        history_name=api_chat_instance.create_new_dialogue(user_id=st.session_state.user_id)
        st.session_state.history_name = history_name
        st.session_state.history_name_list.append(history_name)
        # 清空聊天记录
        st.session_state.messages = api_chat_instance.system_prompt
        with st.balloons():
            st.rerun()

    def col3_func(self):
        st.balloons()

    def dialogue_knowledge_page(self):
        # 使用 session_state 来存储当前的选择
        if 'model_name' not in st.session_state or "model_list" not in st.session_state:
            # 给后端发请求，查询可用的大模型
            model_list = api_chat_instance.get_model_list()
            st.session_state.model_name = model_list[0]
            st.session_state.model_list = model_list
        if "history_name" not in st.session_state or "history_name_list" not in st.session_state:
            # 给后端发送请求，挂载历史聊天记录的名称列表
            history_name_list = api_chat_instance.get_history_name_list(user_id=st.session_state.user_id)
            st.session_state.history_name = history_name_list[-1]
            st.session_state.history_name_list = history_name_list
            # Initialize chat history
            # # 给后端发请求，挂载历史聊天记录
            messages = api_chat_instance.get_history_chat(user_id=st.session_state.user_id,user_name=st.session_state.user_name,history_name=st.session_state.history_name)
            st.session_state.messages = messages
        if "knowledge_name" not in st.session_state or "knowledge_name_list" not in st.session_state:
            knowledge_name_list = api_knowledge_instance.get_knowledge_name_list(user_id=st.session_state.user_id)
            st.session_state.knowledge_name = knowledge_name_list[0]
            st.session_state.knowledge_name_list = knowledge_name_list
        if len(st.session_state.messages)==0:
            # # 给后端发请求，挂载历史聊天记录
            messages = api_chat_instance.get_history_chat(user_id=st.session_state.user_id,user_name=st.session_state.user_name,history_name=st.session_state.history_name)
            st.session_state.messages = messages

        col1,col2,col3,col4 = st.columns([1,1,1,1])
        col1_placeholder = col1.empty()
        col2_placeholder = col2.empty()
        # col3_placeholder = col3.empty()
        col4_placeholder = col4.empty()
        #
        # col1
        col1_selected = col1_placeholder.selectbox(
            ":rainbow[LLM Select]",
            (f"{ml}" for ml in st.session_state.model_list),
        )
        api_knowledge_instance.model_name = col1_selected
        st.session_state.model_name = col1_selected
        # col2
        col2_selected = col2_placeholder.selectbox(":rainbow[History Select]",(hnl for hnl in st.session_state.history_name_list),)
        if col2_selected!=st.session_state.history_name:
            api_chat_instance.history_name = col2_selected
            st.session_state.history_name = col2_selected
            # # 给后端发请求，挂载历史聊天记录
            messages = api_chat_instance.get_history_chat(user_id=st.session_state.user_id,user_name=st.session_state.user_name,history_name=st.session_state.history_name)
            st.session_state.messages=messages
            logger.info(f"\n\n挂载历史聊天记录B={messages}")
        # col3
        if col3.button("上传文件"):
            self.col3_func()
        # col4
        col4_selected = col4_placeholder.selectbox(":rainbow[Knowledge Books]",(i for i in st.session_state.knowledge_name_list),)
        api_knowledge_instance.knowledge_name = col4_selected
        st.session_state.knowledge_name = col4_selected


        st.title("🔗🦜 HelpChat App")
        # Display chat messages from history on app rerun
        if len(st.session_state.messages)!=2:
            # 清洗 messages ，当使用rag，上下文知识向量和query重新拼接到一起组成新prompt时，
            # 会出现 st.session_state.messages 里的user信息自动被更新注入。推测这是streamlit的bug，尚解决不了此bug，用清洗手段暂时回避
            st.session_state.messages = api_chat_instance.clean_messages(messages=st.session_state.messages)
            for index,message in enumerate(st.session_state.messages):
                if index>=2: # 省略跳过默认prompt记录，只显示用户和LLM交互的记录
                    with st.chat_message(name=message['role'],avatar=":material/face:"):
                        st.markdown(message["content"])

        # Accept user input
        left, right = st.columns([8,2])
        prompt = left.chat_input("最近怎么样？")
        if right.button("新建对话"):
            self.create_new_dialogue()
        if prompt:
            logger.info(f"\n\n###query测试A={prompt}")
            st.session_state.messages.append({"role": "user", "content": prompt})
            logger.info(f"\n\n###query测试B={st.session_state.messages}")
            # Display user message in chat message container
            with st.chat_message(name="user",avatar=":material/face:"):
                st.markdown(prompt)

            # Display assistant response in chat message container
            with st.chat_message(name="assistant",avatar=":material/smart_toy:"):
                if len(st.session_state.messages)==0:
                    pass
                else:
                    # 给后端发请求，发送消息
                    stream = api_chat_instance.get_knowledge_chat(user_id=st.session_state.user_id,
                                                                   knowledge_vector_name=st.session_state.knowledge_name,
                                                                  messages=st.session_state.messages.copy(),
                                                                  model_name=st.session_state.model_name)
                    response = st.write_stream(stream)

                    # 保存返回的聊天响应
                    st.session_state.messages.append({"role": "assistant", "content": response})

                # 给后端发请求，实时保存聊天记录
                api_chat_instance.set_history_chat(user_id=st.session_state.user_id,user_name=st.session_state.user_name,history_name=st.session_state.history_name,messages=st.session_state.messages)

