from langchain_ollama import ChatOllama

llm = ChatOllama(model="mistral:latest")
resp = llm.invoke("Hello, from Ollama via Langchain! keep it to one sentence.")
print(resp.content)


# python src\agents\test_open_ollama.py
