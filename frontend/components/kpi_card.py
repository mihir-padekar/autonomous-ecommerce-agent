import streamlit as st
import textwrap  # 🚀 Essential to strip indentation from HTML strings

def render_kpi_cards(metrics):
    """
    Renders the metric KPI cards side-by-side using Streamlit columns.
    Accepts a list of dicts containing keys: icon, title, value, change, trend.
    """
    
    # Dynamically create as many columns as there are metrics (usually 6)
    cols = st.columns(len(metrics))
    
    for col, metric in zip(cols, metrics):
        
        # Select style color based on the metric trend direction
        trend_class = "kpi-change-up" if metric["trend"] == "up" else "kpi-change-down"
        
        with col:
            st.markdown(
                textwrap.dedent(f"""
                <div class="kpi-card">
                    <div class="kpi-icon-wrapper">
                        {metric['icon']}
                    </div>
                    <div class="kpi-title">
                        {metric['title']}
                    </div>
                    <div class="kpi-value">
                        {metric['value']}
                    </div>
                    <div class="{trend_class}">
                        {metric['change']}
                    </div>
                </div>
                """),
                unsafe_allow_html=True,
            )