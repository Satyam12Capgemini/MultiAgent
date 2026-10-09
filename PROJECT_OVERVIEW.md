# Support Copilot: Project Overview

> **Autonomous Multi-Agent Customer Support System with Grounding Critic Loop, Hybrid RAG, Financial Guardrails, and Human-in-the-Loop Escalation.**

---

## 1. What is Support Copilot?

**Support Copilot** is an enterprise-grade AI customer support platform powered by a multi-agent graph architecture. Unlike traditional single-prompt chatbots (like ChatGPT wrappers) that suffer from hallucinations, security vulnerabilities, and uncontrolled actions, Support Copilot uses specialized, permission-scoped autonomous agents orchestrated with **LangGraph**, **FastAPI**, and **Angular 17+**.

---

## 2. Real-World Problems It Solves

| Problem with Standard Chatbots | How Support Copilot Solves It |
|---|---|
| **Hallucination & Fake Answers:** Chatbots make up facts and fake policies. | **Autonomous Critic Loop:** Every draft answer is scored against retrieved source documents. Only answers with $\ge 80\%$ grounding pass to the user. |
| **Security & Data Leaks:** Users accidentally send credit card numbers or malicious prompt injection attacks. | **Code-Enforced Guardrails:** Automatic regex + Luhn algorithm PII masking and dual-layer heuristic prompt injection filters. |
| **Financial Fraud:** Chatbots executing unapproved refunds. | **Hard-Coded Safe Limits:** Billing Agent can only auto-refund orders under ₹500. Everything else requires mandatory human manager approval. |
| **Black-Box Confusion:** Users and agents don't know why an answer was given. | **Live Multi-Agent Trace Panel:** Real-time Server-Sent Events (SSE) stream every node transition, tool execution, and fact-check score. |
| **Dead-End Frustration:** Bot gets stuck when user is angry. | **Sentiment-Aware Escalation:** Automatically routes angry customers to a human specialist queue with full conversation history and attempted drafts. |

---

## 3. Technology Stack

- **Agent Orchestration:** LangGraph (StateGraph, Conditional Routing, Cyclic Self-Correction)
- **Backend API:** FastAPI (Async, Pydantic v2, Server-Sent Events streaming)
- **Large Language Model:** Capgemini Generative Engine (`openai.gpt-4o`) & `text-embedding-3-small`
- **Hybrid Vector Store & RAG:** ChromaDB (Dense Cosine Similarity) + In-Memory BM25 (Sparse Keyword Search) with Reciprocal Rank Fusion ($k=60$)
- **Relational Databases:** Microsoft SQL Server (MSSQL 2022 / LocalDB) & SQLite (via SQLAlchemy 2.0 async + `aioodbc`/`aiosqlite`)
- **Frontend Client:** Angular 17+ (Standalone Components, Signals, Reactive Forms, Dual Light/Dark Calm Console Theme)

---

## 4. The 3 Portals (Personas)

Support Copilot provides three customized portals tailored to specific user roles:

1. **Customer Portal (`/chat`, `/tickets`):**
   - Natural language support chat with streaming responses.
   - Grounded citations `[1]`, `[2]` with document titles.
   - Interactive feedback collection (👍 / 👎).
   - Trace summary and past ticket status tracker.

2. **Support Agent Portal (`/agent/escalations`):**
   - Priority queue for tickets flagged by the AI (Angry sentiment, Low classifier confidence, Critic cap reached).
   - Deep inspection view: see customer info, reason for escalation, failed AI drafts, and retrieved documentation.
   - One-click reply and manual resolution.

3. **Administrator Portal (`/admin/kb`, `/admin/eval`, `/admin/analytics`):**
   - **Knowledge Base Manager:** Upload Markdown/PDF documentation, auto-chunk, and sync vectors.
   - **Evaluation Dashboard:** Run automated 10-case benchmark suites with routing accuracy, faithfulness, hallucination rate, and latency metrics.
   - **Analytics:** View token usage, LLM latency p50/p95, and cost breakdown.
