from langchain_chroma import Chroma


class VectorStoreService(object):
    def __init__(self,embedding):
        # 嵌入模型
        self.embedding = embedding

        # 向量数据库
        self.db = Chroma(
            persist_directory="./chroma_db",
            embedding_function=self.embedding,
            collection_name="rag"
        )


    def add(self, text):
        self.db.add_texts([text])
          # 保存数据

    def search(self, query, k=3):
        docs = self.db.similarity_search(query, k=k)
        return [d.page_content for d in docs]