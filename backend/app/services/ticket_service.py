import uuid
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.db.models import Ticket, TicketMessage, TicketEvent, Customer, Feedback, User
from app.db.session import AsyncSessionLocal
from app.graph.builder import support_graph
from app.services.event_emitter import event_emitter
from app.core.errors import NotFoundError, ForbiddenError
from app.core.logging import logger

class TicketService:
    async def create_ticket(
        self,
        session: AsyncSession,
        customer_id: str,
        message: str,
        subject: Optional[str] = None
    ) -> Tuple[Ticket, str]:
        # 1. Ensure customer exists
        result = await session.execute(select(Customer).where(Customer.id == customer_id))
        cust = result.scalar_one_or_none()
        if not cust:
            # Auto-create customer record if user has none
            cust = Customer(id=customer_id, name="Valued Customer", email=f"customer_{customer_id[:6]}@example.com")
            session.add(cust)
            await session.flush()

        # 2. Create ticket
        ticket = Ticket(
            customer_id=customer_id,
            subject=subject or (message[:40] + "..."),
            status="open",
            loops=0
        )
        session.add(ticket)
        await session.flush()

        # 3. Create initial customer message
        first_msg = TicketMessage(
            ticket_id=ticket.id,
            role="customer",
            content=message
        )
        session.add(first_msg)
        await session.commit()

        run_id = str(uuid.uuid4())

        # 4. Launch graph execution in background task
        asyncio.create_task(self._run_graph(ticket.id, run_id, customer_id, message))

        return ticket, run_id

    async def add_message(
        self,
        session: AsyncSession,
        ticket_id: str,
        customer_id: str,
        message: str
    ) -> Tuple[Ticket, str]:
        result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalar_one_or_none()
        if not ticket:
            raise NotFoundError(f"Ticket {ticket_id} not found")

        msg = TicketMessage(
            ticket_id=ticket.id,
            role="customer",
            content=message
        )
        session.add(msg)
        ticket.status = "open"
        await session.commit()

        run_id = str(uuid.uuid4())
        asyncio.create_task(self._run_graph(ticket.id, run_id, customer_id, message))
        return ticket, run_id

    async def _run_graph(self, ticket_id: str, run_id: str, customer_id: str, message: str):
        try:
            # Emit run started
            await event_emitter.emit(
                ticket_id=ticket_id,
                run_id=run_id,
                seq=0,
                node="system",
                event_type="run_started",
                payload={"run_id": run_id}
            )

            # Build previous conversation history
            messages_history = []
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(TicketMessage).where(TicketMessage.ticket_id == ticket_id).order_by(TicketMessage.created_at)
                )
                msgs = result.scalars().all()
                for m in msgs:
                    messages_history.append({"role": m.role, "content": m.content})

            initial_state = {
                "ticket_id": ticket_id,
                "thread_id": ticket_id,
                "customer_id": customer_id,
                "run_id": run_id,
                "seq": 0,
                "messages": messages_history,
                "loops": 0,
                "critic_feedback": []
            }

            # Execute LangGraph
            final_state = await support_graph.ainvoke(initial_state)
            logger.info(f"Graph execution completed for ticket {ticket_id}, run {run_id}")

        except Exception as e:
            logger.error(f"Error executing graph for ticket {ticket_id}: {e}", exc_info=True)
            await event_emitter.emit(
                ticket_id=ticket_id,
                run_id=run_id,
                seq=99,
                node="system",
                event_type="error",
                payload={"code": "GRAPH_EXECUTION_ERROR", "message": str(e)}
            )

    async def get_tickets(
        self,
        session: AsyncSession,
        customer_id: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Ticket], int]:
        stmt = select(Ticket)
        if customer_id:
            stmt = stmt.where(Ticket.customer_id == customer_id)
        if status:
            stmt = stmt.where(Ticket.status == status)
        if category:
            stmt = stmt.where(Ticket.category == category)

        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await session.execute(total_stmt)).scalar() or 0

        stmt = stmt.order_by(desc(Ticket.updated_at)).offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(stmt)
        tickets = result.scalars().all()
        return list(tickets), total

    async def get_ticket_detail(self, session: AsyncSession, ticket_id: str, customer_id: Optional[str] = None) -> Ticket:
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        if customer_id:
            stmt = stmt.where(Ticket.customer_id == customer_id)
        result = await session.execute(stmt)
        ticket = result.scalar_one_or_none()
        if not ticket:
            raise NotFoundError(f"Ticket {ticket_id} not found")
        return ticket

    async def get_messages(self, session: AsyncSession, ticket_id: str) -> List[TicketMessage]:
        result = await session.execute(
            select(TicketMessage).where(TicketMessage.ticket_id == ticket_id).order_by(TicketMessage.created_at)
        )
        return list(result.scalars().all())

    async def get_trace(self, session: AsyncSession, ticket_id: str) -> Dict[str, Any]:
        result = await session.execute(
            select(TicketEvent).where(TicketEvent.ticket_id == ticket_id).order_by(TicketEvent.seq)
        )
        events = result.scalars().all()

        runs_map: Dict[str, List[Any]] = {}
        for ev in events:
            if ev.run_id not in runs_map:
                runs_map[ev.run_id] = []
            runs_map[ev.run_id].append({
                "seq": ev.seq,
                "node": ev.node,
                "event_type": ev.event_type,
                "payload": json.loads(ev.payload) if ev.payload else {},
                "duration_ms": ev.duration_ms,
                "created_at": ev.created_at
            })

        return {
            "ticket_id": ticket_id,
            "runs": [{"run_id": rid, "events": ev_list} for rid, ev_list in runs_map.items()]
        }

    async def submit_feedback(self, session: AsyncSession, ticket_id: str, rating: int, comment: Optional[str], message_id: Optional[str]):
        fb = Feedback(
            ticket_id=ticket_id,
            message_id=message_id,
            rating=rating,
            comment=comment
        )
        session.add(fb)
        await session.commit()

ticket_service = TicketService()
