from langchain_groq import ChatGroq
from backend.config.settings import GROQ_API_KEY

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)

def planner_agent(user_query):

    prompt = f"""
    You are a Planner Agent.

    Break the user query into workflow steps.

    User Query:
    {user_query}

    Return only the steps.
    """

    response = llm.invoke(prompt)

    return response.content


