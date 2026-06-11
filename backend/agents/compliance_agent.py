def compliance_agent(state):

    workflow = state["workflow_type"]

    if workflow == "delayed_orders":

        violations = state["analysis"]["sla_violations"]

        if violations > 0:

            state["compliance_status"] = "NON_COMPLIANT"

            state["compliance_reason"] = (
                f"{violations} orders exceed SLA thresholds."
            )

        else:

            state["compliance_status"] = "COMPLIANT"

            state["compliance_reason"] = (
                "No SLA violations detected."
            )

    elif workflow == "ticket_analysis":

        critical = state["analysis"]["critical_tickets"]

        score = max(
            0,
            100 - (critical * 5)
        )

        state["compliance_score"] = score

        if score >= 90:

            state["compliance_status"] = "COMPLIANT"

        elif score >= 70:

            state["compliance_status"] = "AT_RISK"

        else:

            state["compliance_status"] = "NON_COMPLIANT"

        state["compliance_reason"] = (
            f"{critical} critical tickets remain open."
        )

    return state