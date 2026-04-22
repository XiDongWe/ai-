from langchain_classic.chains.constitutional_ai.prompts import examples
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import ZhipuAIEmbeddings
from langchain_core.prompts import PromptTemplate,FewShotPromptTemplate

# 大语言模型
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key="sk-9dfd7b0a025f4008815a4153faf482e6",
    openai_api_base="https://api.deepseek.com"
)

# 嵌入模型
embedding = ZhipuAIEmbeddings(
    model="embedding-3",
    api_key="980a601be4844ff58251058d5be9cca6.7X1OhYSv1EUfb9SN",
    api_base="https://api.deepseek.com"
)


example_prompt = PromptTemplate.from_template("名字:{name},作者:{author}")
example_data = [
    {
        "name": "《三体》",
        "author": "刘慈欣"
    }
]
prompt = FewShotPromptTemplate(
    example_prompt=example_prompt,              # 示例提示词
    examples=example_data,                      # 示例内容
    prefix="我给你示例，按照示例返回作者名字",       # 前缀
    suffix="告诉我{name}的作者",                  # 后缀
    input_variables=["name"]                    # 输入变量
)

chain = prompt | llm

res = chain.stream(input={"name" : "西游记"})
for chunk in res :
    print(chunk.content,end="",flush=True)

