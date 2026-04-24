import os
import streamlit as st
from services.llm_service import get_llm
from services.memory_service import MemoryService

# 检查环境变量
if not os.getenv("DEEPSEEK_API_KEY"):
    st.error("❌ 未设置 DEEPSEEK_API_KEY 环境变量，请在终端运行：\n\n```\nset DEEPSEEK_API_KEY=你的key\n```")
    st.stop()
if not os.getenv("ZHIPU_API_KEY"):
    st.error("❌ 未设置 ZHIPU_API_KEY 环境变量（用于向量记忆），请在终端运行：\n\n```\nset ZHIPU_API_KEY=你的key\n```")
    st.stop()

llm = get_llm()
memory = MemoryService()

st.title("🧠 AI聊天（带长期记忆）")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("请输入文本喵~")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 🔍 查记忆
    context = memory.get_context(user_input)

    prompt = f"""
    以下是历史对话：
    {context}

    用户问题：
    {user_input}
    """

    res = llm.invoke(prompt)
    answer = res.content

    st.chat_message("assistant").write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

    # 💾 存记忆
    memory.save(user_input, answer)