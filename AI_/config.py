import os

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")


# Chroma
persist_directory = "./chroma_db"
collection_name = "rag"