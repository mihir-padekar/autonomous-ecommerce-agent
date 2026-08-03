import streamlit as st

from services.data_service import complaints_dataframe


def render_complaints():
    st.title("💬 Complaints")
    st.caption("Customer complaints linked to orders.")

    df = complaints_dataframe()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Complaints", f"{len(df):,}")
    with c2:
        st.metric("Open", f"{len(df[df['Status'] == 'Open']):,}")
    with c3:
        st.metric("In Progress", f"{len(df[df['Status'] == 'In Progress']):,}")
    with c4:
        st.metric("Critical", f"{len(df[df['Priority'] == 'Critical']):,}")

    status_filter = st.multiselect(
        "Filter by status",
        options=sorted(df["Status"].unique()) if not df.empty else [],
        default=[],
    )
    priority_filter = st.multiselect(
        "Filter by priority",
        options=sorted(df["Priority"].unique()) if not df.empty else [],
        default=[],
    )

    filtered = df.copy()
    if status_filter:
        filtered = filtered[filtered["Status"].isin(status_filter)]
    if priority_filter:
        filtered = filtered[filtered["Priority"].isin(priority_filter)]

    st.dataframe(filtered, use_container_width=True, hide_index=True)
