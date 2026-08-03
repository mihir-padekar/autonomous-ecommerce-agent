import streamlit as st
import pandas as pd
from services.workflow_service import WorkflowService


def render_refund_complaints():

    st.title("💰 Refund Complaints")

    data = WorkflowService.refund_complaints_data()

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.metric(
        "Open Refund Cases",
        len(df[df["Status"] != "Closed"])
    )