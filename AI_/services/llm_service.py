import os
from langchain_openai import ChatOpenAI

class LLMService(object):
    def __init__(self):
        pass


    def get_llm(self):
        return ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base="https://api.deepseek.com"
            )
