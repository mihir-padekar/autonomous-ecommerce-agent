def report_agent(state):
    workflow = state["workflow_type"]
    analysis = state["analysis"]
    display_policy = state["policy"]

    if len(display_policy) > 500:
        display_policy = display_policy[:500] + "..."

    if workflow == "ticket_analysis":
        title = "TICKET OPERATIONS REPORT"

    elif workflow == "complaint_analysis":
        title = "COMPLAINT ANALYSIS REPORT"

    elif workflow == "delayed_orders":
        title = "DELAYED ORDER ANALYSIS REPORT"

    if workflow == "delayed_orders":
        report = f"""
        
        
==================================================
{title}
==================================================

Query:
{state['query']}

--------------------------------------------------
EXECUTIVE SUMMARY
--------------------------------------------------

{state['executive_summary']}

--------------------------------------------------
KEY METRICS
--------------------------------------------------

Open Tickets          : {analysis['open_tickets']}
Critical Tickets      : {analysis['critical_tickets']}
High Priority Tickets : {analysis['high_priority_tickets']}
Busiest Team          : {analysis['busiest_team']}
Risk Level            : {analysis['risk_level']}

--------------------------------------------------
COMPLIANCE ASSESSMENT
--------------------------------------------------

Compliance Score      : {state['compliance_score']}%
Compliance Status     : {state['compliance_status']}

Reason:
{state['compliance_reason']}

--------------------------------------------------
POLICY REFERENCE
--------------------------------------------------

Source:
{state['policy_source']}

Page:
{state['policy_page'] + 1}

Relevant Rule:
{display_policy}

==================================================
"""
        # Complaint Analysis
    elif workflow == "complaint_analysis":
        report = f"""
==================================================
{title}
==================================================

Query:
{state['query']}

--------------------------------------------------
EXECUTIVE SUMMARY
--------------------------------------------------

{state['executive_summary']}

--------------------------------------------------
KEY METRICS
--------------------------------------------------

Open Tickets          : {analysis['open_tickets']}
Critical Tickets      : {analysis['critical_tickets']}
High Priority Tickets : {analysis['high_priority_tickets']}
Busiest Team          : {analysis['busiest_team']}
Risk Level            : {analysis['risk_level']}

--------------------------------------------------
COMPLIANCE ASSESSMENT
--------------------------------------------------

Compliance Score      : {state['compliance_score']}%
Compliance Status     : {state['compliance_status']}

Reason:
{state['compliance_reason']}

--------------------------------------------------
POLICY REFERENCE
--------------------------------------------------

Source:
{state['policy_source']}

Page:
{state['policy_page'] + 1}

Relevant Rule:
{display_policy}

==================================================
"""
        # Ticket Analysis
    elif workflow == "ticket_analysis":

        report = f"""
==================================================
{title}
==================================================

Query:
{state['query']}

--------------------------------------------------
EXECUTIVE SUMMARY
--------------------------------------------------

{state['executive_summary']}

--------------------------------------------------
KEY METRICS
--------------------------------------------------

Open Tickets          : {analysis['open_tickets']}
Critical Tickets      : {analysis['critical_tickets']}
High Priority Tickets : {analysis['high_priority_tickets']}
Busiest Team          : {analysis['busiest_team']}
Risk Level            : {analysis['risk_level']}

--------------------------------------------------
COMPLIANCE ASSESSMENT
--------------------------------------------------

Compliance Score      : {state['compliance_score']}%
Compliance Status     : {state['compliance_status']}

Reason:
{state['compliance_reason']}

--------------------------------------------------
POLICY REFERENCE
--------------------------------------------------

Source:
{state['policy_source']}

Page:
{state['policy_page'] + 1}

Relevant Rule:
{display_policy}

==================================================
"""
    state["report"] = report

    return state