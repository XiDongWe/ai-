import os
import time
import streamlit as st

from services.utils import list_chats, load_chat, save_chat, create_chat, delete_chat, rename_chat
from services.llm_service import LLMService
from services.memory_service import MemoryService
from services.prompt import ai_chain

memory = MemoryService()

st.title("AI猫娘")

# ======== 初始化 Session State ========
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "你是一个猫娘，性格温柔，是个傲娇，还有点笨"
if "current_chat_id" not in st.session_state:
    chats = list_chats()
    if chats:
        st.session_state.current_chat_id = chats[0][0]
    else:
        st.session_state.current_chat_id = create_chat()
if "messages" not in st.session_state:
    st.session_state.messages = load_chat(st.session_state.current_chat_id)

# ======== 侧边栏 ========
st.sidebar.title("⚙️ 设置")
system_prompt = st.sidebar.text_area(
    "AI性格设定",
    value=st.session_state.system_prompt,
    height=120
)

st.sidebar.title("💬 历史对话")

# 新建会话按钮
if st.sidebar.button("➕ 新建会话", use_container_width=True):
    new_id = create_chat()
    st.session_state.current_chat_id = new_id
    st.session_state.messages = []
    st.rerun()

# 显示所有会话（带删除按钮）
chats = list_chats()
for cid, cname in chats:
    # 当前会话加个标记
    display_name = f"📌 {cname}" if cid == st.session_state.current_chat_id else cname
    cols = st.sidebar.columns([5, 2])
    with cols[0]:
        if st.button(display_name, key=f"chat_{cid}", use_container_width=True):
            st.session_state.current_chat_id = cid
            st.session_state.messages = load_chat(cid)
            st.rerun()
    with cols[1]:
        if st.button("🗑️", key=f"del_{cid}"):
            delete_chat(cid)
            if cid == st.session_state.current_chat_id:
                remaining = list_chats()
                if remaining:
                    st.session_state.current_chat_id = remaining[0][0]
                else:
                    st.session_state.current_chat_id = create_chat()
                st.session_state.messages = load_chat(st.session_state.current_chat_id)
            st.rerun()

saved_placeholder = st.sidebar.empty()

# ======== 主区域 ========
# 显示当前会话消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 聊天输入
user_input = st.chat_input("请输入文本喵~")

if user_input:
    # 显示用户消息
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 查记忆
    context = memory.get_context(user_input)
    chain = ai_chain(system_prompt)

    # AI流式响应
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

    st.session_state.messages.append({"role": "assistant", "content": answer})

    # 保存到文件
    save_chat(st.session_state.current_chat_id, st.session_state.messages)

    # 首次对话：用LLM自动生成标题
    if len(st.session_state.messages) == 2:
        try:
            llm = LLMService().get_llm()
            name_prompt = f"用3-8个中文词总结这段对话的核心主题作为标题：\n用户：{user_input}\nAI：{answer}"
            chat_name = llm.invoke(name_prompt).content.strip().strip('"').strip("'")
            if chat_name:
                rename_chat(st.session_state.current_chat_id, chat_name)
        except Exception:
            pass  # 命名失败就保留默认名

    # 存记忆
    saved = memory.save(user_input, answer)
    if not saved:
        saved_placeholder.warning("⚠️ 内容已存在，跳过存储")
    else:
        saved_placeholder.success("✅ 已加入记忆")
    time.sleep(1)
    saved_placeholder.empty()
