import json
import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import User, TicketMessage
from app.schemas.ticket import (
    TicketCreateRequest, TicketCreateResponse, TicketListResponse,
    TicketDetailResponse, TicketMessageCreate, TicketMessageOut,
    TicketTraceResponse, FeedbackRequest
)
from app.services.ticket_service import ticket_service
from app.services.event_emitter import event_emitter
from app.api.deps import get_current_user, get_current_user_optional
from app.core.errors import ForbiddenError

router = APIRouter()

@router.post("", response_model=TicketCreateResponse, status_code=201)
async def create_ticket(
    req: TicketCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    customer_id = user.customer_id if (user and user.customer_id) else (req.customer_id or "guest-customer")
    ticket, run_id = await ticket_service.create_ticket(
        session=db,
        customer_id=customer_id,
        message=req.message,
        subject=req.subject
    )

    return TicketCreateResponse(
        ticket_id=ticket.id,
        run_id=run_id,
        status=ticket.status,
        stream_url=f"/api/v1/tickets/{ticket.id}/runs/{run_id}/stream"
    )

@router.get("", response_model=TicketListResponse)
async def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    # If customer, filter to own tickets only
    customer_id = None
    if user and user.role == "customer":
        customer_id = user.customer_id

    items, total = await ticket_service.get_tickets(
        session=db,
        customer_id=customer_id,
        status=status,
        category=category,
        page=page,
        page_size=page_size
    )

    return TicketListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

@router.get("/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    customer_id = user.customer_id if (user and user.role == "customer") else None
    ticket = await ticket_service.get_ticket_detail(db, ticket_id, customer_id)
    messages = await ticket_service.get_messages(db, ticket_id)

    formatted_msgs = []
    for m in messages:
        citations_list = json.loads(m.citations) if m.citations else None
        formatted_msgs.append(TicketMessageOut(
            id=m.id,
            ticket_id=m.ticket_id,
            role=m.role,
            content=m.content,
            citations=citations_list,
            created_at=m.created_at
        ))

    return TicketDetailResponse(
        id=ticket.id,
        customer_id=ticket.customer_id,
        subject=ticket.subject,
        category=ticket.category,
        status=ticket.status,
        last_critic_score=ticket.last_critic_score,
        loops=ticket.loops,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        messages=formatted_msgs
    )

@router.post("/{ticket_id}/messages", response_model=TicketCreateResponse)
async def add_message(
    ticket_id: str,
    req: TicketMessageCreate,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    customer_id = user.customer_id if (user and user.customer_id) else "guest-customer"
    ticket, run_id = await ticket_service.add_message(db, ticket_id, customer_id, req.message)
    return TicketCreateResponse(
        ticket_id=ticket.id,
        run_id=run_id,
        status=ticket.status,
        stream_url=f"/api/v1/tickets/{ticket.id}/runs/{run_id}/stream"
    )

@router.get("/{ticket_id}/runs/{run_id}/stream")
async def stream_run_events(ticket_id: str, run_id: str):
    async def event_generator():
        queue = event_emitter.subscribe(run_id)
        try:
            while True:
                try:
                    # Timeout periodically to send keep-alive
                    event_data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {
                        "event": event_data["event_type"],
                        "data": json.dumps(event_data["payload"])
                    }
                    if event_data["event_type"] in ("done", "error", "escalated"):
                        break
                except asyncio.TimeoutError:
                    yield {
                        "event": "ping",
                        "data": json.dumps({"status": "keep-alive"})
                    }
        finally:
            event_emitter.unsubscribe(run_id, queue)

    return EventSourceResponse(event_generator())

@router.get("/{ticket_id}/trace", response_model=TicketTraceResponse)
async def get_ticket_trace(ticket_id: str, db: AsyncSession = Depends(get_db)):
    trace_data = await ticket_service.get_trace(db, ticket_id)
    return TicketTraceResponse.model_validate(trace_data)

@router.post("/{ticket_id}/feedback")
async def submit_feedback(ticket_id: str, req: FeedbackRequest, db: AsyncSession = Depends(get_db)):
    await ticket_service.submit_feedback(
        session=db,
        ticket_id=ticket_id,
        rating=req.rating,
        comment=req.comment,
        message_id=req.message_id
    )
    return {"status": "ok", "message": "Feedback submitted successfully."}

@router.post("/{ticket_id}/close")
async def close_ticket(ticket_id: str, db: AsyncSession = Depends(get_db)):
    ticket = await ticket_service.get_ticket_detail(db, ticket_id)
    ticket.status = "closed"
    await db.commit()
    return {"status": "ok", "ticket_id": ticket.id, "status": "closed"}
