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
2. Return ONLY JSON.
3. No explanation.

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

        return json.loads(content)

    except Exception:

        raise ValueError(
            f"Planner failed to parse JSON: {content}"
        )