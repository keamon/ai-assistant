# SSIM Employee Digital Assistant — Product Requirements Document (PRD)

> Status: Living document · Version 0.8 · Date: 2026-07-17
> Chain: [`ideas.md`](ideas.md) → **this PRD** → [`spec.md`](spec.md) → [`implementation.md`](implementation.md) → code · Conventions: [`CLAUDE.md`](CLAUDE.md)
> Owner: SSIM AI Platform team
> ⚠️ Keep in sync with code (see CLAUDE.md): user-facing behavior / scope / requirement changes land here.

---

## 1. Overview

State Street Investment Management (SSIM, ~$4.1T AUM, institutional-only) has built a set of
standalone AI agents on Google's ADK + Vertex AI. This product unifies them into a **single
employee digital assistant**: one web surface where an SSIM employee gets help across their
day — morning briefing, meeting preparation and scheduling, room booking, project tasks,
client/CRM work, RFPs, and sales support — backed by a concierge agent that routes to
specialists, with structured outputs rendered as rich UI (not raw chat text).

This PRD defines the committed product: what is delivered in v1, what is on the roadmap, the
requirements behind each capability, and how success is measured.

## 2. Problem & opportunity

- **Fragmentation.** Capabilities live as five separate agents with no shared surface; users
  must know which tool to open and self-route. There is no connective tissue between them.
- **Manual glue work.** Scheduling, room selection, meeting prep, task creation (Jira), and
  CRM logging (Salesforce) are manual and disconnected from the assistant.
- **Underserved journeys.** The morning briefing is shallow on "what should I do next"
  (e.g., meetings that ought to be scheduled), and prep is a separate tool rather than an
  in-context expansion of a meeting.
- **Opportunity.** A single assistant that (a) surfaces the day, (b) acts (books rooms,
  schedules meetings, creates tasks, logs CRM), and (c) shows the effects live in familiar
  board UIs (Jira/Salesforce) makes the suite feel like one product and removes busywork.

## 3. Goals & non-goals

**Goals (v1)**
- One tabbed web app fronting the assistant, with mock Jira and mock Salesforce boards that
  react to assistant actions.
- A concierge chat that can brief, prep, schedule/book rooms, create Jira tasks, and log
  Salesforce activity.
- A new meeting-room booking capability that auto-assigns rooms by capacity + attendee seat
  proximity.
- Daily Briefing that suggests meetings to schedule and lets any meeting expand into a full
  prep brief.

**Non-goals (v1)**
- Real production integrations with live Gmail/Calendar/Drive/Jira/Salesforce (mock-backed;
  real APIs are a roadmap item). Per-employee OAuth identity is out of scope for v1.
- Compliance/gating, investment research, and Tier-2/3 agents (roadmap).
- Fine-grained authz, audit-grade write trails, and multi-tenant isolation (roadmap).

## 4. Target users (personas)

| Persona | Needs the assistant for |
|---|---|
| Portfolio Manager / Strategist | Market/portfolio context, meeting prep, research (roadmap) |
| Relationship Manager | Client meeting prep, follow-ups, CRM updates, scheduling |
| BD / Sales | Proposals, competitive intel, CRM logging, RFP support |
| Project / Ops lead | Workload analysis, creating & tracking Jira tasks |
| All employees | Daily briefing, scheduling, room booking; (roadmap) HR/IT/policy Q&A |

## 5. Scope

### 5.1 Delivered in v1 (this build)

- **Concierge web app**: a single-page **AI Assistant** (chat + Daily Briefing dashboard),
  plus standalone **Jira** and **Salesforce** pages opened in a new tab. No separate Meeting
  Rooms view — room data (inventory, seat directory, bookings) is backend state the concierge
  agent draws on (via `list_available_rooms`/`assign_meeting_room`/`book_room`) and surfaces
  through the Schedule widget, not a UI of its own.
- **Meeting Room Booking agent** (new).
- **Daily Briefing** upgrades: suggested-meetings-to-schedule, one-click scheduling with
  auto room assignment, and **Meeting Prep folded in** as an expandable per-meeting view.
- **Assistant write-backs** that update the mock **Jira** and **Salesforce** boards live.
- Existing agents remain independently deployable (Project Mgmt, RFP, Sales, Meeting Prep).

### 5.2 Roadmap (not in v1)

- **Tier 1:** Compliance & Regulatory Assistant (gates RFP/Sales drafts); Post-Meeting /
  Follow-up agent (writes to CRM/Jira/next-day briefing); Investment Research / Market
  Intelligence.
- **Tier 2:** Client Reporting / review-pack generator; Knowledge / Policy (HR/IT) Q&A.
- **Tier 3:** IT helpdesk, Expense & Travel, New-hire onboarding.
- **Platform:** real data integrations, per-employee auth, shared data/service layer for
  CRM/Jira, deployment to Agent Engine + Cloud Run, observability & eval in CI.

## 6. Functional requirements

Requirements use **P0** (must, v1), **P1** (should, near-term), **P2** (roadmap).

### 6.1 Concierge assistant (chat)
- **FR-A1 (P0)** The user can converse with a single assistant that routes intent to the
  right capability (briefing, prep, rooms/scheduling, Jira, Salesforce).
- **FR-A2 (P0)** For write actions (schedule, book, create tasks, log CRM), the assistant
  confirms ambiguous specifics, then acts, and states plainly what changed.
- **FR-A3 (P0)** The assistant never fabricates client data; unavailable data is flagged.
- **FR-A4 (P1)** Multi-step chains (e.g., summarize a meeting → create Jira tasks → log a
  Salesforce activity) execute in one turn.
- **FR-A5 (P0)** Chat replies render basic markdown emphasis — `**bold**` displays as bold
  text — instead of showing the literal formatting characters; same rule applies to the
  auto-generated daily briefing narrative (FR-B1).

### 6.2 Daily Briefing (home)
- **FR-B1 (P0)** The briefing is **generated and displayed automatically on load** — an
  auto-generated narrative plus today's schedule, priority emails, starred follow-ups, and
  market/portfolio context. No prompt required.
- **FR-B2 (P0)** Surface **suggested meetings to schedule** derived from signals (emails,
  action items) with rationale, attendees, priority, and suggested date.
- **FR-B3 (P0)** The **Schedule** action opens a **confirmation widget** pre-filled with
  title, attendees, description, date/time and a **suggested room**, plus a **dropdown of
  every room free in that window** so the user can override the auto-pick; the user
  reviews/edits and clicks **Confirm** to create the meeting and book the chosen room.
- **FR-B4 (P0)** Each meeting can **expand** into a full prep brief — objective, suggested
  agenda, **talking points**, anticipated questions (rendered as readable Q/A, never raw
  JSON), attendees, client profile, recent comms, and relevant documents (Meeting Prep
  folded in).
- **FR-B5 (P0)** Each **referenced document is clickable** and opens its content in a **popup**.
- **FR-B6 (P0)** A confirmed meeting is always visible immediately after scheduling:
  same-day meetings appear under **Today's schedule**; meetings scheduled for another date
  appear under a separate **Upcoming meetings** list.

### 6.3 Meeting Room Booking
> No standalone UI — this is backend/agent capability, surfaced only through the Schedule
> widget's room dropdown (FR-B3) and chat.
- **FR-R1 (P0)** List rooms free for a window (capacity/building filters).
- **FR-R2 (P0)** Look up each attendee's seat location (building/floor/seat).
- **FR-R3 (P0)** Auto-assign the best-fit room: sufficient capacity, free in the window,
  minimizing attendee travel (building then floor), tightest fit; prefer video-conf rooms
  when anyone is remote/external. Return a human-readable rationale.
- **FR-R4 (P0)** Book a room (write) after confirmation; never double-book. Booking a room
  for an **existing** meeting (vs. scheduling a new one) updates that meeting's displayed
  location immediately, including in an already-open meeting card — not just the booking
  ledger.

### 6.4 Jira (mock board)
- **FR-J1 (P0)** Render Jira as a **separate, realistic full page** (own product chrome —
  project sidebar, board columns, issue-type/priority icons, assignees, points), opened in a
  **new browser tab** — not an in-app tab.
- **FR-J2 (P0)** The assistant can create tasks; new issues appear on the board (highlighted).
- **FR-J3 (P1)** Workload analysis and project-plan export (existing Project Mgmt agent).

### 6.5 Salesforce (mock CRM)
- **FR-S1 (P0)** Render Salesforce as a **separate, realistic Lightning-style full page**
  (global header with a realistic cloud logomark in Salesforce's brand blue — icon only, no
  wordmark text — object nav, list views, activity timeline), opened in a **new browser tab**.
- **FR-S2 (P0)** The assistant can log activities and update opportunities; the CRM updates
  live (highlighted).

### 6.6 Live sync (cross-tab)
- **FR-L1 (P0)** An assistant action or Schedule click is reflected in the relevant tab
  within a few seconds (poll/refetch); newly created items are visually flagged.

### 6.7 Existing specialist agents (retained)
- **FR-X1 (P1)** Project Mgmt, RFP, Sales, and Meeting Prep remain independently usable and
  deployable; their capabilities are progressively surfaced in the concierge.

## 7. UX & surfaces

- **Surface:** custom web app (React) — chosen for maximum UX control.
- **Entry pattern:** hybrid concierge — Daily Briefing as the home dashboard; persistent
  concierge chat as the primary action surface; tabs for discovery of specialized boards.
- **Rendering principle:** structured outputs (cards, badges, kanban, tables, timelines),
  not raw markdown. Meeting = expandable card; suggestion = card with a Schedule button;
  Jira = kanban; Salesforce = tables + timeline.
- **Feedback:** writes produce a plain-language confirmation in chat and a visual change
  (with a brief "new" highlight) in the target tab.
- **Reset:** a "Reset demo" control restores seed state.

## 8. Non-functional requirements

- **Performance:** dashboard/board reads < ~300 ms locally; chat turn latency bounded by the
  model. Read endpoints must work even if the model backend is unavailable.
- **Reliability:** transient model errors degrade gracefully (friendly retry, no broken UI).
- **Consistency:** domain mock data has a single source of truth so the UI never drifts from
  the agents.
- **Portability:** local-first (FastAPI + Vite), with a defined path to Agent Engine +
  Cloud Run.
- **Maintainability:** each agent self-contained and independently deployable; shared
  conventions (prompts use `[Variable]`, JSON-string tools with mock fallback).
- **Security/compliance (v1 posture):** mock data only; no PII beyond synthetic demo data;
  write actions confirmed. Real-data auth is a roadmap gate.

## 9. Success metrics

- **Adoption:** weekly active employees; % of briefings opened; chat turns/user/day.
- **Action rate:** # rooms booked, meetings scheduled, Jira tasks created, CRM activities
  logged via the assistant (the core value events).
- **Time saved:** self-reported minutes saved on scheduling/prep/CRM logging.
- **Quality:** assistant task-success rate (eval), room-assignment acceptance rate,
  write-action confirmation accuracy, hallucination rate ≈ 0 on client data.
- **Demo bar (v1):** a user can, in one session, brief → expand prep → schedule a suggested
  meeting (room auto-booked) → create Jira tasks → log Salesforce activity, and see all
  boards update.

## 10. Dependencies & assumptions

- Google ADK + Vertex AI; GCP project `logical-vim-478515-b1`.
- Model: `gemini-3.5-flash` served from the **`us`** multi-region (see spec §7 and memory —
  `gemini-2.0-flash-001` is retired/404 for this project).
- Local dev uses Application Default Credentials; v1 operates on mock data with graceful
  fallback to real Google APIs where wired.

## 11. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Model availability/quota (429/404 by region) | Chat fails | Pin `gemini-3.5-flash`@`us`; graceful retry; read endpoints model-independent |
| Mock↔real data drift | Demo/real mismatch | Single source of truth (`daily_briefing/app/mock_data.py`); define data contracts (spec §6) |
| Write-action safety | Wrong writes to CRM/Jira | Confirm-before-write; roadmap: audit trail + authz |
| Per-agent duplication (room logic) | Maintenance cost | Accepted for v1 (deployability > DRY); roadmap: shared service layer |
| Auth/identity for real data | Blocks production | Roadmap: per-employee OAuth + scoped access |

## 12. Open questions

- v1 agent set for the concierge: confirmed **briefing + rooms/scheduling + Jira + Salesforce**;
  when do Project Mgmt / Sales / RFP / Compliance / Research join?
- Real vs mock integration order (which system goes real first)?
- Shared CRM/Jira service layer vs per-agent mocks — when to invest?
- Identity model for scoping Gmail/Calendar/Drive per employee.

## 13. Roadmap / phasing

- **Phase 1 (done):** concierge webapp; meeting_room agent; daily briefing upgrades; live
  mock Jira/Salesforce.
- **Phase 2:** deploy (Agent Engine — pending approval; **Cloud Run done**, see `spec.md` §11);
  Compliance + Post-Meeting agents; surface Project Mgmt & Sales journeys in the concierge.
- **Phase 3:** Investment Research; real data integrations + per-employee auth; shared
  CRM/Jira service; eval-in-CI + observability dashboards.
- **Phase 4:** Tier 2/3 employee agents (Knowledge/Policy, IT, Expense, Onboarding).
