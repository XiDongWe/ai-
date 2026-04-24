from pickle import FRAME

from langchain_classic.chains.constitutional_ai.prompts import examples
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import ZhipuAIEmbeddings
from langchain_core.prompts import PromptTemplate,FewShotPromptTemplate,ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda




DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
# 嵌入模型
embedding = ZhipuAIEmbeddings(
    model="embedding-3",
    api_key="",
    api_base="https://api.deepseek.com"
)




chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个猫娘"),
        MessagesPlaceholder("history"),
        ("human", "随便推荐一个工作，告诉我名字就行"),
    ]
)

history_data = [
    ("user", "我叫西东温"),
    ("ai", "好的"),

]

second_prompt = PromptTemplate.from_template(
    "介绍一下{job}"
)

str_parse = StrOutputParser()

myfuc = RunnableLambda(lambda ai_msg: {"job" : ai_msg.content})

chain = chat_prompt | llm | myfuc | second_prompt | llm | str_parse

res = chain.stream({"history" : history_data})
for chunk in res :
    print(chunk,end="",flush=True)

