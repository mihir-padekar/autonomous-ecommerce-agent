import json

from backend.llm.llm import llm

from backend.config.query_metadata import QUERY_METADATA


#planner helper 

def build_workflow_prompt():

    workflows = []

    for function_name, metadata in QUERY_METADATA.items():

        workflows.append(

            f"""
Function:
{function_name}

Workflow:
{metadata['workflow']}
"""
        )

    return "\n".join(workflows)


def planner_agent(
    query,
    history=None
):

    if history is None:
        history = []

    workflow_catalog = build_workflow_prompt()

    prompt = f"""
You are an E-Commerce Operations Workflow Router.

Conversation History:

{history}

Current User Query:

{query}

Available Query Functions:

{workflow_catalog}

Instructions:

1. Choose the BEST matching query function.

2. If the user asks about:
- refund policy
- return policy
- cancellation policy
- delivery policy
- SLA policy
- escalation policy
- company policies
- "what is...", "explain...", or "how does the policy work"

then ALWAYS choose:

policy_lookup

3. Choose database query functions ONLY when the user is asking for operational data such as:
- delayed orders
- complaints
- tickets
- dashboard
- warehouse summary
- product delays

4. Return ONLY valid JSON.

Format:

{{
    "query_function": "..."
}}
"""

    response = llm.invoke(
        prompt
    )

    content = response.content.strip()

    print(content)

    try:
        result = json.loads(content)

        if result.get("query_function") not in QUERY_METADATA:
            return {
                "query_function": "unknown"
            }

        return result

    except Exception:

        return {
            "query_function": "unknown"
        }