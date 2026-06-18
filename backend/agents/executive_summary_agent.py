from backend.llm.llm import llm


def executive_summary_agent(state):

    analysis = state["analysis"]

    compliance_status = state.get("compliance_status","UNKNOWN")

    compliance_score = state.get("compliance_score",0)

    policy_source = state["policy_source"]

    workflow = state["workflow_type"]

    if state["workflow_type"] == "dashboard_analysis":

        analysis = state["analysis"]

        state["executive_summary"] = f"""
    Operations are currently under pressure due to elevated delivery delays.
    {analysis['top_warehouse']} is the most affected warehouse,
    while {analysis['top_product']} is the most delayed product.
    The most common customer issue is
    {analysis['top_complaint']}.
    Management should prioritize logistics improvements.
    """

        return state
    
    elif state["workflow_type"] == "product_analysis":

        analysis = state["analysis"]

        state["executive_summary"] = (

            f"{analysis['top_product']} is currently the most delayed "
            f"product with {analysis['delayed_count']} delayed orders "
            f"and an average delay of "
            f"{analysis['avg_delay_days']} days."

        )

        return state
    
    else:

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
