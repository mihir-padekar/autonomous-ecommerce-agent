from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class WarehouseDelayFilter(BaseModel):
    """Filter parameters for querying warehouse delays."""
    warehouse: Optional[str] = Field(
        default=None,
        description="Filter by warehouse name, e.g., 'Warehouse A', 'North Hub', 'South Facility'. If None, queries all."
    )
    min_delay_days: int = Field(
        default=1,
        ge=0,
        description="Minimum number of days delayed to include in the breakdown."
    )


class WarehouseDelayItem(BaseModel):
    warehouse: str
    total_orders: int
    delayed_count: int
    avg_delay_days: float


class WarehouseDelaySummaryResponse(BaseModel):
    warehouses: List[WarehouseDelayItem]
    total_delayed_orders: int
    most_delayed_warehouse: Optional[str] = None


class OrderLookupFilter(BaseModel):
    order_id: int = Field(description="Unique numeric identifier of the order")


class OrderDetailsResponse(BaseModel):
    order_id: int
    customer_id: int
    customer_name: str
    product_name: str
    order_date: str
    expected_delivery_date: str
    actual_delivery_date: Optional[str] = None
    status: str
    delay_days: int
    warehouse: str
    is_delayed: bool


class UpdateOrderStatusInput(BaseModel):
    order_id: int = Field(description="Order ID to update")
    new_status: str = Field(description="New status, e.g. 'Delivered', 'Delayed', 'Pending', 'Cancelled'")
    reason: str = Field(min_length=5, description="Operational justification for the status change")

    @field_validator("new_status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = {"Delivered", "Delayed", "Pending", "Cancelled", "In Transit"}
        if v.capitalize() not in valid_statuses:
            raise ValueError(f"Invalid status '{v}'. Must be one of {valid_statuses}")
        return v.capitalize()


class RefundOrderInput(BaseModel):
    order_id: int = Field(description="ID of the order to be refunded")
    reason: str = Field(min_length=10, description="Clear business rationale citing policy (e.g. delivery delay > 7 days)")
    refund_amount: Optional[float] = Field(default=None, ge=0.0, description="Optional partial or full refund amount in USD")
    customer_id: Optional[int] = Field(default=None, description="Optional verification customer ID")

