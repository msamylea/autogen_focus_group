from langchain_openai import ChatOpenAI
from openai import OpenAI

llama_model = "llama3:latest"  # l3custom  (see README for tuning options)

completions_model = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

model = ChatOpenAI(model="llama3:latest", base_url="http://localhost:11434/v1", api_key="ollama")