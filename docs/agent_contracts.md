# Agent Contracts

## Planner Agent

Purpose:
Understand user query and decide workflow.

Input:
{
  "query": "Find delayed orders"
}

Output:
{
  "workflow_type": "delayed_orders"
}


--------------------------------------------

## Database Agent

Purpose:
Fetch data from PostgreSQL.

Input:
{
  "workflow_type": "delayed_orders"
}

Output:
{
  "orders": [
    {
      "order_id": 101,
      "delay_days": 5
    }
  ]
}


--------------------------------------------

## Policy Agent

Purpose:
Retrieve business policies using RAG.

Input:
{
  "workflow_type": "delayed_orders"
}

Output:
{
  "policy": "Orders delayed more than 3 days must be escalated."
}


--------------------------------------------

## Analysis Agent

Purpose:
Analyze retrieved data.

Input:
{
  "orders": [...],
  "policy": "..."
}

Output:
{
  "critical_orders": 4,
  "sla_violations": 8
}


--------------------------------------------

## Action Agent

Purpose:
Generate actions.

Input:
{
  "critical_orders": 4
}

Output:
{
  "action": "Escalation ticket created"
}


--------------------------------------------

## Report Agent

Purpose:
Generate final response.

Input:
{
  "analysis": "...",
  "action": "..."
}

Output:
{
  "report": "25 delayed orders found. 8 SLA violations detected."
}