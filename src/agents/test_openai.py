from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(model_name="gpt-4o-mini",
                 api_key="xxxxxxxxxxxxxxxx")
resp = llm.invoke(
    "Hello, from OpenAI via Langchain!. Explain me unit testing in 20 words.")
print(resp.content)


# Replace OpenAi Key and try below command
# python .\src\agents\test_openai.py
