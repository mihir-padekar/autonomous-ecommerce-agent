# test_summary.py

from backend.agents.executive_summary_agent import executive_summary_agent

state = {

    "workflow_type": "ticket_analysis",

    "analysis": {
        "open_tickets": 64,
        "critical_tickets": 6,
        "risk_level": "MEDIUM"
    },

    "compliance_status": "AT_RISK",

    "compliance_score": 70,

    "policy_source": "escalation_rules.pdf"
}

result = executive_summary_agent(state)

print(result["executive_summary"])