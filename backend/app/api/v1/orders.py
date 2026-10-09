from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import User
from app.schemas.order import OrderOut
from app.tools.billing_tools import billing_tools
from app.core.errors import NotFoundError
from app.api.deps import require_roles, get_current_user

router = APIRouter()

@router.get("/{order_id}", response_model=OrderOut)
async def get_order_detail(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    customer_id = user.customer_id if user.role == "customer" else None
    order = await billing_tools.get_order(db, order_id, customer_id)
    if not order:
        raise NotFoundError(f"Order {order_id} not found")
    return OrderOut.model_validate(order)

@router.get("/customers/{customer_id}/orders", response_model=List[OrderOut])
async def get_customer_orders(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["agent", "admin"]))
):
    orders = await billing_tools.list_orders(db, customer_id)
    return [OrderOut.model_validate(o) for o in orders]
