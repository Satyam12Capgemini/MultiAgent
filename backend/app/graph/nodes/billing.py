import re
import time
from typing import Dict, Any
from app.graph.state import TicketState
from app.tools.billing_tools import billing_tools
from app.db.session import AsyncSessionLocal
from app.llm.factory import get_llm_client
from app.services.event_emitter import event_emitter

async def billing_node(state: TicketState) -> Dict[str, Any]:
    start_time = time.time()
    seq = state.get("seq", 0) + 1
    ticket_id = state.get("ticket_id", "")
    run_id = state.get("run_id", "")
    customer_id = state.get("customer_id", "")
    masked_text = state.get("masked_text", "")
    critic_feedback = state.get("critic_feedback", [])

    # Find order id in message
    order_match = re.search(r'ORD-\d+', masked_text, re.IGNORECASE)
    order_id = order_match.group(0).upper() if order_match else None

    # Check if refund requested
    is_refund_request = any(w in masked_text.lower() for w in ["refund", "money back", "double charge", "charged twice", "cancel order"])

    order_info = None
    refund_result = None
    orders_list = []

    async with AsyncSessionLocal() as session:
        if order_id:
            order_info = await billing_tools.get_order(session, order_id, customer_id)
        elif customer_id:
            orders_list = await billing_tools.list_orders(session, customer_id)

        if is_refund_request and order_id:
            # Extract refund amount if mentioned or default to order total / ₹299
            amount_match = re.search(r'(?:₹|rs\.?|inr|\$)\s*(\d+(?:\.\d+)?)', masked_text, re.IGNORECASE)
            if amount_match:
                amount = float(amount_match.group(1))
            elif order_info:
                amount = float(order_info["total_amount"])
            else:
                amount = 299.0

            refund_result = await billing_tools.issue_refund(
                session=session,
                order_id=order_id,
                amount=amount,
                reason=masked_text[:200],
                customer_id=customer_id,
                ticket_id=ticket_id
            )

    # Build response
    if refund_result:
        if not refund_result.get("success") and refund_result.get("status") != "pending_approval":
            answer = refund_result.get("error", f"Could not process refund for order {order_id}. Please verify your order details.")
            escalation_reason = None
            pending_refund = None
        elif refund_result.get("status") == "pending_approval":
            answer = f"I have received your refund request of ₹{refund_result['amount']} for order {order_id}. Because this amount exceeds the auto-approval limit of ₹{refund_result['limit']}, it has been submitted for supervisor approval and our billing team will review it shortly."
            escalation_reason = "refund_over_limit"
            pending_refund = refund_result
        else:
            answer = f"I have processed your refund of ₹{refund_result['amount']} for order {order_id}. The refund ID is {refund_result['refund_id']} and funds will reflect in your original payment method in 3-5 business days."
            escalation_reason = None
            pending_refund = None
    elif order_info:
        items_desc = ", ".join([f"{item['qty']}x {item['name']} (₹{item['price']})" for item in order_info.get("items", [])])
        answer = f"Here are the details for your order {order_id}: Status is '{order_info['status']}', total amount is ₹{order_info['total_amount']}. Items included: {items_desc}."
        escalation_reason = None
        pending_refund = None
    elif orders_list:
        summary_orders = "; ".join([f"Order {o['order_id']}: ₹{o['total_amount']} ({o['status']})" for o in orders_list[:3]])
        answer = f"I found the following recent orders on your account: {summary_orders}. Please let me know which order you need assistance with."
        escalation_reason = None
        pending_refund = None
    else:
        answer = "I'd be glad to help with your billing inquiry. Could you please provide your Order ID (for example, ORD-10023) so I can pull up your account details?"
        escalation_reason = None
        pending_refund = None

    duration = int((time.time() - start_time) * 1000)
    await event_emitter.emit(
        ticket_id=ticket_id,
        run_id=run_id,
        seq=seq,
        node="billing_agent",
        event_type="draft",
        payload={"answer": answer, "order_id": order_id, "refund": refund_result},
        duration_ms=duration
    )

    return {
        "seq": seq,
        "answer": answer,
        "citations": [{"n": 1, "chunk_id": order_id or "orders_db", "title": "Billing System"}] if (order_info or refund_result) else [],
        "pending_refund": pending_refund,
        "escalation_reason": escalation_reason
    }
