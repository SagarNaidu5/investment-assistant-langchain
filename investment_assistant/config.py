from langchain_ollama import ChatOllama
import os

def get_llm(model_name=None):
    if model_name is None:
        model_name = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")  # Use env var or default to Docker service name

    return ChatOllama(
        model=model_name,
        temperature=0.1,
        base_url=base_url
    )
