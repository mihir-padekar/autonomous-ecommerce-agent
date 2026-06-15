QUERY_METADATA = {

    # Orders

    "get_delayed_orders": {
        "workflow": "order_analysis",
        "data_type": "orders"
    },

    "get_high_delay_orders": {
        "workflow": "order_analysis",
        "data_type": "orders"
    },

    # Complaints

    "get_open_complaints": {
        "workflow": "complaint_analysis",
        "data_type": "complaints"
    },

    "get_critical_complaints": {
        "workflow": "complaint_analysis",
        "data_type": "complaints"
    },

    "get_high_and_critical_complaints": {
        "workflow": "complaint_analysis",
        "data_type": "complaints"
    },

    # Tickets

    "get_open_tickets": {
        "workflow": "ticket_analysis",
        "data_type": "tickets"
    },

    "get_critical_open_tickets": {
        "workflow": "ticket_analysis",
        "data_type": "tickets"
    },

    # Analytics

    "get_warehouse_delay_summary": {
        "workflow": "warehouse_analysis",
        "data_type": "summary",
        "summary_type": "warehouse"
    },

    "get_top_delayed_products": {
        "workflow": "product_analysis",
        "data_type": "summary",
        "summary_type": "products"
    },

    "get_full_dashboard_summary": {
        "workflow": "dashboard_summary",
        "data_type": "dashboard"
    }
}