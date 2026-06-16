from fastapi import APIRouter

from backend.database.db import SessionLocal
from backend.database.queries import (
    get_full_dashboard_summary,
    get_warehouse_delay_summary,
    get_top_delayed_products,
    get_delayed_orders,
    get_dashboard_kpis,
    get_warehouse_delay_summary,
    get_complaint_category_summary,
    count_tickets_by_team
)
from backend.database.queries import (
    get_dashboard_kpis
)
from backend.database.db import SessionLocal

from backend.api.schemas.dashboard_schemas import (
    DashboardKPIResponse,
    WarehouseDelayResponse,
    ComplaintCategoryResponse
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

@router.get(
    "/dashboard/kpis",
    response_model=DashboardKPIResponse
)
def dashboard_kpis():

    db = SessionLocal()

    try:

        return get_dashboard_kpis(db)

    finally:

        db.close()

@router.get(
    "/dashboard/charts/warehouse-delays",
    response_model=list[WarehouseDelayResponse]
)
def warehouse_delay_chart():

    db = SessionLocal()

    try:

        return get_warehouse_delay_summary(db)

    finally:

        db.close()

@router.get(
    "/dashboard/charts/complaints",
    response_model=list[ComplaintCategoryResponse]
)
def complaint_chart():

    db = SessionLocal()

    try:

        return get_complaint_category_summary(db)

    finally:

        db.close()

@router.get(
    "/dashboard/charts/tickets"
)
def ticket_chart():

    db = SessionLocal()

    try:

        return count_tickets_by_team(db)

    finally:

        db.close()
