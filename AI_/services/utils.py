import json
import os
import time

from services.file import read_uploaded_file  # noqa: F401

CHAT_DIR = "chat/"


def _ensure_dir():
    os.makedirs(CHAT_DIR, exist_ok=True)


def _chat_path(chat_id):
    return os.path.join(CHAT_DIR, f"{chat_id}.json")


def list_chats():
    """扫描 chat/ 目录，返回按修改时间排序的 [(chat_id, name)]"""
    _ensure_dir()
    chats = []
    for f in os.listdir(CHAT_DIR):
        if f.endswith(".json"):
            chat_id = f[:-5]
            try:
                with open(os.path.join(CHAT_DIR, f), "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                name = data.get("name", "新对话")
                mtime = os.path.getmtime(os.path.join(CHAT_DIR, f))
                chats.append((mtime, chat_id, name))
            except (json.JSONDecodeError, KeyError):
                continue
    chats.sort(key=lambda x: x[0])
    return [(cid, name) for _, cid, name in chats]


def create_chat():
    """创建新会话，返回 chat_id"""
    _ensure_dir()
    chat_id = str(int(time.time() * 1000))
    data = {"name": "新对话", "messages": []}
    with open(_chat_path(chat_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return chat_id


def load_chat(chat_id):
    """加载会话消息列表"""
    path = _chat_path(chat_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("messages", [])
    return []


def save_chat(chat_id, messages):
    """保存会话消息（保留原有名称）"""
    path = _chat_path(chat_id)
    name = "新对话"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        name = existing.get("name", "新对话")
    data = {"name": name, "messages": messages}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def rename_chat(chat_id, new_name):
    """重命名会话"""
    path = _chat_path(chat_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["name"] = new_name
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def delete_chat(chat_id):
    """删除会话文件"""
    path = _chat_path(chat_id)
    if os.path.exists(path):
        os.remove(path)
