import streamlit as st
from utils.logger import logger
from frontend.api.api_chat import api_chat


# 用户第一次进到页面，设falg=True，将历史聊天记录挂载到 st.session_state.messages 里
class dialogue_util:
    FLAG=True
    COUNT=0


# 实例化api请求接口
api_chat_instance:api_chat = api_chat()

# new UI layout
class dialogue:

    def create_new_dialogue(self):
        # 创建新的聊天记录
        history_name=api_chat_instance.create_new_dialogue(user_id=st.session_state.user_id)
        st.session_state.history_name = history_name
        st.session_state.history_name_list.append(history_name)
        # 清空聊天记录
        st.session_state.messages = api_chat_instance.system_prompt
        with st.balloons():
            st.rerun()

        #st.info('This is a purely informational message', icon="ℹ️")

    def dialogue_page(self):
        # 使用 session_state 来存储当前的选择
        if 'model_name' not in st.session_state or "model_list" not in st.session_state:
            # 查询可用的大模型
            model_list = api_chat_instance.get_model_list()
            st.session_state.model_name = model_list[0]
            st.session_state.model_list = [i for i in model_list]
        if "history_name" not in st.session_state or "history_name_list" not in st.session_state:
            # 给后端发送请求，挂载历史聊天记录的名称列表
            history_name_list = api_chat_instance.get_history_name_list(user_id=st.session_state.user_id)
            st.session_state.history_name = history_name_list[-1]
            st.session_state.history_name_list = [i for i in history_name_list]
            # Initialize chat history
            # 给后端发请求，挂载历史聊天记录
            messages = api_chat_instance.get_history_chat(user_id=st.session_state.user_id,user_name=st.session_state.user_name,history_name=st.session_state.history_name)
            st.session_state.messages = messages
        if "messages" not in st.session_state or len(st.session_state.messages)==0:
            # # 给后端发请求，挂载历史聊天记录
            messages = api_chat_instance.get_history_chat(user_id=st.session_state.user_id,user_name=st.session_state.user_name,history_name=st.session_state.history_name)
            st.session_state.messages = messages

        col1,col2 = st.columns([1,1])
        # col1
        #dialogue_util.COUNT+=1
        col1_selected = col1.selectbox(
            ":rainbow[LLM select]",
            (f"{ml}" for ml in st.session_state.model_list),
        )
        st.session_state.model_name = col1_selected
        # col2
        col2_placeholder = col2.empty()
        col2_selected = col2_placeholder.selectbox(":rainbow[History select]",
                                            (hnl for hnl in st.session_state.history_name_list),)
        if col2_selected!=st.session_state.history_name:
            api_chat_instance.history_name = col2_selected#match.group(1)
            st.session_state.history_name = col2_selected
            # # 给后端发请求，挂载历史聊天记录
            messages = api_chat_instance.get_history_chat(user_id=st.session_state.user_id,user_name=st.session_state.user_name,history_name=st.session_state.history_name)
            st.session_state.messages = messages


        st.title("🔗🦜 HelpChat App")
        # Display chat messages from history on app rerun
        if len(st.session_state.messages)!=0:
            # 清洗 messages ，当使用rag，上下文知识向量和query重新拼接到一起组成新prompt时，
            # 会出现 st.session_state.messages 里的user信息自动被更新注入。推测这是streamlit的bug，尚解决不了此bug，用清洗手段暂时回避
            st.session_state.messages = api_chat_instance.clean_messages(messages=st.session_state.messages)
            for index,message in enumerate(st.session_state.messages):
                if index>=2: # 省略跳过默认prompt记录，只显示用户和LLM交互的记录
                    with st.chat_message(name=message['role'],avatar=":material/face:"):
                        st.markdown(message["content"])

        # Accept user input
        # prompt = st.chat_input("最近怎么样？")
        left, right = st.columns([8,2])
        prompt = left.chat_input("最近怎么样？")
        if right.button("新建对话"):
            self.create_new_dialogue()
        if prompt:
            # Add user message to chat history
            logger.info(f"\n###query测试A={prompt}")
            st.session_state.messages.append({"role": "user", "content": prompt})
            logger.info(f"\n###query测试B={st.session_state.messages}")
            # Display user message in chat message container
            with st.chat_message(name="user",avatar=":material/face:"):
                st.markdown(prompt)

            # Display assistant response in chat message container
            with st.chat_message(name="assistant",avatar=":material/smart_toy:"):
                if len(st.session_state.messages)==0:
                    pass
                else:
                    # 给 LLM 发送消息
                    stream = api_chat_instance.get_chat(model_name=st.session_state.model_name,messages=st.session_state.messages)
                    response = st.write_stream(stream)

                    # 保存返回的聊天响应
                    st.session_state.messages.append({"role":"assistant","content":response})

            # 给后端发请求，实时保存聊天记录
            api_chat_instance.set_history_chat(user_id=st.session_state.user_id,user_name=st.session_state.user_name,messages=st.session_state.messages,history_name=st.session_state.history_name)





