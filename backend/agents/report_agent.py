def report_agent(state):
    print("REPORT WORKFLOW:", state["workflow_type"])
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
    DELAYED ORDER ANALYSIS REPORT
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

    Total Delayed Orders      : {analysis['total_orders']}
    Average Delay Days        : {analysis['average_delay_days']}
    Maximum Delay Days        : {analysis['max_delay_days']}
    SLA Violations            : {analysis['sla_violations']}
    High Risk Orders          : {analysis['high_risk_orders']}
    Most Affected Warehouse   : {analysis['most_affected_warehouse']}
    Most Delayed Product      : {analysis['most_delayed_product']}
    Risk Level                : {analysis['risk_level']}

    --------------------------------------------------
    COMPLIANCE ASSESSMENT
    --------------------------------------------------

    Compliance Score      : {state['compliance_score']}%
    Compliance Status     : {state['compliance_status']}

    Reason:
    {state['compliance_reason']}

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
        
    elif workflow == "product_analysis":
        report = f"""
==================================================
PRODUCT DELAY REPORT
==================================================

Top Delayed Product:
{analysis['top_product']}

Delayed Orders:
{analysis['delayed_count']}

Average Delay:
{analysis['avg_delay_days']} days

==================================================
"""
    elif workflow == "warehouse_analysis":

        report = f"""
    ==================================================
    WAREHOUSE DELAY REPORT
    ==================================================

    Warehouse:
    {analysis['warehouse']}

    Delayed Orders:
    {analysis['delayed_orders']}

    Average Delay:
    {analysis['avg_delay_days']} days

    Total Orders:
    {analysis['total_orders']}

    Compliance Status:
    {state['compliance_status']}

    Compliance Score:
    {state['compliance_score']}%

    ==================================================
    """


    elif workflow == "dashboard_analysis":
        report = f"""
==================================================
EXECUTIVE OPERATIONS DASHBOARD
==================================================

Delayed Orders:
{analysis['delayed_orders']}

Most Affected Warehouse:
{analysis['top_warehouse']}

Warehouse Delays:
{analysis['warehouse_delays']}

Most Delayed Product:
{analysis['top_product']}

Product Delays:
{analysis['product_delays']}

Top Complaint Category:
{analysis['top_complaint']}

Complaint Count:
{analysis['complaint_count']}

Busiest Team:
{analysis['busiest_team']}

--------------------------------------------------

Compliance Status:
{state['compliance_status']}

Compliance Score:
{state['compliance_score']}%

==================================================
"""
    state["report"] = report
    return state