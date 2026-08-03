import pandas as pd
import streamlit as st

from database.db import SessionLocal
from database import queries
from database.setup_db import setup_database


@st.cache_data(show_spinner=False)
def _ensure_db():
    setup_database()
    return True


def get_session():
    _ensure_db()
    return SessionLocal()


def orders_dataframe(page: int = 1, page_size: int = 100) -> pd.DataFrame:
    db = get_session()
    try:
        rows = queries.get_orders_paginated(db, page=page, page_size=page_size)
        total = queries.count_orders(db)
        print(total)
        print(type(total))
        df = pd.DataFrame(
            [
                {
                    "Order ID": row.order_id,
                    "Customer ID": row.customer_id,
                    "Customer": row.customer_name,
                    "Product": row.product_name,
                    "Order Date": row.order_date,
                    "Expected Delivery": row.expected_delivery_date,
                    "Actual Delivery": row.actual_delivery_date,
                    "Status": row.status,
                    "Delay (days)": row.delay_days,
                    "Warehouse": row.warehouse,
                }
                for row in rows
            ]
        )
        return df, total
    finally:
        db.close()


def complaints_dataframe() -> pd.DataFrame:
    db = get_session()
    try:
        rows = queries.get_all_complaints(db)
        return pd.DataFrame(
            [
                {
                    "Complaint ID": row.complaint_id,
                    "Customer ID": row.customer_id,
                    "Customer": row.customer_name,
                    "Order ID": row.order_id,
                    "Category": row.category,
                    "Priority": row.priority,
                    "Status": row.status,
                    "Created At": row.created_at,
                    "Complaint": row.complaint_text,
                }
                for row in rows
            ]
        )
    finally:
        db.close()


def tickets_dataframe() -> pd.DataFrame:
    db = get_session()
    try:
        rows = queries.get_all_tickets(db)
        return pd.DataFrame(
            [
                {
                    "Ticket ID": row.ticket_id,
                    "Complaint ID": row.complaint_id,
                    "Issue Type": row.issue_type,
                    "Priority": row.priority,
                    "Assigned Team": row.assigned_team,
                    "Status": row.status,
                    "Created At": row.created_at,
                    "Resolved At": row.resolved_at,
                }
                for row in rows
            ]
        )
    finally:
        db.close()


def inventory_dataframe() -> pd.DataFrame:
    db = get_session()
    try:
        rows = queries.get_all_inventory(db)
        return pd.DataFrame(
            [
                {
                    "SKU ID": row.sku_id,
                    "Product": row.product_name,
                    "Warehouse": row.warehouse,
                    "Stock": row.stock_quantity,
                    "Threshold": row.reorder_threshold,
                    "Status": row.status,
                }
                for row in rows
            ]
        )
    finally:
        db.close()


def customers_dataframe() -> pd.DataFrame:
    db = get_session()
    try:
        rows = queries.get_all_customers(db)
        return pd.DataFrame(
            [
                {
                    "Customer ID": row.customer_id,
                    "Name": row.customer_name,
                    "Email": row.email,
                    "City": row.city,
                    "Total Orders": row.total_orders,
                    "Open Complaints": row.open_complaints,
                    "Last Order": row.last_order_date,
                }
                for row in rows
            ]
        )
    finally:
        db.close()
