import streamlit as st
from services.report_service import ReportService
from components.loader import loading

def render_ai_insights():
    st.title("🧠 AI Insights")

    with loading("Fetching insights..."):
        insights = ReportService.get_live_insights()

    if not insights:
        st.warning("No production backend recommendations are available right now.")
    else:
        # Loop dynamically through your live data strings
        for insight in insights:
            card_html = (
                f'<div class="alert-card" style="margin-bottom: 12px;">'
                f'<p>{insight}</p>'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)