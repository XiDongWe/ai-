import os
import time
import streamlit as st

from services.utils import list_chats, load_chat, save_chat, create_chat, delete_chat, rename_chat, read_uploaded_file
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
if "generating" not in st.session_state:
    st.session_state.generating = False
if "stop_requested" not in st.session_state:
    st.session_state.stop_requested = False
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = set()
if "uploaded_file_content" not in st.session_state:
    st.session_state.uploaded_file_content = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "pending_response" not in st.session_state:
    st.session_state.pending_response = False
if "pending_user_input" not in st.session_state:
    st.session_state.pending_user_input = None
if "pending_context" not in st.session_state:
    st.session_state.pending_context = None

# ======== 处理停止请求 ========
stop_triggered = st.session_state.pop("stop_requested", False)
if stop_triggered and not st.session_state.get("pending_response", False):
    for i in range(len(st.session_state.messages) - 1, -1, -1):
        if st.session_state.messages[i]["role"] == "assistant":
            st.session_state.messages[i]["content"] += "\n\n🛑 已停止生成"
            save_chat(st.session_state.current_chat_id, st.session_state.messages)
            break

# ======== 侧边栏 ========
st.sidebar.title("⚙️ 设置")
system_prompt = st.sidebar.text_area(
    "AI性格设定",
    value=st.session_state.system_prompt,
    height=120
)

# 停止生成按钮（仅在生成时显示）
if st.session_state.generating:
    st.sidebar.button("🛑 停止生成", use_container_width=True, type="primary",
                       on_click=lambda: setattr(st.session_state, "stop_requested", True))

# ======== 侧边栏：文件上传 ========
st.sidebar.divider()
uploaded_file = st.sidebar.file_uploader(
    "📎 上传文件（txt / md / pdf / csv / docx）",
    type=['txt', 'md', 'pdf', 'csv', 'docx', 'py', 'json']
)

# 已加载的文件指示 + 清除
if st.session_state.uploaded_file_name:
    cols = st.sidebar.columns([5, 1])
    with cols[0]:
        st.sidebar.caption(f"📎 {st.session_state.uploaded_file_name}")
    with cols[1]:
        if st.sidebar.button("✕", key="clear_file"):
            st.session_state.uploaded_file_content = None
            st.session_state.uploaded_file_name = None
            st.rerun()

# 处理文件上传
if uploaded_file is not None and not st.session_state.generating:
    file_key = f"{uploaded_file.name}_{uploaded_file.size}"
    if file_key not in st.session_state.uploaded_files:
        st.session_state.uploaded_files.add(file_key)
        file_content = read_uploaded_file(uploaded_file)
        if file_content and not file_content.startswith("【"):
            if len(file_content) > 10000:
                file_content = file_content[:10000] + "\n\n...（文件过长，已截断）"
            st.session_state.uploaded_file_content = file_content
            st.session_state.uploaded_file_name = uploaded_file.name
            st.rerun()
        elif file_content:
            st.sidebar.error(file_content)

# ======== 侧边栏：历史对话 ========
st.sidebar.title("💬 历史对话")

# 新建会话按钮
if st.sidebar.button("➕ 新建会话", use_container_width=True):
    new_id = create_chat()
    st.session_state.current_chat_id = new_id
    st.session_state.messages = []
    st.session_state.uploaded_file_content = None
    st.session_state.uploaded_file_name = None
    st.rerun()

# 显示所有会话（带删除按钮）
chats = list_chats()
for cid, cname in chats:
    # 当前会话加个标记
    display_name = f"📌 {cname}" if cid == st.session_state.current_chat_id else cname
    cols = st.sidebar.columns([6, 2])
    with cols[0]:
        if st.button(display_name, key=f"chat_{cid}", use_container_width=True):
            st.session_state.current_chat_id = cid
            st.session_state.messages = load_chat(cid)
            st.session_state.uploaded_file_content = None
            st.session_state.uploaded_file_name = None
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
# 显示当前会话消息（所有消息渲染在聊天框之前）
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
# 处理挂起的 AI 响应（在聊天框上方渲染）
if st.session_state.pop("pending_response", False):
    st.session_state.generating = True
    pending_input = st.session_state.pending_user_input
    pending_context = st.session_state.pending_context
    st.session_state.pending_user_input = None
    st.session_state.pending_context = None

    with st.chat_message("assistant"):
        placeholder = st.empty()
        if stop_triggered:
            answer = "🛑 已停止生成"
            placeholder.markdown(answer)
        else:
            answer = ""
            with st.spinner("少女祈祷中..."):
                chain = ai_chain(system_prompt)
                for chunk in chain.stream({
                    "context": pending_context,
                    "user_input": pending_input
                }):
                    answer += chunk
                    placeholder.markdown(answer)
    st.session_state.generating = False

    st.session_state.messages.append({"role": "assistant", "content": answer})
    save_chat(st.session_state.current_chat_id, st.session_state.messages)

    # 首次对话：用LLM自动生成标题
    if len(st.session_state.messages) == 2:
        try:
            llm = LLMService().get_llm()
            name_prompt = f"严格用3-8个中文词总结这段对话的核心主题作为标题：\n用户：{pending_input}\nAI：{answer}"
            chat_name = llm.invoke(name_prompt).content.strip().strip('"').strip("'")
            if chat_name:
                rename_chat(st.session_state.current_chat_id, chat_name)
        except Exception:
            pass

    # 存记忆
    saved = memory.save(pending_input, answer)
    if not saved:
        saved_placeholder.warning("⚠️ 内容已存在，跳过存储")
    else:
        saved_placeholder.success("✅ 已加入记忆")
    time.sleep(1)
    saved_placeholder.empty()
    st.rerun()

# ======== 底部：聊天输入 ========
user_input = st.chat_input("请输入文本喵~")

# 用户输入处理 -> 设置挂起，下次渲染时生成 AI 响应
if user_input and not st.session_state.generating:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 构建上下文（记忆 + 上传文件）
    context = memory.get_context(user_input)
    if st.session_state.uploaded_file_content:
        file_ctx = f"\n用户上传的文件《{st.session_state.uploaded_file_name}》内容：\n{st.session_state.uploaded_file_content}"
        context = (context or "") + file_ctx

    st.session_state.pending_response = True
    st.session_state.pending_user_input = user_input
    st.session_state.pending_context = context
    st.rerun()
