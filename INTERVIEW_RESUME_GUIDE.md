# Support Copilot: Resume & Technical Interview Guide

> Quick-reference guide for presenting this project on your resume, in system design rounds, and in multi-agent AI technical interviews.

---

## 1. One-Minute Elevator Pitch (Say this in Interviews)

> *"I designed and implemented **Support Copilot**, an enterprise-grade Multi-Agent Customer Support platform built with **FastAPI**, **LangGraph**, **Angular 17+**, **ChromaDB**, and **MSSQL**. The system routes customer queries to specialized, permission-scoped agents (Billing, Tech, General), leverages **Hybrid RAG** (Dense Vector + BM25 with Reciprocal Rank Fusion), and enforces an autonomous **Critic Grounding Loop** to achieve a 0% hallucination rate. For safety, it features regex + Luhn PII redaction, code-level ₹500 financial limits, real-time Server-Sent Events (SSE) trace streaming, and a Human-in-the-Loop escalation pipeline."*

---

## 2. Resume Bullet Points (Ready to Copy-Paste)

- **Engineered an Autonomous Multi-Agent Customer Support System** using **LangGraph**, **FastAPI**, and **Capgemini Generative Engine (`openai.gpt-4o`)**, achieving 90%+ routing accuracy and sub-2.5s response latency.
- **Implemented a Cyclic Critic-Grounding Loop** that fact-checks draft answers against retrieved knowledge base chunks before final delivery, reducing hallucination rates to 0%.
- **Developed a Hybrid RAG Pipeline** combining dense ChromaDB embeddings (`text-embedding-3-small`) and sparse BM25 keyword matching via Reciprocal Rank Fusion ($k=60$).
- **Integrated Code-Enforced Financial & Security Guardrails**, including Regex + Luhn payment card masking, prompt injection heuristic scanners, and automated ₹500 refund threshold safety caps.
- **Built a Modern Angular 17+ Frontend** featuring standalone components, Signals state management, and real-time Server-Sent Events (SSE) streaming for live node-by-node execution tracing.

---

## 3. Key Technical Interview Questions & Answers

### Q1: Why did you choose a Multi-Agent architecture instead of a single LLM prompt?
> **Answer:** 
> *"A single monolithic LLM prompt suffers from tool sprawl, permission leakage, and higher hallucination rates. In our architecture, the split is based on strict data boundaries and least privilege. The Billing Agent has SQL access for order lookups with a hardcoded ₹500 refund limit; the Tech Agent only has read access to technical hardware manuals; and the Critic has no tools at all, acting purely as an unbiased verification judge."*

---

### Q2: How does your Hybrid RAG system work?
> **Answer:**
> *"Dense vector search alone often misses exact keyword codes (like router error code 'ERR-502' or order ID 'ORD-10023'). We implemented Hybrid Retrieval: dense semantic search via ChromaDB cosine similarity combined with sparse keyword search via in-memory BM25. We then merge and re-rank the candidate chunks using Reciprocal Rank Fusion with $k=60$, ensuring high precision for both semantic queries and exact part numbers."*

---

### Q3: How do you prevent infinite loops in the Critic cycle?
> **Answer:**
> *"The LangGraph state maintains a `loops` counter. Each time the Critic evaluates a draft and scores it below the 0.80 threshold, it increments the loop count and returns actionable feedback. If `loops >= 3` and the answer is still not verified, the graph conditional router triggers the `escalate_node`, transferring the ticket to the Human Specialist queue with the full trace and attempted drafts."*

---

### Q4: How does the frontend achieve real-time streaming without WebSocket overhead?
> **Answer:**
> *"We utilized HTTP Server-Sent Events (SSE) via FastAPI's `EventSourceResponse` and a fetch-based stream client in Angular. As each graph node executes, it emits structured events (`run_started`, `classified`, `retrieved`, `critic_scored`, `token`, `final`, `escalated`). The frontend uses Angular Signals to update the chat bubble and the Multi-Agent Trace panel reactively."*
