# Support Copilot: Frontend Documentation (Angular)

> UI/UX design, theme, page specifications, component library, state management and implementation plan for the Angular client.
> Companion to `SUPPORT_COPILOT_DOCUMENTATION.md` (backend, API and agent design). Endpoint names, roles, routes and SSE events here match that document.

| Field | Value |
|-------|-------|
| Document status | Draft v1.0 (planning, local-only scope) |
| Framework | Angular (standalone components, Signals), latest stable your CLI installs |
| UI library | Angular Material + custom design tokens |
| Scope | Build and run locally; no deployment |

---

## Table of Contents

1. [Frontend Overview](#1-frontend-overview)
2. [Tech Stack and Conventions](#2-tech-stack-and-conventions)
3. [Design Language and Theme](#3-design-language-and-theme)
4. [Layout and Navigation](#4-layout-and-navigation)
5. [Page-by-Page UI Specification](#5-page-by-page-ui-specification)
6. [Shared Component Library](#6-shared-component-library)
7. [Agent Trace Panel (Signature Feature)](#7-agent-trace-panel-signature-feature)
8. [State Management](#8-state-management)
9. [Services and API Mapping](#9-services-and-api-mapping)
10. [TypeScript Models](#10-typescript-models)
11. [Routing, Guards and Interceptors](#11-routing-guards-and-interceptors)
12. [SSE Streaming Client](#12-sse-streaming-client)
13. [Error Handling and UX States](#13-error-handling-and-ux-states)
14. [Accessibility and Responsiveness](#14-accessibility-and-responsiveness)
15. [Performance Guidelines](#15-performance-guidelines)
16. [Testing Strategy](#16-testing-strategy)
17. [Folder Structure](#17-folder-structure)
18. [Environment and Local Setup](#18-environment-and-local-setup)
19. [Frontend Implementation Roadmap](#19-frontend-implementation-roadmap)
20. [UX Acceptance Checklist and Demo Script](#20-ux-acceptance-checklist-and-demo-script)

---

## 1. Frontend Overview

The Angular client serves **three audiences** with one app:

| Role | What they do | Main screens |
|------|--------------|--------------|
| Customer | Ask for help, follow a ticket, rate answers | Chat, My Tickets, Ticket Detail |
| Support agent | Handle escalated tickets, approve refunds | Escalation Queue, Escalation Detail |
| Admin | Manage knowledge base, run evaluations, view analytics | KB Manager, Eval Dashboard, Analytics |

### UX principles

1. **Transparency over magic.** The user can see which agent is working, what was retrieved and how the critic scored the answer. This is the project's differentiator.
2. **Trust through citations.** Every factual answer shows its sources; unsupported answers never reach the chat bubble.
3. **Calm under load.** Streaming, progress stages and skeleton loaders so waiting never feels frozen.
4. **Safe actions are explicit.** Refund approvals and deletions always ask for confirmation and show what will happen.
5. **Two depths of detail.** Customers see a simple stage indicator; agents and admins can expand the full trace.

---

## 2. Tech Stack and Conventions

| Concern | Choice | Notes |
|---------|--------|-------|
| Framework | Angular, standalone components only | No NgModules |
| Change detection | `OnPush` everywhere, Signals for local and store state | RxJS only for streams and HTTP |
| Control flow | Built-in `@if`, `@for`, `@switch` | Always `track` in `@for` |
| UI components | Angular Material | Themed with design tokens (section 3) |
| Icons | Material Symbols (outlined) | Self-hosted font to avoid CDN dependency |
| Fonts | Inter (UI), JetBrains Mono (ids, payloads, code) | Self-hosted via `@fontsource` packages |
| Markdown rendering | `ngx-markdown` | For assistant answers; sanitized |
| Charts | `ng2-charts` (Chart.js) | Analytics and eval dashboards |
| SSE | `@microsoft/fetch-event-source` | `EventSource` cannot send an `Authorization` header |
| Forms | Typed Reactive Forms | |
| HTTP | `HttpClient` + functional interceptors | |
| Styling | SCSS + CSS custom properties | Tokens drive both light and dark themes |
| Lint/format | ESLint + Prettier | |

### Coding conventions

- One component per folder: `name.component.ts|html|scss|spec.ts`.
- Smart (container) components fetch data and own state; presentational components take `input()`s and emit `output()`s.
- Features are lazy-loaded via `loadComponent` / `loadChildren`.
- No business logic in templates; no direct `HttpClient` use in components.
- API models live in `shared/models` and mirror the backend schemas.

---

## 3. Design Language and Theme

### 3.1 Theme concept: "Calm Console"

A modern, data-forward support console: clean surfaces, generous whitespace, soft rounded corners and one confident accent colour. It should feel like a professional SaaS helpdesk with an engineer's transparency layer (the trace panel). Light and dark themes are both first-class; the app follows the OS preference on first load and remembers the user's choice.

**Mood keywords:** trustworthy, calm, precise, technical-but-friendly.

### 3.2 Colour tokens

Defined as CSS custom properties on `:root` (light) and `[data-theme="dark"]`.

| Token | Light | Dark | Use |
|-------|-------|------|-----|
| `--bg` | `#F8FAFC` | `#0B1020` | App background |
| `--surface` | `#FFFFFF` | `#111827` | Cards, panels |
| `--surface-2` | `#F1F5F9` | `#1A2332` | Subtle fills, table headers |
| `--border` | `#E2E8F0` | `#273244` | Dividers, outlines |
| `--text` | `#0F172A` | `#E5E7EB` | Primary text |
| `--text-muted` | `#64748B` | `#9CA3AF` | Secondary text |
| `--primary` | `#4F46E5` | `#818CF8` | Primary actions, links, focus |
| `--primary-contrast` | `#FFFFFF` | `#0B1020` | Text on primary |
| `--accent` | `#0D9488` | `#2DD4BF` | Secondary highlights, success-adjacent |
| `--success` | `#16A34A` | `#4ADE80` | Passed checks, resolved |
| `--warning` | `#D97706` | `#FBBF24` | Pending approval, retry |
| `--danger` | `#DC2626` | `#F87171` | Errors, escalation, destructive |
| `--info` | `#0284C7` | `#38BDF8` | Informational |

> Verify every text/background pair meets WCAG AA contrast (4.5:1 for body text) after finalising the palette.

### 3.3 Agent / node colour coding

Used consistently in the trace panel, ticket badges and analytics charts so users learn the colours once.

| Node / Category | Colour (light) | Icon (Material Symbol) |
|-----------------|----------------|------------------------|
| `guard` | Slate `#64748B` | `shield` |
| `classify` | Violet `#7C3AED` | `category` |
| `billing` | Amber `#D97706` | `receipt_long` |
| `tech` | Blue `#2563EB` | `build` |
| `general` | Teal `#0D9488` | `help` |
| `critic` | Rose `#E11D48` | `fact_check` |
| `escalate` | Red `#DC2626` | `support_agent` |
| `finalize` | Green `#16A34A` | `check_circle` |

Dark theme uses lighter tints of the same hues (e.g. violet `#A78BFA`, blue `#60A5FA`).

### 3.4 Typography

| Style | Font | Size / weight / line-height | Use |
|-------|------|-----------------------------|-----|
| Display | Inter | 28 / 700 / 36 | Page titles on dashboards |
| H1 | Inter | 22 / 600 / 30 | Page headers |
| H2 | Inter | 18 / 600 / 26 | Section headers, card titles |
| Body | Inter | 14 / 400 / 22 | Default text |
| Body-lg | Inter | 16 / 400 / 26 | Chat messages |
| Caption | Inter | 12 / 500 / 16 | Meta, badges, timestamps |
| Mono | JetBrains Mono | 12-13 / 400 / 20 | IDs, JSON payloads, scores |

### 3.5 Shape, spacing, elevation, motion

| Token | Value |
|-------|-------|
| Spacing scale | 4, 8, 12, 16, 24, 32, 48 px (`--space-1` to `--space-7`) |
| Radius | `--radius-sm` 6px, `--radius-md` 12px, `--radius-lg` 16px, pill 999px |
| Elevation | `--shadow-1` subtle card shadow; `--shadow-2` for menus and dialogs. Dark theme prefers borders over shadows |
| Motion | 150 ms for hover/focus, 250 ms for panel open/close, `cubic-bezier(0.2, 0, 0, 1)` |
| Reduced motion | Respect `prefers-reduced-motion`: disable slide/pulse animations, keep instant state changes |

### 3.6 Angular Material theming

Keep Material as the component base and map it to the tokens above.

```scss
// styles/_theme.scss  (adjust the mixin to your installed Angular Material version)
@use '@angular/material' as mat;

html {
  @include mat.theme((
    color: (primary: mat.$violet-palette, tertiary: mat.$cyan-palette, theme-type: light),
    typography: Inter,
    density: -1
  ));
}

html[data-theme='dark'] {
  @include mat.theme((color: (primary: mat.$violet-palette, tertiary: mat.$cyan-palette, theme-type: dark)));
}
```

Then override Material system variables with the project tokens (`--mat-sys-primary: var(--primary)` and so on) so one source of truth controls colours. Check the Angular Material docs for the exact API of your version (the `mat.theme` mixin is the current Material 3 approach).

### 3.7 Branding

- Wordmark: **Support Copilot** in Inter 600, with a small glyph (a chat bubble with a check mark) in `--primary`.
- Favicon: the glyph on a rounded square.
- Empty states use simple line illustrations (inline SVG) in `--text-muted` and `--primary`.

### 3.8 Theme toggle

A sun/moon icon button in the top bar. Behaviour: `system` (default) → `light` → `dark`. Stored in `localStorage` (`sc.theme`) and applied by setting `data-theme` on `<html>` before first paint to avoid a flash.

---

## 4. Layout and Navigation

### 4.1 App shell

```
+----------------------------------------------------------------------+
| ◈ Support Copilot            [ search tickets ]        🌓  🔔  (SK) ▾ |  <- top bar (56px)
+------------+---------------------------------------------------------+
|            |                                                         |
|  Chat      |                                                         |
|  Tickets   |                  <router-outlet>                        |
|  ───────   |                                                         |
|  Queue     |                                                         |
|  ───────   |                                                         |
|  KB        |                                                         |
|  Eval      |                                                         |
|  Analytics |                                                         |
|            |                                                         |
+------------+---------------------------------------------------------+
   sidebar 240px (collapses to 72px icons, drawer on mobile)
```

### 4.2 Role-based navigation

| Item | Route | Customer | Agent | Admin |
|------|-------|:--------:|:-----:|:-----:|
| Chat | `/chat` | ✓ | | |
| My Tickets / All Tickets | `/tickets` | ✓ | ✓ | ✓ |
| Escalation Queue | `/agent/escalations` | | ✓ | ✓ |
| Knowledge Base | `/admin/kb` | | | ✓ |
| Evaluation | `/admin/eval` | | | ✓ |
| Analytics | `/admin/analytics` | | | ✓ |

The sidebar renders only items the current role can access. Default landing page after login: customer → `/chat`, agent → `/agent/escalations`, admin → `/admin/analytics`.

### 4.3 Breakpoints

| Name | Width | Behaviour |
|------|-------|-----------|
| Mobile | < 768 px | Sidebar becomes a drawer; chat and trace become tabs |
| Tablet | 768-1199 px | Sidebar collapsed to icons; trace panel is an overlay drawer |
| Desktop | ≥ 1200 px | Full sidebar; chat and trace side by side |

---

## 5. Page-by-Page UI Specification

### 5.1 Login (`/login`)

```
+------------------------------------------+
|                                          |
|              ◈ Support Copilot           |
|        Smart help, with receipts.        |
|                                          |
|   Email     [______________________]     |
|   Password  [______________________] 👁  |
|                                          |
|   [           Sign in            ]       |
|                                          |
|   Demo accounts: Customer · Agent · Admin|
+------------------------------------------+
```

- Centered card on a soft gradient background (primary → accent at 8% opacity).
- Inline validation, disabled button while submitting, error banner on 401.
- "Demo accounts" chips fill in seeded credentials (local demo only).
- API: `POST /auth/login`, then `GET /auth/me`.

### 5.2 Chat (`/chat`), the hero screen

```
+---------------------------------------------+-------------------------------+
| Conversation                                | Agent Trace            [⟷ hide]|
|                                             |                               |
|  (assistant) Hi! How can I help today?      |  ● guard        3 ms   ✓      |
|                                             |  ● classify   640 ms   ✓      |
|            I was charged twice for     (me) |     billing · conf 0.93       |
|            order ORD-10023                  |  ● billing_agent  2.1 s  ✓    |
|                                             |     get_order(ORD-10023)      |
|  (assistant)                                |  ● critic  loop 1             |
|  I can see two charges of ₹499 …  [1] [2]   |     score 0.67  ▾             |
|  ┌ Sources ─────────────────────────┐       |  ↻ retrying (loop 2)          |
|  │ [1] Billing FAQ  [2] Refund Policy│       |  ● billing_agent  1.4 s  ✓    |
|  └──────────────────────────────────┘       |  ● critic  loop 2             |
|  👍 👎                                      |     score 0.91  ✓ passed      |
|                                             |  ● finalize                   |
| ┌─────────────────────────────────────┐     |                               |
| │ Type your message…            [ ➤ ] │     |                               |
| └─────────────────────────────────────┘     |                               |
+---------------------------------------------+-------------------------------+
```

**Behaviour**

- Message list auto-scrolls to the latest message unless the user has scrolled up (then show a "Jump to latest" pill).
- The customer view shows a **stage indicator** above the input while a run is active: *Understanding your request → Looking up information → Checking sources → Writing answer*, derived from trace events.
- Answer text streams token by token **only after the critic passes** (backend sends `token` events post-critic), so rejected drafts never appear in the bubble.
- Assistant messages render Markdown; citation markers `[1]` become clickable chips that scroll to / open the matching source card.
- If the run escalates, a distinct system message appears: "I've passed this to a human agent. You'll hear back here." with a status chip (*Escalated*).
- Refund pending approval shows an amber inline card: "Refund of ₹1,200 is waiting for approval."
- Thumbs up/down under each assistant message calls `POST /tickets/{id}/feedback`.
- Input: multiline textarea, Enter sends, Shift+Enter newline, disabled while a run is streaming, character counter at 80% of the limit.
- Trace panel: visible by default on desktop for agent/admin; for customers it is collapsed to the simple stage indicator with a "Show details" toggle (configurable).

**States:** empty (welcome + 3 suggested prompts), streaming, escalated, error (retry button), offline.

### 5.3 My Tickets / All Tickets (`/tickets`)

```
+----------------------------------------------------------------------+
| Tickets                                         [ + New ticket ]      |
| [ Search… ]  Status ▾  Category ▾  Date range ▾            [ Reset ]  |
+----------------------------------------------------------------------+
| Subject            Category   Status       Critic   Updated            |
|----------------------------------------------------------------------|
| Double charge      ◉ billing  ● Answered    0.91    2 min ago      ›   |
| Router reboots     ◉ tech     ● Escalated   0.62    1 h ago        ›   |
| Reset password     ◉ general  ● Resolved    0.95    Yesterday      ›   |
+----------------------------------------------------------------------+
| Rows per page 20 ▾                              ‹ 1 2 3 … 7 ›         |
+----------------------------------------------------------------------+
```

- Server-side pagination, sorting and filtering via `GET /tickets` params.
- Category chip uses node colour coding; status badge colours: open (info), answered (success), escalated (danger), resolved (muted green), closed (grey).
- Customers see only their tickets; agents/admins see all (backend enforced).
- Mobile: rows become stacked cards.

### 5.4 Ticket Detail (`/tickets/:id`)

Two tabs:

- **Conversation:** full message history, citations, feedback, close button.
- **Trace** (agent/admin, optional for customer): per-run timeline from `GET /tickets/{id}/trace`, runs listed newest first, each expandable.

Header shows subject, category chip, status badge, created/updated times, and critic score of the last run.

### 5.5 Escalation Queue (`/agent/escalations`)

```
+----------------------------------------------------------------------+
| Escalations      [ Open (7) ] [ Claimed by me (2) ] [ Resolved ]      |
+----------------------------------------------------------------------+
| ⚠ Refund over limit      Order ORD-10023   ₹1,200   10 min    [Claim] |
| ⚠ Critic cap reached     Router reboots              1 h      [Claim] |
| ⚠ Angry sentiment        Cancel my plan              2 h      [Claim] |
+----------------------------------------------------------------------+
```

- Reason badge (colour-coded), age with warning colour after a threshold, one-click **Claim**.
- Auto-refresh every 15 s (polling; no websocket needed for v1).

### 5.6 Escalation Detail (`/agent/escalations/:id`)

```
+------------------------------+-----------------------------------------+
| Conversation                 | Context for the agent                   |
|  (customer) …                |  Reason: Refund over limit              |
|  (assistant draft) …         |  Classifier: billing · 0.93 · negative  |
|                              |  ┌ Pending refund ───────────────────┐  |
|                              |  │ ORD-10023  ₹1,200  Duplicate charge│  |
|  ┌────────────────────────┐  |  │ [ Reject ]        [ Approve ]      │  |
|  │ Write a reply…         │  |  └───────────────────────────────────┘  |
|  └────────────────────────┘  |  Retrieved sources (3)  ▾               |
|  [ Send ]  [ Send & resolve ]|  Last draft & critic feedback  ▾        |
+------------------------------+-----------------------------------------+
```

- **Approve / Reject** opens a confirm dialog that restates amount, order and customer, with an optional note. Calls `POST /escalations/{id}/approve-refund`.
- Reply box supports "Send" and "Send & resolve" (`POST /escalations/{id}/reply` with `resolve` flag).
- A suggested reply button can pre-fill the last draft for the agent to edit (optional).

### 5.7 Knowledge Base Manager (`/admin/kb`)

```
+----------------------------------------------------------------------+
| Knowledge Base                              [ ⬆ Upload ]  [ Reindex all ]|
+----------------------------------------------------------------------+
| ┌──────────────── drop files here (PDF, MD, TXT, HTML) ─────────────┐ |
| └────────────────────────────────────────────────────────────────────┘ |
| Title                 Category   Chunks  Status         Actions        |
| Router Guide          tech       24      ● Indexed      ⟳  🗑  ›       |
| Refund Policy         general    9       ◌ Processing…  …              |
| Broken.pdf            tech       0       ✕ Failed       ⟳  🗑  (why?)  |
+----------------------------------------------------------------------+
| Search test:  [ router keeps rebooting ] [tech ▾] [ Run ]              |
|   0.82  Router Guide · chunk 7  "If the router restarts…"              |
+----------------------------------------------------------------------+
```

- Drag-and-drop uploader with category and title fields.
- Status chips update by polling `GET /kb/documents` while any document is `pending` or `processing`.
- Failed items show the error message in a tooltip/dialog.
- Delete requires confirmation ("Removes document and all chunks from the index").
- **Search test panel** calls `POST /kb/search` so admins can verify retrieval quality without the LLM.

### 5.8 Evaluation Dashboard (`/admin/eval`)

- Run list with label, date, critic on/off, key metrics.
- **Comparison view:** select two runs, see a side-by-side metric table with deltas (green/red).
- Metric cards: routing accuracy, retrieval hit-rate, faithfulness, hallucination rate, avg loops, latency p50/p95, cost per ticket.
- Per-case table with filters (failed only, category) and expandable details showing expected vs actual.
- "Start run" dialog: dataset, critic toggle, label. Progress bar while `running`.
- API: `GET/POST /eval/runs`, `GET /eval/runs/{id}`, `GET /eval/datasets`.

### 5.9 Analytics (`/admin/analytics`)

```
+----------------------------------------------------------------------+
| Analytics                                   Last 7 days ▾             |
+----------------------------------------------------------------------+
| [Tickets 134] [Escalation rate 18%] [Avg critic 0.86] [Avg loops 1.4] |
|                                                                        |
|  Tickets by category (donut)     |  Escalations by reason (bar)       |
|  Avg latency per node (bar)      |  Tokens & cost per day (line)      |
+----------------------------------------------------------------------+
```

- Charts use the node colour coding.
- Data from `GET /analytics/summary` and `GET /analytics/usage`.
- Each chart has an accessible table fallback (toggle "View as table").

### 5.10 Utility pages

- `/403` Forbidden, `/404` Not found, and a global error page. Each has a friendly message and a "Back to home" button.

---

## 6. Shared Component Library

| Component | Purpose | Key inputs |
|-----------|---------|------------|
| `MessageBubbleComponent` | Chat message (customer / assistant / human / system) | `message`, `streaming` |
| `MarkdownViewComponent` | Safe Markdown rendering with citation marker support | `content`, `citations` |
| `CitationChipComponent` | Clickable `[n]` marker linking to a source | `n`, `source` |
| `SourceCardComponent` | Title, snippet, score of a retrieved chunk | `chunk` |
| `StageIndicatorComponent` | Simple "what's happening" stepper for customers | `stage` |
| `TraceTimelineComponent` | Vertical timeline of nodes (section 7) | `events` |
| `TraceNodeCardComponent` | One node with status, duration, expandable payload | `node` |
| `CriticScoreComponent` | Score gauge / bar with pass threshold marker | `score`, `threshold` |
| `StatusBadgeComponent` | Ticket/escalation status chip | `status` |
| `CategoryChipComponent` | Billing/tech/general chip with colour + icon | `category` |
| `ConfidenceMeterComponent` | Small bar for classifier confidence | `value` |
| `RefundApprovalCardComponent` | Pending refund summary with actions | `refund` |
| `FileDropzoneComponent` | Drag-and-drop uploader with validation | `accept`, `maxSizeMb` |
| `ConfirmDialogComponent` | Reusable confirmation dialog | `title`, `message`, `danger` |
| `EmptyStateComponent` | Illustration + message + CTA | `icon`, `title`, `action` |
| `SkeletonComponent` | Loading placeholders | `lines`, `shape` |
| `PageHeaderComponent` | Title, breadcrumbs, actions slot | |
| `JsonViewerComponent` | Collapsible JSON in mono font | `data` |
| `ToastService` | Success/error snackbars | |

All presentational components are `OnPush` and have a Storybook-style demo page (optional) or are exercised via unit tests.

---

## 7. Agent Trace Panel (Signature Feature)

### 7.1 Purpose

Make the agent graph visible: which node ran, how long it took, what it decided, and why the answer was accepted, retried or escalated.

### 7.2 Event-to-UI mapping

| SSE event | UI effect |
|-----------|-----------|
| `run_started` | Clear panel, show first pending node |
| `node_started` | Add node card with spinner and node colour |
| `node_completed` | Stop spinner, show duration and one-line summary |
| `classified` | Show category chip + confidence meter + sentiment |
| `retrieved` | Show list of source cards (title, score), expandable |
| `draft` | Show collapsible "Draft (loop n)" with text; **trace only** |
| `critic_scored` | Show `CriticScoreComponent` with threshold line, unsupported claims and feedback list |
| `retrying` | Show a curved "↻ retry (loop n)" connector and increment loop badge |
| `escalated` | Show red escalation card with reason; chat shows handoff message |
| `token` | Append to the pending assistant message (chat, not trace) |
| `final` | Mark finalize node done, attach citations to message |
| `error` | Show error card in trace and toast in chat |
| `done` | Close stream, set run state to `done` |

### 7.3 Visual rules

- Each node card has a coloured left border (node colour) and icon.
- Running node: subtle pulsing dot (disabled with reduced motion).
- Loops are grouped: `critic` + retried agent appear under a "Loop 1 / Loop 2" bracket so the retry story is easy to follow.
- The critic card uses a horizontal bar with a marker at 0.8; bar turns green above threshold, amber below.
- Payloads (JSON) are collapsed by default and shown in a mono font.
- Trace persists after the run; reopening a ticket loads it from `GET /tickets/{id}/trace` using the same components.

### 7.4 Customer vs agent depth

| Mode | Shown |
|------|-------|
| Simple (customer default) | Stage indicator + sources under the answer |
| Detailed (agent/admin default, optional for customer) | Full trace timeline with payloads |

---

## 8. State Management

Signals-based stores, provided at feature level (not global) unless shared.

### 8.1 Stores

| Store | Scope | Holds |
|-------|-------|-------|
| `AuthStore` | root | `user`, `accessToken`, `refreshToken`, `isAuthenticated`, `role` |
| `ThemeStore` | root | `mode` (`system`/`light`/`dark`), resolved theme |
| `ChatStore` | chat feature | messages, active ticket, run state, trace nodes, stage |
| `TicketListStore` | tickets feature | filters, pagination, items, loading |
| `EscalationStore` | agent feature | queue, filters, selected escalation |
| `KbStore` | admin feature | documents, upload progress, search results |
| `EvalStore` | admin feature | runs, selected runs for comparison |
| `UiStore` | root | sidebar state, toasts |

### 8.2 ChatStore shape

```ts
export type RunState = 'idle' | 'running' | 'escalated' | 'done' | 'error';

export interface TraceNode {
  seq: number;
  node: NodeName;
  status: 'running' | 'done' | 'failed';
  durationMs?: number;
  summary?: string;
  loop?: number;
  payload?: unknown;
}

export class ChatStore {
  readonly messages = signal<ChatMessage[]>([]);
  readonly ticketId = signal<string | null>(null);
  readonly runState = signal<RunState>('idle');
  readonly trace = signal<TraceNode[]>([]);
  readonly stage = computed(() => deriveStage(this.trace(), this.runState()));
  readonly canSend = computed(() => this.runState() !== 'running');
}
```

### 8.3 Event reducer

A single pure function applies each `RunEvent` to the store state, which keeps the streaming logic testable:

```ts
export function applyEvent(state: ChatState, ev: RunEvent): ChatState {
  switch (ev.type) {
    case 'run_started':    return { ...state, runState: 'running', trace: [] };
    case 'node_started':   return addNode(state, ev.data);
    case 'node_completed': return completeNode(state, ev.data);
    case 'critic_scored':  return attachCritic(state, ev.data);
    case 'token':          return appendToken(state, ev.data.text);
    case 'final':          return finalizeMessage(state, ev.data);
    case 'escalated':      return { ...state, runState: 'escalated', ...addHandoff(state, ev.data) };
    case 'error':          return { ...state, runState: 'error', error: ev.data };
    case 'done':           return state.runState === 'running' ? { ...state, runState: 'done' } : state;
    default:               return state;
  }
}
```

---

## 9. Services and API Mapping

| Service | Endpoints used |
|---------|----------------|
| `AuthService` | `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me` |
| `TicketService` | `POST /tickets`, `GET /tickets`, `GET /tickets/{id}`, `GET /tickets/{id}/messages`, `POST /tickets/{id}/messages`, `GET /tickets/{id}/trace`, `POST /tickets/{id}/feedback`, `POST /tickets/{id}/close` |
| `RunStreamService` | `GET /tickets/{id}/runs/{run_id}/stream` (SSE) |
| `EscalationService` | `GET /escalations`, `GET /escalations/{id}`, `POST /escalations/{id}/claim`, `/reply`, `/approve-refund`, `/resolve` |
| `OrderService` | `GET /orders/{order_id}`, `GET /customers/{id}/orders` (agent view) |
| `KbService` | `POST /kb/documents`, `GET /kb/documents`, `GET /kb/documents/{id}`, `DELETE /kb/documents/{id}`, `POST /kb/documents/{id}/reindex`, `POST /kb/reindex`, `POST /kb/search` |
| `EvalService` | `GET/POST /eval/datasets`, `POST /eval/runs`, `GET /eval/runs`, `GET /eval/runs/{id}` |
| `AnalyticsService` | `GET /analytics/summary`, `GET /analytics/usage` |
| `HealthService` | `GET /health/ready` (optional status dot in the footer) |

Base URL comes from `environment.apiBase` (`/api/v1`; proxied to `http://localhost:8000` in dev).

---

## 10. TypeScript Models

```ts
export type Role = 'customer' | 'agent' | 'admin';
export type Category = 'billing' | 'tech' | 'general';
export type NodeName =
  | 'guard' | 'classify' | 'billing_agent' | 'tech_agent'
  | 'general_agent' | 'critic' | 'escalate' | 'finalize';
export type TicketStatus = 'open' | 'answered' | 'escalated' | 'resolved' | 'closed';

export interface User { id: string; email: string; role: Role; }

export interface Citation { n: number; chunkId: string; title: string; }

export interface ChatMessage {
  id: string;
  role: 'customer' | 'assistant' | 'human_agent' | 'system';
  content: string;
  citations?: Citation[];
  createdAt: string;
  streaming?: boolean;
}

export interface TicketSummary {
  id: string; subject: string; category?: Category; status: TicketStatus;
  lastCriticScore?: number; updatedAt: string;
}

export interface Page<T> { items: T[]; page: number; pageSize: number; total: number; }

export type RunEvent =
  | { type: 'run_started'; data: { runId: string } }
  | { type: 'node_started'; data: { node: NodeName; seq: number } }
  | { type: 'node_completed'; data: { node: NodeName; seq: number; durationMs: number; summary?: string } }
  | { type: 'classified'; data: { category: Category; confidence: number; sentiment: string } }
  | { type: 'retrieved'; data: { chunks: { chunkId: string; title: string; score: number }[] } }
  | { type: 'draft'; data: { loop: number; text: string } }
  | { type: 'critic_scored'; data: { loop: number; score: number; unsupportedClaims: string[]; feedback: string[] } }
  | { type: 'retrying'; data: { loop: number; reason: string } }
  | { type: 'escalated'; data: { reason: string; escalationId: string } }
  | { type: 'token'; data: { text: string } }
  | { type: 'final'; data: { messageId: string; answer: string; citations: Citation[] } }
  | { type: 'error'; data: { code: string; message: string } }
  | { type: 'done'; data: Record<string, never> };

export interface ApiError { error: { code: string; message: string; details?: unknown; request_id: string } }
```

> The backend sends snake_case JSON. Convert at the service boundary (a small mapper or `camelCase` interceptor) so components only see camelCase.

---

## 11. Routing, Guards and Interceptors

### 11.1 Route table

```ts
export const routes: Routes = [
  { path: 'login', loadComponent: () => import('./features/auth/login.component') },
  {
    path: '',
    component: ShellComponent,
    canActivate: [authGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'home' },     // role-based redirect resolver
      { path: 'chat', canActivate: [roleGuard(['customer'])], loadComponent: () => import('./features/chat/chat-page.component') },
      { path: 'tickets', loadComponent: () => import('./features/tickets/ticket-list.component') },
      { path: 'tickets/:id', loadComponent: () => import('./features/tickets/ticket-detail.component') },
      { path: 'agent/escalations', canActivate: [roleGuard(['agent', 'admin'])], loadComponent: () => import('./features/agent/escalation-queue.component') },
      { path: 'agent/escalations/:id', canActivate: [roleGuard(['agent', 'admin'])], loadComponent: () => import('./features/agent/escalation-detail.component') },
      { path: 'admin/kb', canActivate: [roleGuard(['admin'])], loadComponent: () => import('./features/admin/kb/kb-manager.component') },
      { path: 'admin/eval', canActivate: [roleGuard(['admin'])], loadComponent: () => import('./features/admin/eval/eval-dashboard.component') },
      { path: 'admin/analytics', canActivate: [roleGuard(['admin'])], loadComponent: () => import('./features/admin/analytics/analytics.component') },
    ],
  },
  { path: '403', loadComponent: () => import('./shared/pages/forbidden.component') },
  { path: '**', loadComponent: () => import('./shared/pages/not-found.component') },
];
```

### 11.2 Guards

- `authGuard`: redirects to `/login` (with `returnUrl`) when unauthenticated.
- `roleGuard(roles)`: redirects to `/403` if the role is not allowed.
- Guards are a UX layer only; the backend enforces access.

### 11.3 Interceptors (functional)

| Interceptor | Behaviour |
|-------------|-----------|
| `authInterceptor` | Adds `Authorization: Bearer <token>`; on 401 tries one refresh via `/auth/refresh`, retries the request, otherwise logs out |
| `errorInterceptor` | Maps `ApiError` to a typed error, shows a toast for 5xx/network errors, preserves `request_id` |
| `caseInterceptor` | Converts snake_case ↔ camelCase |
| `loadingInterceptor` (optional) | Global progress bar for long requests |

---

## 12. SSE Streaming Client

`EventSource` cannot set headers, so use `fetch` streaming. Note that `fetch-event-source` bypasses `HttpClient` interceptors: refresh the token **before** opening a stream and handle 401 manually.

```ts
@Injectable({ providedIn: 'root' })
export class RunStreamService {
  private auth = inject(AuthService);

  stream(ticketId: string, runId: string): Observable<RunEvent> {
    return new Observable<RunEvent>((sub) => {
      const ctrl = new AbortController();
      this.auth.ensureFreshToken().then(() =>
        fetchEventSource(`${environment.apiBase}/tickets/${ticketId}/runs/${runId}/stream`, {
          headers: { Authorization: `Bearer ${this.auth.accessToken()}` },
          signal: ctrl.signal,
          openWhenHidden: true,                       // keep streaming in background tabs
          async onopen(res) {
            if (!res.ok) throw new StreamError(res.status);
          },
          onmessage: (ev) => {
            if (!ev.event) return;                    // keep-alive comments
            const data = JSON.parse(ev.data);
            sub.next({ type: ev.event, data } as RunEvent);
            if (ev.event === 'done') sub.complete();
          },
          onerror: (err) => { sub.error(err); throw err; },   // stop auto-retry
        }),
      );
      return () => ctrl.abort();                      // unsubscribe = cancel stream
    });
  }
}
```

### Behaviour rules

- Unsubscribing (navigating away) aborts the stream; the run continues on the server and its trace can be reloaded later from `GET /tickets/{id}/trace`.
- On network drop mid-run, show a "Connection lost" banner and offer **Reload result** (fetch messages + trace) instead of auto-retrying the stream.
- Ignore unknown event types so the backend can add events without breaking the UI.
- Development helper: a `MockRunStreamService` that replays a recorded event sequence, so the whole UI can be built before the backend graph is ready.

---

## 13. Error Handling and UX States

| Situation | UI response |
|-----------|-------------|
| Form validation error | Inline message under the field, focus the first invalid field |
| 401 | Silent refresh once; otherwise redirect to login with "Session expired" |
| 403 | `/403` page or toast "You don't have access" |
| 404 | Not-found page for routes; inline "Ticket not found" for resources |
| 409 | Toast with explanation (e.g. "Already claimed by another agent") and list refresh |
| 422 | Map field errors to the form |
| 429 | Toast "Too many requests, try again in a moment", disable send briefly |
| 502 / Engine down | Chat shows "The assistant is temporarily unavailable" with retry; trace shows the failing node |
| Network offline | Persistent banner, queued actions disabled |
| Stream error | Error card in trace, **Retry** button in chat |
| Upload failure | Row shows failed state with reason and retry |

Every error message includes a short, human sentence and, for 5xx, a copyable `request_id` in a "Details" expander.

Loading rules: skeletons for lists and detail pages, spinner only inside buttons, never block the whole screen.

---

## 14. Accessibility and Responsiveness

- Target **WCAG 2.1 AA**.
- Full keyboard navigation; visible focus ring (2 px `--primary` outline with offset).
- Chat message list uses `role="log"` with `aria-live="polite"`; the stage indicator uses `aria-live="polite"` and the trace timeline is a labelled list.
- Colour is never the only signal: statuses and nodes also have icons and text labels.
- Dialogs trap focus and return it to the trigger on close.
- Respect `prefers-reduced-motion` and `prefers-color-scheme`.
- Touch targets at least 40 × 40 px on mobile.
- Charts have table fallbacks; images and icons have `aria-label` or are `aria-hidden` when decorative.
- Test with keyboard only and a screen reader at least once per major screen (Phase F8).

---

## 15. Performance Guidelines

- `ChangeDetectionStrategy.OnPush` and Signals; avoid function calls in templates.
- Lazy-load all feature routes; keep the initial bundle small (target under ~300 KB gzipped for the shell).
- `@for ... track item.id` everywhere.
- Virtual scrolling (`cdk-virtual-scroll`) for long message histories and the eval case table.
- Batch trace updates: apply SSE events through the reducer and render at most once per animation frame for `token` events.
- Debounce search inputs (300 ms) and cancel in-flight requests with `switchMap`.
- Lazy-load chart libraries only on analytics/eval routes.
- Use `NgOptimizedImage` for any raster images; prefer inline SVG.

---

## 16. Testing Strategy

| Level | What | Tooling |
|-------|------|---------|
| Unit | Reducer (`applyEvent`), stage derivation, mappers, guards, interceptors, pipes | Jasmine/Karma or Jest |
| Component | `MessageBubble`, `TraceTimeline`, `CriticScore`, `RefundApprovalCard`, forms | Angular TestBed |
| Service | HTTP services with `HttpTestingController`; `RunStreamService` with a mocked stream | |
| Store | Signals stores with fake services | |
| E2E (optional) | Login → ask question → see trace → escalate → agent reply | Playwright |
| Visual (optional) | Light/dark snapshots of key screens | Playwright screenshots |
| Accessibility | Automated axe checks on main routes | `axe-core` / Playwright |

**Must-have tests:** the event reducer for every event type, loop/retry rendering, hidden-draft rule (no `draft` text in chat bubbles), role-based nav visibility, 401 refresh flow, and SSE abort on destroy.

---

## 17. Folder Structure

```
frontend/
├── proxy.conf.json                # /api -> http://localhost:8000
├── src/
│   ├── styles/
│   │   ├── _tokens.scss           # CSS custom properties (light/dark)
│   │   ├── _theme.scss            # Angular Material theme mapping
│   │   ├── _typography.scss
│   │   └── styles.scss
│   ├── assets/                    # logo, illustrations (SVG)
│   ├── environments/              # environment.ts
│   └── app/
│       ├── app.config.ts          # providers: router, http, interceptors, animations
│       ├── app.routes.ts
│       ├── core/
│       │   ├── auth/              # auth.service, auth.store, guards, interceptors
│       │   ├── http/              # error, case-converter interceptors, api-error types
│       │   ├── theme/             # theme.store, theme-toggle
│       │   └── layout/            # shell, sidebar, topbar
│       ├── shared/
│       │   ├── components/        # message-bubble, citation-chip, source-card, status-badge,
│       │   │                      # category-chip, critic-score, file-dropzone, confirm-dialog, ...
│       │   ├── models/            # TypeScript interfaces (section 10)
│       │   ├── pipes/             # relative-time, score-format
│       │   └── pages/             # forbidden, not-found
│       └── features/
│           ├── auth/              # login
│           ├── chat/              # chat-page, chat.store, run-stream.service, trace-panel/,
│           │                      # stage-indicator
│           ├── tickets/           # ticket-list, ticket-detail, ticket.service
│           ├── agent/             # escalation-queue, escalation-detail, escalation.service
│           └── admin/
│               ├── kb/            # kb-manager, kb.service
│               ├── eval/          # eval-dashboard, eval.service
│               └── analytics/     # analytics, analytics.service
└── package.json
```

---

## 18. Environment and Local Setup

```ts
// src/environments/environment.ts
export const environment = {
  production: false,
  apiBase: '/api/v1',          // proxied to the backend in dev
  features: {
    showTraceToCustomers: false,   // simple stage indicator by default
    escalationPollMs: 15000,
    useMockStream: false,          // true = replay recorded events (no backend needed)
  },
};
```

```json
// proxy.conf.json
{
  "/api": { "target": "http://localhost:8000", "secure": false, "changeOrigin": true }
}
```

```bash
cd frontend
npm install
ng serve --proxy-config proxy.conf.json      # http://localhost:4200
ng test                                       # unit tests
ng build                                      # production build check (no deployment needed)
```

Backend must be running on `http://localhost:8000` (see the backend documentation, section 18). To build the UI without the backend or the Generative Engine, set `useMockStream: true`.

---

## 19. Frontend Implementation Roadmap

| Phase | Scope | Deliverable | Est. |
|-------|-------|-------------|------|
| F0 | Angular project, Material, design tokens, light/dark theme, fonts, app shell (sidebar + top bar), routing skeleton | Themed empty shell with working theme toggle | 2 days |
| F1 | Auth: login page, `AuthService`, interceptors, guards, role-based nav | Login as each role, correct nav and redirects | 2 days |
| F2 | Chat page without streaming: `TicketService`, message list, input, markdown, citations, empty/error states | Send a message, receive a full answer | 3 days |
| F3 | SSE client, `ChatStore` + reducer, stage indicator, **trace panel**, critic score, retry/escalation visuals, `MockRunStreamService` | Live trace with loops and escalation | 5 days |
| F4 | Tickets list (filters, pagination) and ticket detail with historical trace | Browse and reopen tickets | 3 days |
| F5 | Escalation queue + detail, refund approval dialog, reply and resolve | Full human handoff flow | 4 days |
| F6 | KB manager: upload, status polling, delete, reindex, search test | Admin can manage and test the KB | 3 days |
| F7 | Eval dashboard (runs, comparison, per-case) and analytics charts | Critic ON vs OFF visible in UI | 4 days |
| F8 | Polish: accessibility pass, responsive pass, animations, error states, unit and component tests, demo GIF | Portfolio-ready UI | 3-4 days |

**Total:** about 4-5 weeks part-time, overlapping with backend phases. Build F0-F3 first against the mock stream; connect to the real backend as soon as the graph streams events.

---

## 20. UX Acceptance Checklist and Demo Script

### Acceptance checklist

- [ ] Light and dark themes both look correct on every screen; no flash on load.
- [ ] Customer, agent and admin each see only their navigation and routes.
- [ ] Chat streams the final answer only; rejected drafts never appear in the bubble.
- [ ] Trace panel shows nodes, durations, retrieved sources, critic scores, retries and escalation correctly.
- [ ] Citations are clickable and point to the right source.
- [ ] Refund approval requires confirmation and shows amount, order and customer.
- [ ] Every list has loading, empty and error states.
- [ ] Keyboard-only use works on login, chat, queue and KB upload.
- [ ] Layout works at 375 px, 768 px and 1440 px widths.
- [ ] Unit tests pass for the reducer, guards and interceptors.

### Demo script (2-3 minutes, for the README video)

1. **Login as customer**, toggle dark mode.
2. Ask a **tech question**: show stage indicator, streamed answer with citations, expand the trace to show retrieval and critic score.
3. Ask a **billing question** with a duplicate charge: show the tool step and a critic **retry loop** (score 0.67 → 0.91).
4. Ask something **outside the KB**: show escalation handoff message.
5. **Switch to agent**: claim the escalation, review context, approve a refund, reply and resolve.
6. **Switch to admin**: upload a new document, run the search test, open the eval comparison (critic ON vs OFF) and the analytics page.
