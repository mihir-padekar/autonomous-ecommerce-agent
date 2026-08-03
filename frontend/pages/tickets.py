import streamlit as st

from services.data_service import tickets_dataframe


def render_tickets():
    st.title("🎫 Tickets")
    st.caption("Support tickets generated from complaints.")

    df = tickets_dataframe()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Tickets", f"{len(df):,}")
    with c2:
        st.metric("Open", f"{len(df[df['Status'] == 'Open']):,}")
    with c3:
        st.metric("In Progress", f"{len(df[df['Status'] == 'In Progress']):,}")
    with c4:
        st.metric("Resolved", f"{len(df[df['Status'] == 'Resolved']):,}")

    team_filter = st.multiselect(
        "Filter by team",
        options=sorted(df["Assigned Team"].unique()) if not df.empty else [],
        default=[],
    )

    filtered = df.copy()
    if team_filter:
        filtered = filtered[filtered["Assigned Team"].isin(team_filter)]

    st.dataframe(filtered, use_container_width=True, hide_index=True)
