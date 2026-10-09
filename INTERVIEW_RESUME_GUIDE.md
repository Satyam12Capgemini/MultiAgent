# Support Copilot: Technical Interview & Resume Defense Guide

> Master reference for presenting Support Copilot in AI engineering resumes, system design rounds, and multi-agent technical interviews.

---

## Table of Contents

1. [One-Minute Elevator Pitch](#1-one-minute-elevator-pitch)
2. [High-Impact Resume Bullet Points](#2-high-impact-resume-bullet-points)
3. [System Design Defense & Architecture Questions](#3-system-design-defense--architecture-questions)
4. [Deep-Dive Technical Q&A (10 Core Questions)](#4-deep-dive-technical-qa-10-core-questions)
5. [Evaluation Numbers & Proof Points](#5-evaluation-numbers--proof-points)

---

## 1. One-Minute Elevator Pitch

> *"I designed and built **Support Copilot**, a production-grade autonomous Multi-Agent Customer Support system using **FastAPI**, **LangGraph**, **Angular 17+**, **ChromaDB**, and **Microsoft SQL Server**.
>
> To solve the critical industry problem of chatbot hallucinations and security leaks, our architecture separates domain specialists (Billing, Tech Hardware, General Policy) under strict least-privilege permissions. We implemented **Hybrid RAG** combining dense ChromaDB embeddings (`text-embedding-3-small`) and sparse BM25 with Reciprocal Rank Fusion ($k=60$), followed by an autonomous **Grounding-Critic loop** that fact-checks every atomic claim before customer delivery, achieving a **0% hallucination rate**.
>
> For safety, the system enforces **Regex + Luhn PII card scrubbing**, a **code-enforced ₹500 auto-refund threshold**, real-time **Server-Sent Events (SSE)** trace transparency, and a context-preserving **Human-in-the-Loop escalation pipeline** for angry customer sentiment."*

---

## 2. High-Impact Resume Bullet Points

### For AI / Machine Learning Engineer Roles:
- **Architected an Autonomous Multi-Agent Customer Support System** using **LangGraph**, **FastAPI**, and **Capgemini Generative Engine (`openai.gpt-4o`)**, achieving a 90%+ routing accuracy and sub-2.5s end-to-end response latency.
- **Engineered a Cyclic Critic-Grounding Loop** that decomposes LLM drafts into atomic claims and verifies them against retrieved source documentation, reducing hallucination rates from 20% to 0%.
- **Implemented a Production Hybrid RAG Pipeline** integrating dense vector search (ChromaDB, 1536-d) and sparse keyword retrieval (BM25) via Reciprocal Rank Fusion ($k=60$), boosting citation faithfulness to 100%.
- **Developed Code-Enforced Financial & Security Guardrails**, including Regex + Luhn algorithm payment card redaction, prompt injection scanners, and hard-coded ₹500 automated refund limits.

### For Full-Stack / Backend Engineer Roles:
- **Built a Reactive Angular 17+ Client** utilizing Standalone Components, Signals state management, and real-time Server-Sent Events (SSE) streaming for step-by-step agent execution tracing.
- **Designed an Asynchronous FastAPI Backend** with Pydantic v2 validation, JWT role-based access control (Customer, Agent, Admin), and SQLAlchemy 2.0 supporting MSSQL 2022 and SQLite.
- **Constructed a Multi-Role Enterprise Helpdesk Suite** featuring a customer support chat, a real-time Human Escalation Queue with AI context replay, and an administrative Knowledge Base management portal.

---

## 3. System Design Defense & Architecture Questions

### Q1: Why LangGraph instead of CrewAI, AutoGen, or monolithic LangChain?
**Answer:**
1. **Deterministic State Machine:** Customer support requires strict deterministic routing (e.g., security checks must ALWAYS precede intent classification; money operations must ALWAYS be gated). LangGraph's `StateGraph` provides explicit graph edges and cycle control.
2. **First-Class Cyclic Loops:** LangGraph natively supports cyclic graphs with stateful feedback loops (essential for our Critic self-correction loop capped at 3 iterations).
3. **Resumable State & Checkpointing:** LangGraph allows pausing execution when human escalation is triggered and resuming the exact graph state once a human agent responds.

---

### Q2: Why split into multiple agents instead of a single prompt with all tools?
**Answer:**
1. **Tool Sprawl & Context Contamination:** A single prompt given SQL database tools, hundreds of KB chunks, and refund APIs suffers from high tool selection error and context dilution.
2. **Least Privilege Data Isolation:** The Billing Agent has SQL read/write access for orders, whereas the Tech Specialist only has read access to public router manuals. A single-prompt chatbot risks leaking internal database schemas when answering public hardware queries.
3. **Unbiased QA:** The Critic Agent has zero tools and zero database access, preventing it from hallucinating or modifying data while judging factual grounding.

---

### Q3: How does the Hybrid RAG pipeline with Reciprocal Rank Fusion (RRF) work?
**Answer:**
- **Problem:** Dense vector embeddings excel at semantic similarity (*"How do I reboot my box?"* $\rightarrow$ *"Power cycle instructions"*), but perform poorly on exact part numbers or error codes (*"Model N300"*, *"ERR-502"*).
- **Solution:** We run parallel retrieval:
  1. Dense Cosine Similarity in ChromaDB using `text-embedding-3-small` (1536-d).
  2. Sparse Keyword Search using in-memory BM25 Okapi.
  3. We merge and re-rank the candidate chunks using the standard RRF formula ($k=60$):
     $$\text{RRF Score}(d) = \frac{1}{60 + \text{rank}_{\text{dense}}(d)} + \frac{1}{60 + \text{rank}_{\text{sparse}}(d)}$$
  4. Only chunks with merged score $\ge 0.35$ are passed to the agent context.

---

### Q4: How do you prevent infinite loops in the Critic cycle?
**Answer:**
- The graph state maintains a `loops` integer.
- When the Critic scores a draft below 0.80, it increments `loops += 1` and appends structured revision feedback (e.g., *"Claim in step 3 unsupported by chunk 1"*).
- The LangGraph conditional edge checks:
  - If `score < 0.80` and `loops < 3` $\longrightarrow$ Route back to specialist agent.
  - If `score < 0.80` and `loops == 3` $\longrightarrow$ Route to `escalate_node` with reason `"critic_cap_reached"`.
- This guarantees maximum 3 LLM fact-checking calls per customer message.

---

### Q5: How is financial safety enforced for refund processing?
**Answer:**
- We do NOT trust the LLM to make financial decisions via natural language prompts.
- The `billing_tools.py` module enforces a hardcoded threshold:
  ```python
  AUTO_REFUND_LIMIT = 500.0  # ₹500 INR
  if order.total_amount > AUTO_REFUND_LIMIT:
      return {"status": "escalated_for_approval", "reason": "Exceeds ₹500 limit"}
  ```
- If an order exceeds ₹500, the tool refuses automatic write operations and creates a pending authorization request in the Human Specialist Queue.

---

### Q6: Why did you use Server-Sent Events (SSE) instead of WebSockets?
**Answer:**
- **Unidirectional Streaming:** AI token streaming and telemetry are strictly server-to-client streams.
- **HTTP/2 Compatibility:** SSE runs over standard HTTP, eliminating WebSocket firewall/proxy blocking issues.
- **Built-in Reconnection:** SSE has native client reconnection protocols and works seamlessly with standard JWT `Authorization: Bearer` headers using fetch-based stream readers.

---

### Q7: How does PII card masking with the Luhn algorithm work?
**Answer:**
- Regex alone produces false positives on order tracking numbers and serial codes.
- Our guardrail runs regex to find 13-19 digit candidate numbers, then validates each candidate using the **Luhn Algorithm (Mod-10 Checksum)**.
- Only numbers passing the checksum (genuine credit/debit cards) are redacted to `****-****-****-XXXX`, preventing sensitive data ingestion into the LLM or vector store.

---

### Q8: What happens when an angry customer contacts support?
**Answer:**
- The `classify_node` evaluates user sentiment into `neutral`, `positive`, or `angry`.
- If `sentiment == "angry"`, company policy dictates avoiding automated robotic back-and-forth.
- The conditional router immediately transitions to `escalate_node`, transferring the ticket to the Human Specialist Dashboard (`/agent/escalations`) with complete conversation history and sentiment tags.

---

### Q9: How does the system ensure low latency with multi-agent orchestration?
**Answer:**
- In-memory event buffering and non-blocking asynchronous Python execution (`asyncio`).
- Dense vector search is performed in local embedded ChromaDB (< 15ms).
- Sparse BM25 index is cached in memory (< 2ms).
- Single-pass high-confidence queries bypass unnecessary nodes, completing in **< 250ms** on local mock or **< 2.5s** on live GPT-4o.

---

### Q10: How do you evaluate and benchmark the system?
**Answer:**
- We built an automated benchmark suite (`eval/run.py`) running against 10 gold-standard customer scenarios:
  - Routing Accuracy: 90.0%
  - Faithfulness: 100.0%
  - Hallucination Rate: 0.0%
  - Avg Critic Loops: 1.1 loops
  - Avg Latency: 177 ms
