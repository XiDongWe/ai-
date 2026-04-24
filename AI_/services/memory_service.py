import os
from langchain_community.embeddings import ZhipuAIEmbeddings
from services.vector_stores import VectorStoreService

class MemoryService(object):

    def __init__(self):
        embedding = ZhipuAIEmbeddings(
            model="embedding-3",
            api_key=os.getenv("ZHIPU_API_KEY"),
        )
        self.vs = VectorStoreService(embedding)

    def save(self,user_input,ai_output):
        text = f"用户: {user_input}\nAI: {ai_output}"
        self.vs.add(text)

    # 通过查询历史记录来返回上下文
    def get_context(self,user_input):
        # 获取上下文
        context = self.vs.search(user_input)
        return "\n".join(context)