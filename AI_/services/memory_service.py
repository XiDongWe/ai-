import os
from langchain_community.embeddings import ZhipuAIEmbeddings
from .vector_stores import VectorStoreService

class MemoryService(object):

    def __init__(self):
        embedding = ZhipuAIEmbeddings(
            model="embedding-3",
            api_key=os.getenv("ZHIPU_API_KEY"),
        )
        self.vs = VectorStoreService(embedding)

    def save(self,user_input,ai_output):

        docs = self.vs.db.similarity_search_with_score(user_input, k=1)

        if docs:
            doc, score = docs[0]

            # 分数越小越相似（Chroma默认）
            if score < 0.1:
                return  False # 太像了，不存



        self.vs.db.add_texts(
            [user_input, ai_output],
            metadatas=[
                {"role": "user"},
                {"role": "assistant"}
            ]
        )
        return True

    # 通过查询历史记录来返回上下文
    def get_context(self,user_input):
        # 获取上下文
        context = self.vs.search(user_input)
        return "\n".join(context)