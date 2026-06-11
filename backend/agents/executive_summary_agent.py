from backend.llm.llm import llm


def executive_summary_agent(state):

    analysis = state["analysis"]

    compliance_status = state["compliance_status"]

    compliance_score = state["compliance_score"]

    policy_source = state["policy_source"]

    workflow = state["workflow_type"]

    prompt = f"""
You are a Senior E-Commerce Operations Analyst.

Workflow:
{workflow}

Operational Metrics:
{analysis}

Compliance Status:
{compliance_status}

Compliance Score:
{compliance_score}

Policy Source:
{policy_source}

Your task is to interpret the operational situation.

Explain:

1. What the metrics indicate.
2. Which business area is most affected.
3. The primary operational risk.
4. One management recommendation.

Rules:
- Use professional business language.
- Do not simply repeat the metrics.
- Mention numbers only if important.
- Return a single executive summary paragraph.
- Maximum 80 words.
"""

    response = llm.invoke(prompt)

    state["executive_summary"] = response.content

    return state