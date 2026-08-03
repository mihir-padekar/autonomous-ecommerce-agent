import streamlit as st

from services.data_service import orders_dataframe


def render_orders():
    st.title("📦 Orders")
    st.caption("All customer orders from the database.")

    page = st.number_input("Page", min_value=1, value=1, step=1)
    page_size = st.selectbox("Rows per page", [50, 100, 200], index=1)

    df, total = orders_dataframe(page=page, page_size=page_size)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Orders", f"{total:,}")
    with c2:
        st.metric("Delivered", f"{len(df[df['Status'] == 'Delivered']):,}")
    with c3:
        st.metric("Delayed", f"{len(df[df['Status'] == 'Delayed']):,}")
    with c4:
        st.metric("Pending", f"{len(df[df['Status'] == 'Pending']):,}")

    st.dataframe(df, use_container_width=True, hide_index=True)

    total_pages = max(1, (total + page_size - 1) // page_size)
    st.caption(f"Page {page} of {total_pages} · Showing {len(df)} of {total:,} orders")
