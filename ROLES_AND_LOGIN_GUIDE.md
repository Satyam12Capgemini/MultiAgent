# Support Copilot: Roles, Responsibilities & Login Credentials Guide

> Comprehensive operational guide detailing the responsibilities of Customer, Support Agent, and Administrator roles, their corresponding portal screens, workflows, and demo login credentials.

---

## Table of Contents

1. [Role Overview & Hierarchy](#1-role-overview--hierarchy)
2. [Role Breakdown & Detailed Responsibilities](#2-role-breakdown--detailed-responsibilities)
   - [👤 Customer](#-customer)
   - [🛡️ Support Agent (Human Specialist)](#️-support-agent-human-specialist)
   - [⚙️ System Administrator](#️-system-administrator)
3. [Demo Login Credentials](#3-demo-login-credentials)
4. [Step-by-Step Portal Walkthroughs](#4-step-by-step-portal-walkthroughs)
   - [How Support Agents Handle Escalated Tickets](#how-support-agents-handle-escalated-tickets)
   - [How Administrators Manage KB, Evaluations & Analytics](#how-administrators-manage-kb-evaluations--analytics)
5. [Security & Access Control Matrix (RBAC)](#5-security--access-control-matrix-rbac)

---

## 1. Role Overview & Hierarchy

Support Copilot provides three dedicated portals tailored to distinct operational personas:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 ROLES & RESPONSIBILITIES                                │
├───────────────┬───────────────────────────┬────────────────────────────────────────────┤
│ Role          │ Main Screens / Routes     │ Core Responsibilities                      │
├───────────────┼───────────────────────────┼────────────────────────────────────────────┤
│ 👤 Customer   │ • /chat                   │ • Natural language chat with AI Copilot.   │
│               │ • /tickets                │ • View inline citations [1], [2] & trace.  │
│               │ • /tickets/:id            │ • Submit satisfaction feedback (👍/👎).    │
├───────────────┼───────────────────────────┼────────────────────────────────────────────┤
│ 🛡️ Support    │ • /agent/escalations      │ • Review AI-flagged escalations.           │
│    Agent      │ • /agent/escalations/:id  │ • Inspect failed drafts & customer mood.   │
│ (Specialist)  │ • /tickets                │ • Approve refunds exceeding ₹500 limit.    │
│               │                           │ • Send manual human replies to customers.  │
├───────────────┼───────────────────────────┼────────────────────────────────────────────┤
│ ⚙️ System     │ • /admin/kb               │ • Knowledge Base: Ingest PDF/Markdown docs │
│    Admin      │ • /admin/eval             │   and synchronize ChromaDB vectors.        │
│               │ • /admin/analytics        │ • Run automated 10-case eval benchmarks.   │
│               │ • All Agent & User routes │ • Monitor token usage, latency, and costs. │
└───────────────┴───────────────────────────┴────────────────────────────────────────────┘
```

---

### 👤 Customer
The **Customer** is the end-user seeking technical support, billing inquiries, or general policy information:
- **Dynamic Registration & Account Isolation:** Any user can sign up with their own name, email, and password. Data is strictly partitioned using `customer_id`.
- **Pre-loaded Dynamic Order History:** Upon registration, 5 diverse, realistic sample orders (with varied statuses like *Delivered*, *Shipped*, *Out for Delivery*, *Processing*, and various product types) are seeded into the customer's account.
- **Interactive "📦 My Orders" Drawer & Chips:** Customers can view all their order numbers, statuses, items, and amounts in a collapsible drawer or quick cards with 1-click inquiry chips (e.g. 🔍 *Track*, 💳 *Refund*).
- **Intelligent LLM Inquiries:** Natural questions (e.g. *"What is the progress of my order?"*) are processed by the LLM (`openai.gpt-4o`) using real SQL database records to provide personalized, accurate, and conversational updates.
- **Transparent Citations:** See exact document sources `[1]`, `[2]` for every factual claim.
- **Trace Visibility:** View high-level progress indicators (e.g. *"Running guardrails"*, *"Fact-checking with critic"*).
- **Feedback Loop:** Rate answers as helpful (👍) or unhelpful (👎) to train future retrieval scoring.

---

### 🛡️ Support Agent (Human Specialist)
The **Support Agent** handles tickets that cannot be safely or reliably resolved by the autonomous AI:

1. **Handling Escalation Triggers:**
   - **Angry Customer Sentiment:** If a customer is frustrated (e.g., double billing), the AI stops robotic replies and transfers the ticket to the agent queue.
   - **Low Classifier Confidence ($< 60\%$):** When query intent is ambiguous.
   - **Critic Loop Cap ($== 3$):** When the AI fails 3 grounding verification attempts.
   - **High-Value Refunds ($> ₹500$):** Financial guardrails prevent auto-refunds above ₹500; agents review and authorize them.
2. **Deep Context Inspection:**
   - Review customer profile and order history.
   - Inspect the AI's failed draft answers and the Critic's rejection reasons.
   - Review the knowledge chunks retrieved by ChromaDB.
3. **Resolution & Handoff:**
   - Write a verified manual response that syncs directly into the customer's chat window.
   - Mark the ticket as `resolved` or `closed`.

---

### ⚙️ System Administrator
The **Administrator** manages system configuration, knowledge bases, evaluation benchmarks, and observability:

1. **Knowledge Base Management (`/admin/kb`):**
   - Upload new Markdown manuals, technical troubleshooting guides, and PDF policies.
   - Configure chunking parameters (chunk size: 500 characters, overlap: 50 characters).
   - Ingest chunks into ChromaDB (1536-dimensional embeddings) and update the in-memory BM25 keyword index.
2. **Evaluation & Accuracy Benchmarking (`/admin/eval`):**
   - Execute automated evaluation benchmarks over gold-standard test suites (`eval/dataset.json`).
   - Compare performance metrics with **Critic ON** vs **Critic OFF**.
   - Measure Routing Accuracy ($> 90\%$), Faithfulness ($100\%$), and Hallucination Rates ($0\%$).
3. **Observability & Analytics (`/admin/analytics`):**
   - Monitor total ticket volume broken down by domain (`billing`, `tech`, `general`).
   - Track LLM token consumption (prompt vs completion tokens) and estimated API costs.
   - Measure p50 and p95 latency percentiles.

---

## 3. Login Credentials & Dynamic Customer Registration

Support Copilot combines fixed administrator/specialist accounts with **dynamic self-service registration for unlimited customers**:

### A. Fixed Administrative Accounts (Pre-Seeded)
The Agent and Admin roles are fixed system operators:

| Role | Email Address | Password | Default Redirect Page | Role Description |
|---|---|---|---|---|
| **🛡️ Support Agent** | `agent@example.com` | `Password@123` | `/agent/escalations` | Frontline human specialist queue |
| **⚙️ System Admin** | `admin@example.com` | `Password@123` | `/admin/analytics` | Full system administrator & manager |

---

### B. Dynamic Customer Accounts (Unlimited Scale & Sign Up)
Customers are **NOT hardcoded**. The system supports thousands of distinct customers via dynamic JWT registration:

1. **Self-Service Registration:**
   - Any new customer can open `http://localhost:4200/login`, click the **`New Customer Sign Up`** tab, enter their Name, Email, and Password, and instantly create an account.
   - Triggers `POST /api/v1/auth/register`, which auto-generates a unique `customer_id` (e.g. `cust-a1b2c3d4`), hashes the password using bcrypt, and issues a signed JWT token.
2. **Strict Customer Data Isolation:**
   - Every ticket created by Customer A is tagged with `customer_id = 'cust-A'`.
   - When Customer A accesses `/tickets` or `/tickets/:id`, the API enforces `where(Ticket.customer_id == user.customer_id)`.
   - Customer A **cannot view, list, or tamper with** Customer B's tickets (cross-customer queries return a `404 Not Found`).
   - Support Agents and System Admins have elevated privileges to view tickets across all customers.

---

### C. Quick Demo Login Buttons
On the login screen (`http://localhost:4200/login`), quick-fill buttons are provided for instant testing:
- **`Customer` Button:** Auto-fills pre-seeded customer `aditya.sharma@example.com` / `Password@123`.
- **`Agent` Button:** Auto-fills `agent@example.com` / `Password@123`.
- **`Admin` Button:** Auto-fills `admin@example.com` / `Password@123`.

---

## 4. Step-by-Step Portal Walkthroughs

### How Support Agents Handle Escalated Tickets
1. Sign in as `agent@example.com` / `Password@123`.
2. Navigate to **Escalations Queue** (`/agent/escalations`).
3. Click on any ticket with status **`escalated`** (e.g., *"Double charge complaint"*).
4. Inspect the **Escalation Context Drawer**:
   - **Reason:** `angry_customer_sentiment`
   - **Classification:** `Billing Agent (95% confidence)`
   - **Last AI Draft:** View what the bot attempted to answer.
5. In the reply composer at the bottom, type the human resolution:
   > *"Hello Aditya, I have reviewed your account and verified the duplicate transaction. I have authorized a full refund of ₹299 for order ORD-10023. You will receive the credit in 3-5 business days."*
6. Click **Send Reply & Resolve**. The message immediately synchronizes with the customer's chat screen.

---

### How Administrators Manage KB, Evaluations & Analytics
1. Sign in as `admin@example.com` / `Password@123`.
2. Navigate to **KB Admin** (`/admin/kb`):
   - Review existing ingested documents (`Router Troubleshooting Guide`, `Account Policy`, `Shipping FAQ`).
   - Click **Upload Document** to add new company policies.
3. Navigate to **Evaluation** (`/admin/eval`):
   - Click **Run Benchmark Suite (Critic ON)**.
   - View live pass/fail matrix across all 10 test cases, measuring routing accuracy and latency.
4. Navigate to **Analytics** (`/admin/analytics`):
   - View ticket volume metrics, LLM token consumption breakdown, and latency graphs.

---

## 5. Security & Access Control Matrix (RBAC)

Access is strictly enforced via **JWT Bearer Tokens** and Angular **Role Guards**:

```
┌─────────────────────────────────┬──────────┬──────────┬──────────┐
│ Screen / Resource               │ Customer │  Agent   │  Admin   │
├─────────────────────────────────┼──────────┼──────────┼──────────┤
│ Customer Chat (/chat)           │    ✅    │    ✅    │    ✅    │
│ My Tickets (/tickets)           │    ✅    │    ✅    │    ✅    │
│ Escalations Queue (/agent/...)  │    ❌    │    ✅    │    ✅    │
│ Manual Reply API (/reply)       │    ❌    │    ✅    │    ✅    │
│ KB Document Upload (/admin/kb)  │    ❌    │    ❌    │    ✅    │
│ Eval Benchmark (/admin/eval)    │    ❌    │    ❌    │    ✅    │
│ Analytics Dashboard (/analytics)│    ❌    │    ❌    │    ✅    │
└─────────────────────────────────┴──────────┴──────────┴──────────┘
```
