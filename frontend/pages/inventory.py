import streamlit as st

from services.data_service import inventory_dataframe


def render_inventory():
    st.title("📦 Inventory")
    st.caption("Product stock levels across warehouses.")

    df = inventory_dataframe()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total SKUs", f"{len(df):,}")
    with c2:
        st.metric("In Stock", f"{len(df[df['Status'] == 'In Stock']):,}")
    with c3:
        st.metric("Low Stock", f"{len(df[df['Status'] == 'Low Stock']):,}")
    with c4:
        st.metric("Out of Stock", f"{len(df[df['Status'] == 'Out of Stock']):,}")

    warehouse_filter = st.multiselect(
        "Filter by warehouse",
        options=sorted(df["Warehouse"].unique()) if not df.empty else [],
        default=[],
    )
    status_filter = st.multiselect(
        "Filter by status",
        options=sorted(df["Status"].unique()) if not df.empty else [],
        default=[],
    )

    filtered = df.copy()
    if warehouse_filter:
        filtered = filtered[filtered["Warehouse"].isin(warehouse_filter)]
    if status_filter:
        filtered = filtered[filtered["Status"].isin(status_filter)]

    st.dataframe(filtered, use_container_width=True, hide_index=True)
