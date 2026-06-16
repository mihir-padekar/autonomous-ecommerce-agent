from pydantic import BaseModel


class DashboardKPIResponse(BaseModel):

    total_orders: int

    delayed_orders: int

    complaints: int

    sla_violations: int

    open_tickets: int

class WarehouseDelayResponse(BaseModel):

    warehouse: str
    delayed_count: int
    avg_delay_days: float
    total_orders: int


class ComplaintCategoryResponse(BaseModel):

    category: str
    count: int