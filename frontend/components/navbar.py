import streamlit as st

def nav_button(label):
    active = st.session_state.current_page == label

    if st.button(
        label,
        use_container_width=True,
        key=f"nav_{label}"
    ):
        st.session_state.current_page = label
        st.rerun()

def render_sidebar():

    with st.sidebar:
        st.html("""
        <div class="sidebar-brand">
            <div class="brand-icon">🤖</div>
            <div>
                <div class="brand-title">
                    E-Commerce
                </div>
                <div class="brand-subtitle">
                    Operations Agent
                </div>
            </div>
        </div>
        """)

        
        st.html("<div class='menu-section'>MAIN</div>")

        nav_button("Dashboard")
        nav_button("Chat")

        st.html("<div class='menu-section'>WORKFLOWS</div>")

        nav_button("Delayed Orders")
        # nav_button("Refund Complaints")
        # nav_button("SLA Violations")
        # nav_button("Inventory Alerts")
        # nav_button("Custom Query")
        nav_button("Workflow History")

        st.html("<div class='menu-section'>DATA</div>")

        nav_button("Orders")
        nav_button("Complaints")
        nav_button("Tickets")
        nav_button("Inventory")
        nav_button("Customers")

        st.html("<div class='menu-section'>ANALYTICS</div>")

        nav_button("Reports")
        nav_button("Trends")
        nav_button("AI Insights")

        st.html("<div class='menu-section'>CONFIGURATION</div>")

        nav_button("Policies (RAG)")

        st.html("<br>")

        st.button(
            "Logout",
            use_container_width=True,
            key="logout"
        )