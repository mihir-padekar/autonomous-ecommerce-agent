import streamlit as st
from services.report_service import ReportService
from components.loader import loading


def render_reports():

    st.title("📊 Reports")

    with loading("Fetching Reports..."):

        live_data = ReportService.get_dashboard_analysis()
        analysis = live_data.get("analysis", {})
        raw_text_report = live_data.get("report", "")

    st.subheader("🤖 Live AI Agent Dashboard Analysis")

    if not analysis:
        st.error("Unable to populate metrics. Please verify that your local API service is running.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric(
                label="Delayed Orders", 
                value=analysis.get("delayed_orders", 0)
            )
        with c2:
            st.metric(
                label="Top Delayed Product", 
                value=analysis.get("top_product", "N/A"), 
                delta=f"{analysis.get('product_delays', 0)} delays",
                delta_color="inverse"
            )
        with c3:
            st.metric(
                label="Top Warehouse Hub", 
                value=analysis.get("top_warehouse", "N/A"), 
                delta=f"{analysis.get('warehouse_delays', 0)} stuck",
                delta_color="inverse"
            )
        with c4:
            st.metric(
                label="Busiest Operations Team", 
                value=analysis.get("busiest_team", "N/A")
            )

        st.markdown("<br>", unsafe_allow_html=True)

        c5, c6 = st.columns(2)
        with c5:
            st.metric(
                label="Top Complaint Category", 
                value=analysis.get("top_complaint", "N/A")
            )
        with c6:
            st.metric(
                label="Total Complaint Count", 
                value=analysis.get("complaint_count", 0)
            )

    st.divider()

    # Live Generated Report View & Document Extraction Section
    st.subheader("📄 Executive Operations Summary")
    
    if raw_text_report:
        st.text(raw_text_report)
        
        st.download_button(
            label="Download Agent Report (.txt)",
            data=raw_text_report,
            file_name="live_agent_report.txt",
            mime="text/plain"
        )