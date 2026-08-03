import streamlit as st
import pandas as pd
from services.api_client import APIClient
from components.loader import loading

def render_delayed_orders():

    st.title("🚚 Delayed Orders")

    with loading("Loading Delayed Orders..."):  
        api_response = APIClient.get_delayed_orders()

    df = pd.DataFrame(api_response)

    if df.empty:
        st.warning("No delayed orders found")
        return

    # ==========================
    # KPI CARDS
    # ==========================

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Total Delayed Orders",
            len(df)
        )

    with c2:
        if "delay_days" in df.columns:
            avg_delay = round(df["delay_days"].astype(float).mean(), 1)
            st.metric(
                "Avg Delay",
                f"{avg_delay} Days"
            )

    with c3:
        if "status" in df.columns:
            escalated = len(
                df[
                    df["status"]
                    .astype(str)
                    .str.lower()
                    .eq("escalated")
                ]
            )
            st.metric(
                "Escalated",
                escalated
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================
    # TABLE
    # ==========================
    display_df = df.rename(columns={
    "order_id": "Order ID",
    "customer_name": "Customer",
    "delay_days": "Days Delayed",
    "status": "Status"
})

    display_df = display_df[
    [
        "Order ID",
        "Customer",
        "Days Delayed",
        "Status"
    ]
]

    st.dataframe(
    display_df,
    width="stretch",
    hide_index=True
)

   