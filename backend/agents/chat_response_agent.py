from backend.llm.llm import llm


def chat_response_agent(state):

    prompt = f"""
You are an E-Commerce Operations Assistant.

Conversation History:
{state.get("history", [])}

User Query:
{state["query"]}

Analysis:
{state["analysis"]}

Policy:
{state.get("policy", "")}

Executive Summary:
{state.get("executive_summary", "")}

Instructions:

- Answer naturally like ChatGPT.
- Be concise.
- Mention important metrics.
- Use policy context if relevant.
- Do NOT generate a report.
- Do NOT use headings.
- Maximum 150 words.
"""

    response = llm.invoke(prompt)

    state["chat_response"] = response.content

    return state