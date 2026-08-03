import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from pages.dashboard import render_dashboard
from pages.delayed_orders import render_delayed_orders
from pages.refund_complaints import render_refund_complaints
from pages.sla_violations import render_sla_violations
from pages.inventory_alerts import render_inventory_alerts
from pages.custom_query import render_custom_query
from pages.workflow_history import render_workflow_history
from pages.reports import render_reports
from pages.trends import render_trends
from pages.ai_insights import render_ai_insights
from pages.orders import render_orders
from pages.complaints import render_complaints
from pages.tickets import render_tickets
from pages.inventory import render_inventory
from pages.customers import render_customers

from components.chatbot import render_chatbot
from components.navbar import render_sidebar

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="E-Commerce Operations Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# LOAD CSS
# --------------------------------------------------

with open("assets/styles.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

render_sidebar()

# --------------------------------------------------
# MAIN LAYOUT
# --------------------------------------------------

# ==========================
# CHAT PAGE
# ==========================

if st.session_state.current_page == "Chat":
    render_chatbot()

# ==========================
# ALL OTHER PAGES
# ==========================

else:

    main_col, assistant_col = st.columns([4, 1.3])

    with main_col:

        if st.session_state.current_page == "Dashboard":
            render_dashboard()

        elif st.session_state.current_page == "Delayed Orders":
            render_delayed_orders()

        # elif st.session_state.current_page == "Refund Complaints":
        #     render_refund_complaints()

        # elif st.session_state.current_page == "SLA Violations":
        #     render_sla_violations()

        # elif st.session_state.current_page == "Inventory Alerts":
        #     render_inventory_alerts()

        # elif st.session_state.current_page == "Custom Query":
        #     render_custom_query()

        elif st.session_state.current_page == "Workflow History":
            render_workflow_history()

        elif st.session_state.current_page == "Reports":
            render_reports()

        elif st.session_state.current_page == "Trends":
            render_trends()

        elif st.session_state.current_page == "AI Insights":
            render_ai_insights()

        elif st.session_state.current_page == "Orders":
            render_orders()

        elif st.session_state.current_page == "Complaints":
            render_complaints()

        elif st.session_state.current_page == "Tickets":
            render_tickets()

        elif st.session_state.current_page == "Inventory":
            render_inventory()

        elif st.session_state.current_page == "Customers":
            render_customers()

    with assistant_col:
        render_chatbot()