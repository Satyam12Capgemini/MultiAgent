from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.db.models import Order, OrderItem, Refund, Customer
from app.core.logging import logger

class BillingTools:
    async def get_order(self, session: AsyncSession, order_id: str, customer_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        stmt = select(Order).where(Order.id == order_id)
        if customer_id:
            stmt = stmt.where(Order.customer_id == customer_id)
        result = await session.execute(stmt)
        order = result.scalar_one_or_none()
        if not order:
            return None

        # Fetch items
        items_result = await session.execute(select(OrderItem).where(OrderItem.order_id == order_id))
        items = items_result.scalars().all()

        return {
            "order_id": order.id,
            "customer_id": order.customer_id,
            "total_amount": order.total_amount,
            "currency": order.currency,
            "status": order.status,
            "placed_at": order.placed_at.isoformat(),
            "items": [{"name": i.product_name, "qty": i.quantity, "price": i.unit_price} for i in items]
        }

    async def list_orders(self, session: AsyncSession, customer_id: str) -> List[Dict[str, Any]]:
        result = await session.execute(select(Order).where(Order.customer_id == customer_id))
        orders = result.scalars().all()
        return [
            {
                "order_id": o.id,
                "total_amount": o.total_amount,
                "currency": o.currency,
                "status": o.status,
                "placed_at": o.placed_at.isoformat()
            }
            for o in orders
        ]

    async def issue_refund(
        self,
        session: AsyncSession,
        order_id: str,
        amount: float,
        reason: str,
        customer_id: Optional[str] = None,
        ticket_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # Validate order exists and belongs to customer
        order_data = await self.get_order(session, order_id, customer_id)
        if not order_data:
            return {
                "success": False,
                "error": f"Order {order_id} not found for this customer."
            }

        # Guardrail: Check refund auto-approval limit in code
        if amount > settings.REFUND_AUTO_LIMIT:
            # Create pending approval
            refund = Refund(
                order_id=order_id,
                amount=amount,
                reason=reason,
                status="pending_approval",
                requested_by_ticket=ticket_id
            )
            session.add(refund)
            await session.commit()
            return {
                "success": False,
                "status": "pending_approval",
                "refund_id": refund.id,
                "amount": amount,
                "limit": settings.REFUND_AUTO_LIMIT,
                "message": f"Refund amount of ₹{amount} exceeds auto-approval limit of ₹{settings.REFUND_AUTO_LIMIT}. Escalated for human manager approval."
            }

        # Auto-issue refund
        refund = Refund(
            order_id=order_id,
            amount=amount,
            reason=reason,
            status="issued",
            requested_by_ticket=ticket_id
        )
        session.add(refund)
        await session.commit()

        return {
            "success": True,
            "status": "issued",
            "refund_id": refund.id,
            "amount": amount,
            "message": f"Refund of ₹{amount} has been successfully issued for order {order_id}."
        }

billing_tools = BillingTools()
