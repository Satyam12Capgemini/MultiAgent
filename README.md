# 🤖 Support Copilot: Multi-Agent Customer Support System

> Enterprise multi-agent customer support platform featuring **LangGraph**, **FastAPI**, **Angular**, **Hybrid RAG (ChromaDB + BM25 with RRF)**, a deterministic **Grounding-Critic fact-checking loop**, **Guardrails (PII masking + Prompt-injection scan)**, and **Resumable Human Escalation**.

---

## 📚 Complete Project Documentation

- 📘 [**Project Overview & Problems Solved**](PROJECT_OVERVIEW.md) — What is Support Copilot, why multi-agent, personas, and tech stack.
- 🔀 [**Architecture & Execution Flow**](ARCHITECTURE_FLOW.md) — Step-by-step routing flow from user message to specialist agents, RAG, critic loop, and escalation.
- ⚡ [**Features & Superpowers**](FEATURES_AND_SUPERPOWERS.md) — PII guardrails, ₹500 financial safety limit, 0% hallucination critic, and live trace UI.
- 🎯 [**Resume & Technical Interview Guide**](INTERVIEW_RESUME_GUIDE.md) — 1-minute elevator pitch, resume bullets, and technical Q&As.
- 📋 [**Backend System Design Specification**](plan.md) — Full technical architecture and schema reference.
- 🎨 [**Frontend UI/UX Specification**](Frontendplan.md) — Calm console design tokens, components, and state management.

---

## 🏗️ System Architecture & Workflow

```
Customer Message
      │
      ▼
[Guard Node: PII Masking (Luhn Card/Email/ID) + Prompt-Injection Scan]
      │
      ▼
[Classifier Node: Intent & Sentiment Analysis] ── Low Conf / Angry ──► [Human Escalation Queue]
      │
      ├──► [Billing Agent]  ── (SQL Tools: Orders, Safe Refund Limits)
      ├──► [Tech Agent]     ── (Hybrid RAG: Vector + BM25 Fusion over Tech Docs)
      └──► [General Agent]  ── (Hybrid RAG: Vector + BM25 Fusion over Policy/FAQ)
                │
                ▼
      [Grounding Critic Node: Atomic Claim Decomposition & Code-level Score Rubric]
                │
                ├── Score < 80% and Loops < 3 ──► Retry Agent with Actionable Feedback
                ├── Loops == 3 ───────────────► Escalate to Human Specialist
                └── Score >= 80%
                        │
                        ▼
      [Finalize Node: Policy Sanitization + SSE Token Stream + Citation Mapping]
                        │
                        ▼
               Customer Chat Bubble
```

---

## 🚀 Key Features & Highlights

- **Multi-Agent Permission Separation:**
  - **Billing Agent:** Direct access to SQL orders database with code-enforced ₹500 auto-refund threshold. Over-limit requests create pending supervisor approvals.
  - **Tech Agent:** Grounded RAG synthesis with strict `[1]`, `[2]` citation markers.
  - **General Agent:** Policy & FAQ guidance with verified knowledge grounding.
  - **Grounding Critic:** Decomposes answers into atomic claims; validates each against retrieved context (`SUPPORTED`, `PARTIAL`, `UNSUPPORTED`). Calculates numeric score in Python code to prevent LLM critic drift.
- **Guardrails:**
  - PII masking with regex and Luhn algorithm verification for credit/debit cards.
  - Prompt injection detection filtering jailbreaks and system override attempts.
  - Output policy enforcer stripping internal action leaks and unverified refund promises.
- **Human-in-the-Loop Escalation:**
  - Resumable escalation dashboard displaying classifier confidence, retrieved chunks, last draft, and refund approval cards.
  - Direct human-agent replies synced back to customer conversation.
- **Evaluation Benchmark:**
  - Built-in test suite and evaluation runner (`python -m eval.run`) measuring **Routing Accuracy**, **Faithfulness**, and **Hallucination Rate** with Critic ON vs Critic OFF.

---

## 📊 Measured Benchmark Results

| Metric | With Critic Loop (Full Graph) | Baseline (Critic OFF) | Impact |
|---|---|---|---|
| **Routing Accuracy** | **90.0%** | 90.0% | Stable high precision |
| **Faithfulness Score** | **100.0%** | 80.0% | **+ 20.0%** |
| **Hallucination Rate** | **0.0%** | 20.0% | **↓ 20.0% Reduction** |
| **Average Critic Loops** | **1.1** | N/A | Fast convergence |
| **Average Latency** | **177 ms** | 183 ms | High responsiveness |

---

## 🛠️ Quick Start & Local Setup

### 1. Prerequisites
- Python 3.11+
- Node.js 20+ & npm

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Initialize database & seed demo accounts/orders
python -m app.cli seed

# Ingest sample knowledge base documents into ChromaDB + MSSQL/SQLite
python -m app.cli ingest ../data/kb_samples

# Run test suite
python -m pytest -v

# Run evaluation runner
python -m eval.run --dataset ../eval/dataset.json --critic on --label baseline-with-critic

# Start FastAPI server (Runs on port 8000)
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install packages
npm install

# Start Angular dev server (Runs on port 4200)
npm start
```

Open [http://localhost:4200](http://localhost:4200) in your browser.

---

## 👥 Demo Accounts (Password: `Password@123`)

| Role | Email | Capabilities |
|---|---|---|
| **Customer** | `aditya.sharma@example.com` | Live chat, citation view, feedback, ticket tracking |
| **Agent** | `agent@supportcopilot.local` | Escalation review, refund approvals, human reply |
| **Admin** | `admin@supportcopilot.local` | KB manager, evaluation runs, system analytics |

---

## 📁 Repository Structure

```
MultiAgent-Implementation/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/            # config.py, security.py, logging.py, errors.py
│   │   ├── api/v1/          # auth, tickets, escalations, kb, rag, eval, analytics
│   │   ├── db/              # models.py, session.py
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # ticket_service, escalation_service, kb_service, eval_service
│   │   ├── llm/             # GenerativeEngine client, Fake client, embeddings
│   │   ├── rag/             # chunker, chroma_store, bm25, fusion (RRF), retriever, ingest
│   │   ├── graph/           # state, nodes (guard, classify, billing, tech, general, critic, escalate, finalize), builder
│   │   ├── tools/           # billing_tools (with refund guardrails)
│   │   └── guardrails/      # pii, injection, policy
│   ├── tests/               # 13 pytest unit & integration tests
│   ├── cli.py               # seed, ingest, reset-db, reindex
│   └── requirements.txt
├── frontend/
│   ├── src/app/
│   │   ├── core/            # auth.service, interceptor, role.guard, run-stream.service
│   │   ├── features/        # chat (with trace panel), tickets, agent escalations, kb, eval, analytics
│   │   └── shared/          # navbar, models
│   ├── proxy.conf.json
│   └── package.json
├── data/kb_samples/         # Router Guide, Billing Policy, Shipping FAQ
├── eval/                    # dataset.json, run.py, results/
├── plan.md                  # Comprehensive Technical Specification
└── README.md
```
