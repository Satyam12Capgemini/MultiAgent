from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class OrderItemOut(BaseModel):
    id: str
    product_name: str
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: str
    customer_id: str
    total_amount: float
    currency: str
    status: str
    placed_at: datetime
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True

class RefundOut(BaseModel):
    id: str
    order_id: str
    amount: float
    reason: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
