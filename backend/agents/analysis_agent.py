from collections import Counter

def analysis_agent(state):

    data_type = state["data_type"]

    # Delayed Orders Analysis
    
    if data_type == "orders":

        orders = state["data"]

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

    elif data_type == "complaints":

        complaints = state["data"]

        total_complaints = len(complaints)

        critical_complaints = len([
            c for c in complaints
            if c.priority == "Critical"
        ])

        high_complaints = len([
            c for c in complaints
            if c.priority == "High"
        ])

       

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
    elif data_type == "tickets":    

        tickets = state["data"]
        query_function = state["query_function"]

        total_tickets = len(tickets)

        critical_tickets = len([
            t for t in tickets
            if t.priority == "Critical"
        ])

        high_tickets = len([
            t for t in tickets
            if t.priority == "High"
        ])


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

    elif data_type == "summary":

        summary_type = state["summary_type"]

        # PRODUCT SUMMARY
        if summary_type == "products":

            product = state["data"][0]

            state["analysis"] = {

                "top_product": product["product"],

                "delayed_count": product["delayed_count"],

                "avg_delay_days": product["avg_delay_days"]
            }

        # WAREHOUSE SUMMARY
        elif summary_type == "warehouse":

            warehouse = state["data"][0]

            state["analysis"] = {

                "warehouse": warehouse["warehouse"],

                "delayed_orders": warehouse["delayed_count"],

                "avg_delay_days": warehouse["avg_delay_days"],

                "total_orders": warehouse["total_orders"]
            }

    elif data_type == "dashboard":

        dashboard = state["data"]

        delayed_orders = next(
            item["count"]
            for item in dashboard["order_status"]
            if item["status"] == "Delayed"
        )

        top_warehouse = dashboard[
            "warehouse_delays"
        ][0]

        top_product = dashboard[
            "top_delayed_products"
        ][0]

        top_complaint = dashboard[
            "complaint_categories"
        ][0]

        busiest_team = max(
            dashboard["ticket_teams"],
            key=dashboard["ticket_teams"].get
        )

        state["analysis"] = {

            "delayed_orders": delayed_orders,

            "top_warehouse":
                top_warehouse["warehouse"],

            "warehouse_delays":
                top_warehouse["delayed_count"],

            "top_product":
                top_product["product"],

            "product_delays":
                top_product["delayed_count"],

            "top_complaint":
                top_complaint["category"],

            "complaint_count":
                top_complaint["count"],

            "busiest_team":
                busiest_team
        }   
        
    return state