import random
from datetime import datetime, timedelta


class MockData:

    # =====================================================
    # KPI DATA
    # =====================================================

    @staticmethod
    def get_kpi_metrics():

        return [
            {
                "icon": "📦",
                "title": "Total Orders",
                "value": f"{random.randint(12000,15000):,}",
                "change": f"+{random.randint(1,15)}%",
                "trend": "up"
            },
            {
                "icon": "🚚",
                "title": "Delayed Orders",
                "value": f"{random.randint(500,1500):,}",
                "change": f"+{random.randint(1,15)}%",
                "trend": "down"
            },
            {
                "icon": "💬",
                "title": "Open Complaints",
                "value": f"{random.randint(100,900):,}",
                "change": f"+{random.randint(1,10)}%",
                "trend": "up"
            },
            {
                "icon": "⚠️",
                "title": "SLA Violations",
                "value": f"{random.randint(50,250):,}",
                "change": f"+{random.randint(1,10)}%",
                "trend": "down"
            },
            {
                "icon": "💰",
                "title": "Pending Refunds",
                "value": f"{random.randint(50,150):,}",
                "change": f"+{random.randint(1,10)}%",
                "trend": "up"
            },
            {
                "icon": "📉",
                "title": "Low Stock Items",
                "value": f"{random.randint(10,50):,}",
                "change": f"+{random.randint(1,5)}",
                "trend": "down"
            }
        ]

    # =====================================================
    # CHART DATA
    # =====================================================

    @staticmethod
    def get_chart_data():

        return {
            "delayed_orders": {
                "days": [
                    "Mon",
                    "Tue",
                    "Wed",
                    "Thu",
                    "Fri",
                    "Sat",
                    "Sun"
                ],
                "values": [
                    random.randint(150,700)
                    for _ in range(7)
                ]
            },

            "complaints": {
                "labels": [
                    "Delivery",
                    "Refund",
                    "Payment",
                    "Quality"
                ],
                "values": [
                    random.randint(10,50),
                    random.randint(10,50),
                    random.randint(10,50),
                    random.randint(10,50)
                ]
            },

            "sla": {
                "days": [
                    "Mon",
                    "Tue",
                    "Wed",
                    "Thu",
                    "Fri",
                    "Sat",
                    "Sun"
                ],
                "values": [
                    random.randint(10,60)
                    for _ in range(7)
                ]
            }
        }

    # =====================================================
    # WORKFLOW TABLE
    # =====================================================

    @staticmethod
    def get_workflows(count=25):

        workflow_names = [
            "Delayed Orders Escalation",
            "Refund Complaint Analysis",
            "Inventory Monitoring",
            "SLA Audit",
            "Customer Complaint Review",
            "Weekly Report",
            "Payment Failure Analysis"
        ]

        statuses = [
            "Completed",
            "Running",
            "Failed"
        ]

        agents = [
            "Planner",
            "Database",
            "Policy",
            "Analysis",
            "Action",
            "Report"
        ]

        records = []

        for i in range(count):

            records.append(
                {
                    "Workflow ID":
                        f"WF{10000+i}",

                    "Workflow Name":
                        random.choice(workflow_names),

                    "Status":
                        random.choice(statuses),

                    "Executed At":
                        (
                            datetime.now()
                            -
                            timedelta(
                                minutes=random.randint(
                                    1,
                                    1500
                                )
                            )
                        ).strftime(
                            "%d-%b-%Y %I:%M %p"
                        ),

                    "Agent":
                        random.choice(agents),

                    "Duration":
                        f"{random.randint(5,40)} min"
                }
            )

        return records

    # =====================================================
    # AGENTS
    # =====================================================

    @staticmethod
    def get_agents():

        return [
            {
                "name": "Planner Agent",
                "status": "Healthy"
            },
            {
                "name": "Database Agent",
                "status": "Healthy"
            },
            {
                "name": "Policy Agent",
                "status": "Running"
            },
            {
                "name": "Analysis Agent",
                "status": "Running"
            },
            {
                "name": "Action Agent",
                "status": "Idle"
            },
            {
                "name": "Report Agent",
                "status": "Healthy"
            }
        ]

    # =====================================================
    # ALERTS
    # =====================================================

    @staticmethod
    def get_alerts():

        return [
            {
                "title":
                    "Critical Inventory Alert",
                "priority":
                    "High"
            },
            {
                "title":
                    "Refund SLA Breach",
                "priority":
                    "Medium"
            },
            {
                "title":
                    "Delayed Shipment Spike",
                "priority":
                    "High"
            },
            {
                "title":
                    "Warehouse Capacity Warning",
                "priority":
                    "Low"
            }
        ]

    # =====================================================
    # DELAYED ORDERS PAGE
    # =====================================================

    @staticmethod
    def get_delayed_orders(count=30):

        data = []

        for i in range(count):

            data.append(
                {
                    "Order ID":
                        f"ORD{random.randint(10000,99999)}",

                    "Customer":
                        f"Customer {i+1}",

                    "Days Delayed":
                        random.randint(1,10),

                    "Status":
                        random.choice(
                            [
                                "Pending",
                                "Escalated",
                                "Resolved"
                            ]
                        )
                }
            )

        return data

    # =====================================================
    # REFUND COMPLAINTS
    # =====================================================

    @staticmethod
    def get_refund_complaints(count=25):

        data = []

        for i in range(count):

            data.append(
                {
                    "Complaint ID":
                        f"RC{random.randint(1000,9999)}",

                    "Customer":
                        f"Customer {i+1}",

                    "Amount":
                        f"${random.randint(20,500)}",

                    "Status":
                        random.choice(
                            [
                                "Open",
                                "Investigating",
                                "Closed"
                            ]
                        )
                }
            )

        return data

    # =====================================================
    # AI INSIGHTS
    # =====================================================

    @staticmethod
    def get_ai_insights():

        return [
            "Refund complaints increased by 12% this week.",
            "Inventory risk detected for 8 SKUs.",
            "SLA performance dropped 2.4%.",
            "Zone-3 contributes 48% of delayed orders.",
            "Customer satisfaction remains above target."
        ]

    # =====================================================
    # EXECUTIVE SUMMARY
    # =====================================================

    @staticmethod
    def get_executive_summary():

        return """
Executive Summary

Overall platform health remains stable.

Delayed orders increased slightly but remain within acceptable thresholds.

Inventory alerts require immediate attention for multiple SKUs.

Refund processing efficiency improved by 8%.

AI recommends prioritizing inventory and shipment workflows over the next 48 hours.
"""