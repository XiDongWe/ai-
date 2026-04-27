from langchain_core.prompts import PromptTemplate,ChatPromptTemplate
from services.llm_service import LLMService
from langchain_core.output_parsers import StrOutputParser

def ai_chain(system):

    str_output = StrOutputParser()
    llm = LLMService().get_llm()
    parser = StrOutputParser()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("system", "历史对话：{context}"),
        ("human", "{user_input}"),
        ("system", """
1. 要完全符合用户的system需求
2. 严格根据历史对话回答
3. 聊天内容多一点，像正常聊天一样

""")
    ])
    chain = prompt | llm | str_output

    return chain