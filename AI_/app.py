import os
import streamlit as st
from services.llm_service import LLMService
from services.memory_service import MemoryService
from services.prompt import ai_chain
from langchain_core.output_parsers import StrOutputParser


memory = MemoryService()
str_output = StrOutputParser()

st.title("AI猫娘")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "你是一个猫娘，性格温柔，是个傲娇，还有点笨"

# 侧边栏设置
st.sidebar.title("⚙️ 设置")
system_prompt = st.sidebar.text_area(
    "AI性格设定",
    value=st.session_state.system_prompt,
    height=120
)


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("请输入文本喵~")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 🔍 查记忆
    context = memory.get_context(user_input)

    chain = ai_chain(system_prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        answer = ""

        with st.spinner("少女祈祷中..."):
            for chunk in chain.stream({
                "context": context,
                "user_input": user_input
            }):
                answer += chunk
                placeholder.markdown(answer)

    # 确保历史消息还显示
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })



    # 💾 存记忆
    memory.save(user_input, answer)