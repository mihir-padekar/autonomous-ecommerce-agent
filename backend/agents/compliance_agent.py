def compliance_agent(state):

    workflow = state["workflow_type"]

    if workflow == "order_analysis":

        violations = state["analysis"]["sla_violations"]

        score = max(
            0,
            100 - (violations * 2)
        )

        state["compliance_score"] = score

        if score >= 90:

            state["compliance_status"] = "COMPLIANT"

        elif score >= 70:

            state["compliance_status"] = "AT_RISK"

        else:

            state["compliance_status"] = "NON_COMPLIANT"

        state["compliance_reason"] = (
            f"{violations} orders exceed SLA thresholds."
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

    elif workflow == "product_analysis":

        state["compliance_status"] = "INFO"

        state["compliance_score"] = 100

        state["compliance_reason"] = (
            "Product delay analysis does not require compliance evaluation."
        )

    elif workflow == "warehouse_analysis":

        delayed_orders = state["analysis"]["delayed_orders"]

        if delayed_orders > 40:

            state["compliance_status"] = "AT_RISK"
            state["compliance_score"] = 70

            state["compliance_reason"] = (
                f"Warehouse has {delayed_orders} delayed orders."
            )

        else:

            state["compliance_status"] = "COMPLIANT"
            state["compliance_score"] = 100

            state["compliance_reason"] = (
                "Warehouse delay levels are acceptable."
            )
    elif workflow == "dashboard_analysis":

        delayed_orders = state["analysis"]["delayed_orders"]

        if delayed_orders > 200:

            state["compliance_status"] = "AT_RISK"

            state["compliance_score"] = 60

            state["compliance_reason"] = (
                f"{delayed_orders} delayed orders detected."
            )

        else:

            state["compliance_status"] = "COMPLIANT"

            state["compliance_score"] = 100

            state["compliance_reason"] = (
                "Operational metrics are within limits."
            )
    else:

        state["compliance_status"] = "UNKNOWN"

        state["compliance_score"] = 0

        state["compliance_reason"] = (
            "No compliance evaluation available."
        )
    return state