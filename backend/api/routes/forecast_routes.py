from fastapi import APIRouter
from backend.services.prophet_service import get_delay_forecast

router = APIRouter(
    prefix="/forecast",
    tags=["Forecast"]
)

@router.get("/delayed-orders")
def delayed_orders_forecast():
    return get_delay_forecast()