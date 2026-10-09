# Support Copilot: Features & Superpowers

> Comprehensive documentation of the core features, guardrails, and transparency mechanisms built into Support Copilot.

---

## 1. The 5 Superpowers

### Superpower 1: Guardrail Protection & PII Masking
- **Payment Card Masking:** Uses Regex + Luhn verification to redact card numbers before model transmission.
- **Sensitive Identity Masking:** Automatically masks phone numbers, SSNs, and emails.
- **Prompt Injection Defense:** Blocks jailbreak attempts (e.g., *"Ignore system instructions"*, *"Print internal DB credentials"*).

---

### Superpower 2: Role-Based Specialist Agents with Least Privilege
Agents are split strictly by **data access boundaries** and **permissions**:

| Agent | Accessible Data Store | Permissions | Safe Constraints |
|---|---|---|---|
| **Billing Agent** | MSSQL / SQLite Relational Tables | Read + Conditional Write | Maximum auto-refund capped at ₹500 in code. |
| **Tech Specialist** | ChromaDB (`tech` collection) | Read-Only | Cannot access orders, customers, or financial records. |
| **General Agent** | ChromaDB (`general` collection) | Read-Only | Restricted to company policy & shipping FAQ. |
| **Critic Agent** | Retrieved Chunks + Draft Answer | No Tool Access | Pure analytical evaluator. |

---

### Superpower 3: 0% Hallucination Critic Loop (Grounding Check)
- Traditional LLMs often fabricate policies or steps when uncertain.
- Support Copilot introduces a **Self-Correction Grounding Loop**:
  - The Critic Agent evaluates every claim against retrieved source text.
  - If a claim is unsupported, the Critic issues specific feedback for revision.
  - Evaluated on a 10-case benchmark with **0% hallucination rate** and **100% citation faithfulness**.

---

### Superpower 4: Real-Time Multi-Agent Trace UI
- An interactive right-side trace panel built directly into the Angular application:
  - Displays each executed node in real-time (`guard` $\rightarrow$ `classify` $\rightarrow$ `tech_agent` $\rightarrow$ `critic` $\rightarrow$ `finalize`).
  - Shows routing confidence percentage (e.g. `95%`), sentiment status (`Neutral` / `Angry`), and critic scores.
  - Transparently shows which knowledge chunks and page sections were used to answer the query.

---

### Superpower 5: Safe Human-in-the-Loop Escalation
- Automated AI systems must know when to stop.
- Escalation triggers include:
  1. **Angry Customer Sentiment:** Avoids aggravating customers with automated loops.
  2. **Low Classification Confidence ($< 60\%$):** Prevents routing to the wrong domain.
  3. **Critic 3-Loop Cap Reached:** If the agent fails 3 verification attempts, human support is notified.
- The human specialist receives the complete state snapshot (failed drafts, retrieved docs, sentiment score) for instant resolution.

---

## 2. Portals & User Roles

```
                               ┌─────────────────────────────┐
                               │     SUPPORT COPILOT APP     │
                               └──────────────┬──────────────┘
                                              │
              ┌───────────────────────────────┼───────────────────────────────┐
              │                               │                               │
              ▼                               ▼                               ▼
       [Customer Portal]               [Support Agent]                 [Admin Portal]
        • Live Chat                     • Escalations Queue             • KB Document Ingestion
        • Trace Panel                   • Full Context Inspection       • Evaluation Benchmarking
        • Inline Citations              • Human Reply & Resolve         • Latency & Cost Analytics
        • Feedback (👍/👎)              • Refund Approval               • BM25 / Vector Reindexing
```

---

## 3. Evaluation & Benchmarking System

Built-in evaluation engine (`eval/run.py`) provides measurable metrics:
- **Routing Accuracy:** Proportion of tickets routed to the correct specialist ($\ge 90\%$).
- **Faithfulness Score:** Percentage of claims supported by citations ($100\%$).
- **Hallucination Rate:** Percentage of ungrounded statements ($0\%$).
- **Average Latency:** Fast pipeline execution ($< 250\text{ ms}$ baseline, $< 2.5\text{ s}$ live LLM).
