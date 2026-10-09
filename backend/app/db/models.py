import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime, ForeignKey, Boolean, BigInteger, Numeric, Index
)
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="customer")  # customer, agent, admin
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    customer = relationship("Customer", back_populates="user")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("User", back_populates="customer", uselist=False)
    orders = relationship("Order", back_populates="customer")
    tickets = relationship("Ticket", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"

    id = Column(String(30), primary_key=True)  # e.g. ORD-10023
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    status = Column(String(20), nullable=False)  # placed, shipped, delivered, refunded
    placed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(30), ForeignKey("orders.id"), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")

class Refund(Base):
    __tablename__ = "refunds"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(30), ForeignKey("orders.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    reason = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="issued")  # issued, pending_approval, rejected
    requested_by_ticket = Column(String(36), nullable=True)
    approved_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    order = relationship("Order", back_populates="refunds")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    subject = Column(String(300), nullable=True)
    category = Column(String(20), nullable=True)  # billing, tech, general
    status = Column(String(20), nullable=False, default="open", index=True)  # open, answered, escalated, resolved, closed
    last_critic_score = Column(Float, nullable=True)
    loops = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False, index=True)

    customer = relationship("Customer", back_populates="tickets")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketMessage.created_at")
    events = relationship("TicketEvent", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketEvent.seq")
    escalations = relationship("Escalation", back_populates="ticket", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="ticket", cascade="all, delete-orphan")

class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ticket_id = Column(String(36), ForeignKey("tickets.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # customer, assistant, human_agent, system
    content = Column(Text, nullable=False)
    citations = Column(Text, nullable=True)  # JSON array of citations
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    ticket = relationship("Ticket", back_populates="messages")

class TicketEvent(Base):
    __tablename__ = "ticket_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(36), ForeignKey("tickets.id"), nullable=False, index=True)
    run_id = Column(String(36), nullable=False, index=True)
    seq = Column(Integer, nullable=False)
    node = Column(String(40), nullable=False)
    event_type = Column(String(40), nullable=False)  # node_started, classified, retrieved, critic_scored, escalated, etc.
    payload = Column(Text, nullable=True)  # JSON string
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    ticket = relationship("Ticket", back_populates="events")

    __table_args__ = (
        Index("ix_ticket_run_seq", "ticket_id", "run_id", "seq"),
    )

class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ticket_id = Column(String(36), ForeignKey("tickets.id"), nullable=False, index=True)
    reason = Column(String(50), nullable=False)  # low_conf, angry_sentiment, critic_cap_reached, refund_limit_exceeded, empty_retrieval, user_requested
    summary = Column(Text, nullable=True)
    context_json = Column(Text, nullable=True)  # JSON string of retrieved docs, last draft, classifier output
    status = Column(String(20), nullable=False, default="open", index=True)  # open, claimed, resolved
    claimed_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    ticket = relationship("Ticket", back_populates="escalations")

class KBDocument(Base):
    __tablename__ = "kb_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(300), nullable=False)
    category = Column(String(20), nullable=False)  # tech, general
    source = Column(String(500), nullable=True)
    file_hash = Column(String(64), nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, indexed, failed
    error = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    chunks = relationship("KBChunk", back_populates="document", cascade="all, delete-orphan")

class KBChunk(Base):
    __tablename__ = "kb_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    doc_id = Column(String(36), ForeignKey("kb_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)

    document = relationship("KBDocument", back_populates="chunks")

class LLMUsage(Base):
    __tablename__ = "llm_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(36), nullable=True, index=True)
    run_id = Column(String(36), nullable=True, index=True)
    node = Column(String(40), nullable=True)
    model = Column(String(100), nullable=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ticket_id = Column(String(36), ForeignKey("tickets.id"), nullable=False, index=True)
    message_id = Column(String(36), nullable=True)
    rating = Column(Integer, nullable=False)  # 1 (thumbs up) or -1 (thumbs down)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    ticket = relationship("Ticket", back_populates="feedback")

class EvalDataset(Base):
    __tablename__ = "eval_datasets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    cases = relationship("EvalCase", back_populates="dataset", cascade="all, delete-orphan")
    runs = relationship("EvalRun", back_populates="dataset")

class EvalCase(Base):
    __tablename__ = "eval_cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("eval_datasets.id"), nullable=False, index=True)
    case_code = Column(String(50), nullable=True)  # e.g. case-017
    message = Column(Text, nullable=False)
    expected_category = Column(String(20), nullable=False)
    expected_route = Column(String(40), nullable=False)
    expected_source_docs = Column(Text, nullable=True)  # JSON array
    reference_answer = Column(Text, nullable=True)
    should_escalate = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    dataset = relationship("EvalDataset", back_populates="cases")

class EvalRun(Base):
    __tablename__ = "eval_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("eval_datasets.id"), nullable=False, index=True)
    label = Column(String(100), nullable=False)
    critic_enabled = Column(Boolean, default=True, nullable=False)
    status = Column(String(20), default="running", nullable=False)  # running, completed, failed
    summary_metrics = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    dataset = relationship("EvalDataset", back_populates="runs")
    results = relationship("EvalResult", back_populates="run", cascade="all, delete-orphan")

class EvalResult(Base):
    __tablename__ = "eval_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("eval_runs.id"), nullable=False, index=True)
    case_id = Column(String(36), ForeignKey("eval_cases.id"), nullable=False)
    actual_category = Column(String(20), nullable=True)
    actual_route = Column(String(40), nullable=True)
    actual_answer = Column(Text, nullable=True)
    critic_score = Column(Float, nullable=True)
    loops = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    passed = Column(Boolean, default=False)
    metrics = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    run = relationship("EvalRun", back_populates="results")

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=False)
    details = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
