import streamlit as st

from services.data_service import customers_dataframe


def render_customers():
    st.title("👥 Customers")
    st.caption("Customer profiles derived from order history.")

    df = customers_dataframe()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Customers", f"{len(df):,}")
    with c2:
        st.metric("With Open Complaints", f"{len(df[df['Open Complaints'] > 0]):,}")
    with c3:
        st.metric("Avg Orders / Customer", f"{df['Total Orders'].mean():.1f}" if not df.empty else "0")

    city_filter = st.multiselect(
        "Filter by city",
        options=sorted(df["City"].dropna().unique()) if not df.empty else [],
        default=[],
    )

    filtered = df.copy()
    if city_filter:
        filtered = filtered[filtered["City"].isin(city_filter)]

    st.dataframe(filtered, use_container_width=True, hide_index=True)
