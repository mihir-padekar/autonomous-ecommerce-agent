from backend.llm.llm import llm


def chat_response_agent(state):

    prompt = f"""
You are an E-Commerce Operations Assistant.

Conversation History:
{state.get("history", [])}

User Query:
{state["query"]}

Analysis:
{state.get("analysis", "No operational analysis available.")}

Policy:
{state.get("policy", "")}

Executive Summary:
{state.get("executive_summary", "")}

Instructions:

- Answer naturally like ChatGPT.
- Be concise.
- Mention important metrics.
- When answering a policy or SLA query, strictly preserve and state the exact numbers, time windows (e.g., days/hours), conditions, and approval tiers from the Policy context.
- Do NOT contradict or omit specific figures present in the policy.
- Do NOT generate a report.
- Do NOT use headings.
- Maximum 150 words.
"""

    response = llm.invoke(prompt)

    state["chat_response"] = response.content

    return state