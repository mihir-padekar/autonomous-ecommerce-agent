from backend.llm.llm import llm


def followup_agent(
    query,
    history
):

    prompt = f"""
You are an E-Commerce Operations Assistant.

Conversation History:
{history}

Current Question:
{query}

Instructions:

- Use the conversation history.
- Answer only the user's question.
- Do not repeat the entire previous answer.
- Keep response under 100 words.
- If the user asks for a summary, provide a concise summary.
- If the user asks for recommendations, provide recommendations.
- If information is unavailable, say so.
"""

    response = llm.invoke(prompt)

    return response.content