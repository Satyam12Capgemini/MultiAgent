import json
import asyncio
from typing import Dict, Any, Optional, Set
from app.db.session import AsyncSessionLocal
from app.db.models import TicketEvent
from app.core.logging import logger

class EventEmitter:
    def __init__(self):
        # Maps run_id -> set of asyncio.Queue instances
        self.subscribers: Dict[str, Set[asyncio.Queue]] = {}
        # Maps run_id -> list of emitted events (replay buffer for late subscribers)
        self.history: Dict[str, list] = {}

    def subscribe(self, run_id: str) -> asyncio.Queue:
        if run_id not in self.subscribers:
            self.subscribers[run_id] = set()
        queue = asyncio.Queue()
        
        # Pre-fill with any events that were already emitted before subscription
        if run_id in self.history:
            for past_event in self.history[run_id]:
                queue.put_nowait(past_event)
                
        self.subscribers[run_id].add(queue)
        return queue

    def unsubscribe(self, run_id: str, queue: asyncio.Queue):
        if run_id in self.subscribers:
            self.subscribers[run_id].discard(queue)
            if not self.subscribers[run_id]:
                del self.subscribers[run_id]

    async def emit(
        self,
        ticket_id: str,
        run_id: str,
        seq: int,
        node: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None
    ):
        event_data = {
            "ticket_id": ticket_id,
            "run_id": run_id,
            "seq": seq,
            "node": node,
            "event_type": event_type,
            "payload": payload or {},
            "duration_ms": duration_ms
        }

        # 1. Buffer in memory for instant replay
        if run_id not in self.history:
            self.history[run_id] = []
        self.history[run_id].append(event_data)

        # 2. Persist to ticket_events in Database
        try:
            async with AsyncSessionLocal() as session:
                db_event = TicketEvent(
                    ticket_id=ticket_id,
                    run_id=run_id,
                    seq=seq,
                    node=node,
                    event_type=event_type,
                    payload=json.dumps(payload) if payload else None,
                    duration_ms=duration_ms
                )
                session.add(db_event)
                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to persist ticket event to DB: {e}")

        # 3. Push to live SSE subscribers
        if run_id in self.subscribers:
            for q in list(self.subscribers[run_id]):
                try:
                    await q.put(event_data)
                except Exception as e:
                    logger.debug(f"Failed to push to SSE queue: {e}")

event_emitter = EventEmitter()
