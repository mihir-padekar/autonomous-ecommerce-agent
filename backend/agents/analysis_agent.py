from collections import Counter

def analysis_agent(state):

    workflow = state["workflow_type"]

    # Delayed Orders Analysis
    
    if workflow == "delayed_orders":

        orders = state["orders"]

        total_orders = len(orders)

        avg_delay = round(
            sum(order.delay_days for order in orders) / total_orders,
            2
        ) if total_orders else 0

        max_delay = max(
            [order.delay_days for order in orders],
            default=0
        )

        sla_violations = len(
            [o for o in orders if o.delay_days > 3]
        )

        high_risk_orders = len(
            [o for o in orders if o.delay_days > 5]
        )

        warehouse_counts = Counter(
            order.warehouse
            for order in orders
        )

        top_warehouse = warehouse_counts.most_common(1)[0][0] if warehouse_counts else "N/A"
        
        product_counts = Counter(
            order.product_name
            for order in orders
        )

        top_product = product_counts.most_common(1)[0][0] if product_counts else "N/A"

        if high_risk_orders > 50:
            risk = "HIGH"

        elif high_risk_orders > 20:
            risk = "MEDIUM"

        else:
            risk = "LOW"

        state["analysis"] = {

            "total_orders": total_orders,

            "average_delay_days": avg_delay,

            "max_delay_days": max_delay,

            "sla_violations": sla_violations,

            "high_risk_orders": high_risk_orders,

            "risk_level": risk,

            "most_affected_warehouse": top_warehouse,

            "most_delayed_product": top_product

        }
    ## Complaint Analysis

    elif workflow == "complaint_analysis":

        complaints = state["complaints"]

        total_complaints = len(complaints)

        critical_complaints = len([
            c for c in complaints
            if c.priority == "Critical"
        ])

        high_complaints = len([
            c for c in complaints
            if c.priority == "High"
        ])

        from collections import Counter

        category_counts = Counter(
            c.category
            for c in complaints
        )

        most_common_category = (
            category_counts.most_common(1)[0][0]
            if category_counts
            else "None"
        )

        if critical_complaints > 10:
            risk = "HIGH"
        elif critical_complaints > 5:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        state["analysis"] = {

            "open_complaints": total_complaints,

            "critical_complaints": critical_complaints,

            "high_priority_complaints": high_complaints,

            "most_common_category": most_common_category,

            "risk_level": risk
        }
    # Ticket Analysis
    elif workflow == "ticket_analysis":

        tickets = state["tickets"]

        total_tickets = len(tickets)

        critical_tickets = len([
            t for t in tickets
            if t.priority == "Critical"
        ])

        high_tickets = len([
            t for t in tickets
            if t.priority == "High"
        ])

        from collections import Counter

        team_counts = Counter(
            t.assigned_team
            for t in tickets
        )

        busiest_team = (
            team_counts.most_common(1)[0][0]
            if team_counts
            else "None"
        )

        if critical_tickets > 10:
            risk = "HIGH"
        elif critical_tickets > 5:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        state["analysis"] = {

            "open_tickets": total_tickets,

            "critical_tickets": critical_tickets,

            "high_priority_tickets": high_tickets,

            "busiest_team": busiest_team,

            "risk_level": risk
        }
    return state