from fastapi import APIRouter

from backend.database.db import SessionLocal
from backend.database.queries import (
    get_full_dashboard_summary,
    get_warehouse_delay_summary,
    get_top_delayed_products,
    get_delayed_orders
)

router = APIRouter()

@router.get("/dashboard")
def dashboard():

    db = SessionLocal()

    try:

        return get_full_dashboard_summary(db)

    finally:

        db.close()

@router.get("/warehouse-summary")
def warehouse_summary():

    db = SessionLocal()

    try:
        return get_warehouse_delay_summary(db)

    finally:
        db.close()

@router.get("/top-products")
def top_products():

    db = SessionLocal()

    try:
        return get_top_delayed_products(db)

    finally:
        db.close()

@router.get("/delayed-orders")
def delayed_orders():

    db = SessionLocal()

    try:
        return get_delayed_orders(db)

    finally:
        db.close()