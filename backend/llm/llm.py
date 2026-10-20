from langchain_groq import ChatGroq

from backend.config.settings import GROQ_API_KEY


llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    api_key=GROQ_API_KEY,
    temperature=0.2
)