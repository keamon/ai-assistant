# SSIM Employee Digital Assistant — Technical Specification (SPEC)

> Status: Living document · Version 0.8 · Date: 2026-07-17
> Chain: [`ideas.md`](ideas.md) → [`prd.md`](prd.md) → **this spec** → [`implementation.md`](implementation.md) → code · Conventions: [`CLAUDE.md`](CLAUDE.md)
> Scope: the whole solution — agent layer (6 ADK agents) + concierge web app (backend +
> frontend) + shared mock data/state, plus the deployment path.
> ⚠️ Keep in sync with code (see CLAUDE.md): agent / tool / endpoint / data-contract / model / architecture changes land here.

---

## 1. Architecture overview

Two layers:

1. **Agent layer** — independent, deployable ADK agents (one folder each). Each is a
   self-contained Vertex AI Agent Engine app with mock-data fallback.
2. **Experience layer** — `webapp/`: a FastAPI backend running a single ADK **concierge**
   agent whose tools read/write a **shared in-process store**, and a React/Vite/TS frontend
   (assistant view + standalone Jira/Salesforce pages). Because the store is shared, an
   assistant action is immediately visible in the Jira / Salesforce views and in the
   assistant's own schedule/room state.

```
                        ┌─────────────────────── Browser (React/Vite/TS) ───────────────────────┐
                        │       Assistant + Briefing        │ Jira board  │ Salesforce CRM       │
                        └───────────▲───────────────────────────────────▲──────────────────────┘
                                    │ POST /api/assistant                │ GET /api/{jira,salesforce,rooms,briefing}
                        ┌───────────┴───────────────────────────────────┴──────────────────────┐
   webapp/backend       │ FastAPI (server/main.py)                                               │
   (local; → Cloud Run) │   ├── ADK Runner → concierge Agent (server/agent.py)                    │
                        │   │        └── tools (server/tools.py) ── read/write ──┐                │
                        │   └── read endpoints ─────────────────────────────────┤                │
                        │                              shared STORE (server/store.py) ◄───────────┤
                        │                              seeded by server/seed.py + logic (logic.py)│
                        └───────────────────────────────────────────────────────────────────────┘
                                    │ imports domain mock (single source of truth)
                        ┌───────────┴───────────────────────────────────────────────────────────┐
   Agent layer          │ daily_briefing · meeting_prep · meeting_room · proj_ma · rfp · sales    │
   (Vertex Agent Engine)│  each: app/agent.py (tools + Agent+App), app/mock_data.py, app_utils/,  │
                        │        agent_engine_app.py, tests/, pyproject.toml                       │
                        └───────────────────────────────────────────────────────────────────────┘
```

## 2. Repository layout

```
ai_assist/
├── ideas.md prd.md spec.md
├── daily_briefing/  meeting_prep/  meeting_room/  proj_ma/  rfp/  sales/   # ADK agents
│   └── app/{agent.py, mock_data.py, agent_engine_app.py, __init__.py, app_utils/}
│       tests/{unit,integration,eval}  pyproject.toml  GEMINI.md  README.md
└── webapp/
    ├── backend/  (pyproject.toml, server/{main,agent,tools,logic,store,seed,__init__}.py)
    └── frontend/ (package.json, vite.config.ts, src/{App,api,types,styles,richText}.tsx/ts,
                   src/components/*, src/tabs/*, src/pages/*, src/styles/*.css,
                   src/hooks/useFreshTracker.ts)
```

## 3. Model & Vertex configuration

- **Model:** `gemini-3.5-flash` (via `google.adk.models.Gemini`, `retry_options=HttpRetryOptions(attempts=3)`).
- **Location:** `GOOGLE_CLOUD_LOCATION="us"` (US multi-region). Empirically: `gemini-3.5-flash`
  404s in `us-central1`/`us-east4`, is 429 at `global`; `gemini-2.0-flash-001` (prior pin)
  404s everywhere for this project. See memory `vertex-gemini-model-availability`.
- **Vertex flags:** `GOOGLE_GENAI_USE_VERTEXAI="True"`, project from `google.auth.default()`
  (`logical-vim-478515-b1`). Applied identically in every agent and in `webapp/backend/server/agent.py`.
- **Prompt convention:** system prompts are Markdown and use `[Variable]` placeholders (never
  `{Variable}`, which ADK treats as session-state lookups).

## 4. Agent layer

### 4.1 Conventions (all agents)
- Tools are plain Python functions returning **JSON strings**, with a `try:` real-Google-API
  path and an `except:` mock fallback tagged `"source": "mock"`.
- Module exposes `root_agent = Agent(...)` and `app = App(root_agent=..., name=...)`;
  `app/__init__.py` re-exports `app`; `agent_engine_app.py` wraps it as `AgentEngineApp(AdkApp)`
  with telemetry + feedback.
- Packaging: `uv` + `pyproject.toml` (`google-adk>=1.15,<2`, aiplatform, api-python-client).

### 4.2 Agent catalog

| Agent (folder) | `Agent` name | Tools | Primary data sources | Output |
|---|---|---|---|---|
| **Daily Briefing** (`daily_briefing`) | `daily_briefing_agent` | `get_todays_calendar_events`, `get_recent_emails`, `get_starred_emails`, `get_market_context`, `suggest_meetings_to_schedule`, `get_meeting_prep`, `schedule_meeting`, + folded prep: `search_emails_by_attendees`, `search_drive_documents`, `get_drive_document_content`, `get_customer_profile` | Gmail, Calendar, market context; Drive + CRM profiles (folded); rooms/seats (for scheduling) | Morning briefing; per-meeting prep; scheduled event + room booking |
| **Meeting Prep** (`meeting_prep`) | `meeting_prep_agent` | `search_calendar_events`, `get_meeting_by_id`, `search_emails_by_attendees`, `search_drive_documents`, `get_drive_document_content`, `get_customer_profile` | Calendar, Gmail, Drive, customer profiles | Pre-meeting brief |
| **Meeting Room** (`meeting_room`) — NEW | `meeting_room_agent` | `list_available_rooms`, `get_attendee_locations`, `assign_meeting_room`, `book_room` | Room inventory, seat directory, booking ledger (mock) | Auto-assigned room + booking |
| **Project Mgmt** (`proj_ma`) | `project_management_agent` | `list_jira_projects`, `get_jira_project_summary`, `get_jira_issues`, `get_team_members`, `get_workload_analysis`, `create_project_plan_sheet` | Jira (mock), Sheets | Workload analysis; exported plan sheet |
| **RFP Response** (`rfp`) | `rfp_response_agent` | `read_rfp_from_drive`, `read_rfp_from_local_file`, `search_internal_documents`, `get_internal_document_content`, `create_rfp_response_document` | Drive docs | Drafted RFP → Google Doc |
| **Sales Support** (`sales`) | `sales_support_agent` | `get_customer_profile`, `get_crm_interaction_history`, `search_customer_emails`, `search_product_materials`, `search_case_studies`, `get_competitive_intelligence`, `create_proposal_document`, `draft_client_email` | CRM (mock), product library, competitive intel | Proposals, email drafts, competitive briefs |

### 4.3 Meeting-room assignment algorithm (FR-R3)
Given attendees, date, window, optional `min_capacity`:
1. `required = max(min_capacity, #in-person attendees, 1)` (in-person = attendees found in
   the seat directory; others are "remote/external").
2. Candidates = rooms with `capacity ≥ required` **and** free in the window (no booking
   overlap) **and** (`av==True` if any remote attendee). If none, relax the AV constraint.
3. Rank by `(proximity_penalty, capacity−required, av_first)` where
   `proximity_penalty = Σ attendees` [ same building & floor → 0; same building, other floor
   → `1 + 0.1·|Δfloor|`; different building → 10 ]. Lowest wins.
4. Return best + rationale + up to two alternatives. `book_room` writes only after confirmation
   and re-checks availability (no double-book).

### 4.4 Daily Briefing additions (FR-B2/3/4)
- `suggest_meetings_to_schedule()` → curated suggestions grounded in email/portfolio signals,
  filtered to drop any whose subject already matches a calendar event.
- `get_meeting_prep(event_id|title)` → `{meeting, is_customer_meeting, customer_profile,
  recent_emails, related_documents}` (recent_emails exclude the owner to surface the other
  parties' threads).
- `schedule_meeting(title, attendees, date, start, end)` → creates a calendar event and
  auto-assigns/books a room using an embedded copy of the room logic (self-contained so the
  agent stays independently deployable).

## 5. Web app — backend (`webapp/backend`, package `server`)

- **`store.py`** — process-wide `STORE = Store()` holding mutable: `calendar_events`,
  `emails`, `market`, `drive_docs`, `customer_profiles`, `rooms`, `employee_locations`,
  `room_bookings`, `meeting_suggestions`, `jira`, `salesforce`, plus LLM caches
  `briefing_narrative` and `prep_cache[event_id]`. `reset()` re-seeds and clears the caches.
- **`llm.py`** — direct `google.genai` client (Vertex, `us`, `gemini-3.5-flash`):
  `generate_briefing_narrative(summary)` and `generate_meeting_prep(prep) ->
  {objective, agenda[], talking_points[], anticipated_questions[]}`, where each
  `anticipated_questions[]` entry is a normalized `{question, answer}` object (`_normalize_qa`
  coerces model output — dict, or a `"question — answer"` string — into that shape, so the UI
  never renders raw JSON). JSON parsed with a safe fallback; both degrade to composed text if
  Vertex is unavailable. Results cached by callers.
- **`seed.py`** — `build_seed()` loads `daily_briefing/app/mock_data.py` **by file path**
  (single source of truth for SSIM domain data; that module imports only `datetime`), deep-copies
  it, and adds demo-only `jira` and `salesforce` state.
- **`logic.py`** — pure functions over a `Store`: room availability/assignment/booking,
  `briefing_summary`, `suggest_meetings`, `meeting_prep`, `schedule_meeting`,
  `create_jira_tasks`, `log_salesforce_activity`, `update_opportunity`, `get_doc`. Shared by
  tools and read endpoints so chat and UI-button paths behave identically. `book_room`
  (booking a room for an **existing** calendar meeting, as opposed to `schedule_meeting`
  which creates a new one) matches `event_title` against `calendar_events` and writes the
  new room into that event's `location`, so the meeting's prep/briefing views immediately
  reflect the booked room instead of the meeting's original (or empty) location.
- **`tools.py`** — ADK function tools (JSON-string wrappers over `logic` + `STORE`):
  `get_daily_briefing`, `suggest_meetings_to_schedule`, `get_meeting_prep`,
  `list_available_rooms`, `assign_meeting_room`, `book_room`, `schedule_meeting` (optional
  `room_id` to override the auto-pick), `create_jira_tasks`, `log_salesforce_activity`,
  `update_opportunity`. Simple scalar/string args for reliable automatic function-calling
  (e.g., `task_titles` newline/`;`-separated).
- **`agent.py`** — single concierge `Agent` (`ssim_assistant`, `gemini-3.5-flash`@`us`) with
  all tools; system prompt describes each capability and the confirm-before-write rule.
- **`main.py`** — FastAPI, CORS `*`, lazy `Runner` (`InMemorySessionService`, session per
  `session_id`). Endpoints below. Chat runs the sync ADK runner in FastAPI's threadpool;
  empty/failed turns return a friendly retry so the UI never breaks. If `webapp/backend/static/`
  exists (the Cloud Run image only — see §11), mounts the built frontend there and serves it at
  `/`, so `/` returns `index.html` and any other non-`/api` path falls through to it.

### 5.1 HTTP API

| Method | Path | Body → Response |
|---|---|---|
| POST | `/api/assistant` | `{message, session_id?}` → `{reply, session_id}` (tools mutate STORE) |
| GET | `/api/briefing` | → `{date, events, upcoming_events, priority_emails, starred_emails, market, suggestions, narrative}` (`events` = today only, `upcoming_events` = later dates sorted by start; narrative LLM-generated + cached) |
| GET | `/api/prep/{event_id}` | → `MeetingPrep` + `{objective, agenda[], talking_points[], anticipated_questions: {question, answer}[]}` (LLM, cached per event) |
| POST | `/api/assign-room` | `{attendees[], date, start_time, end_time}` → best-fit room **preview (no write)** for the schedule widget |
| POST | `/api/available-rooms` | `{attendees[], date, start_time, end_time}` → `{available_rooms: Room[]}` — every free room, for the schedule widget's room dropdown |
| GET | `/api/doc/{doc_id}` | → `{name, content, webViewLink, category}` (document popup) |
| POST | `/api/schedule` | `{title, attendees[], date, start_time, end_time, room_id?}` → `{scheduled, event, room, rationale, booking}` — `room_id` overrides the auto-pick; `rationale` is `null` when a room is explicitly chosen |
| GET | `/api/calendar` | → `{date, events}` |
| GET | `/api/jira` | → `{project, columns, issues}` |
| GET | `/api/salesforce` | → `{accounts, opportunities, activities}` |
| POST | `/api/reset` | → re-seed store, clear sessions |
| GET | `/api/health` | → `{status, service, date}` |
| GET | `/` | deployed container only: built SPA (`index.html`); no-op locally without a frontend build |

## 6. Web app — frontend (`webapp/frontend`, React + Vite + TS)

- **Routing (`App.tsx`):** a dependency-free **hash router** (listens to `hashchange`).
  Default renders the assistant app; `#/jira` and `#/salesforce` render standalone full-page
  product views (no assistant chrome), opened in a **new browser tab** via header buttons
  (`window.open('#/jira','_blank')`). Hash routing keeps deep links / static hosting simple.
- **Assistant app shell:** topbar (brand, date pill, Open Jira ↗, Open Salesforce ↗, Reset);
  single-page body, no in-app tab nav. Holds `refreshKey`, chat `messages`, `sessionId`;
  `bump()` increments `refreshKey`; a 5s interval also bumps → views refetch (FR-L1).
- **`api.ts`** typed fetch helpers (adds `doc`, `assignRoom`, `availableRooms`); **`types.ts`**
  shared interfaces (Briefing.narrative/upcoming_events; MeetingPrep
  objective/agenda/talking_points/anticipated_questions: `AnticipatedQuestion[]` where
  `AnticipatedQuestion = {question, answer?}`).
- **Views:**
  - `tabs/AssistantTab` — stat tiles; **auto-rendered daily briefing** narrative card
    (`/api/briefing.narrative`, minimal markdown render via shared `richText.tsx`
    `renderRich()` — `**bold**` + line breaks only); today's schedule as expandable rows
    that lazy-fetch enriched `/api/prep/{id}` and show **Objective / Agenda / Talking points /
    Anticipated questions** (rendered as Q/A cards, not raw JSON) + details/profile/comms;
    each row also re-fetches its `/api/prep/{id}` on every `refreshKey` bump (re-fetches if
    open, invalidates its cached prep if closed) so a room booked for that meeting via chat
    (FR-L1) appears in the meeting card's location without needing to collapse/reopen it; an
    **Upcoming meetings** card (dated rows,
    `/api/briefing.upcoming_events`) so meetings scheduled for another date stay visible;
    document entries open `DocModal`; suggestion **Schedule** button opens `ScheduleModal`.
    No dedicated rooms view — room inventory/bookings/seat data lives in `STORE` for the
    concierge agent's tools and the Schedule widget's room dropdown only.
  - `pages/JiraPage` (+ `styles/jira.css`) — realistic Jira board (project sidebar, top bar,
    columns, issue-type/priority icons, assignee avatars, story points); polls `/api/jira`.
  - `pages/SalesforcePage` (+ `styles/salesforce.css`) — Lightning-style (global header with a
    realistic cloud logomark in Salesforce brand blue `var(--sf-blue) = #0176d3` — no wordmark
    text next to it, object nav, list-view tables for Opportunities/Accounts, activity
    timeline); polls `/api/salesforce`.
- **Components:** `Modal` (generic, Esc/overlay close), `ScheduleModal` (pre-filled title/
  attendees/description/date/time; previews the best-fit room via `/api/assign-room` and lists
  every free room via `/api/available-rooms` in a **room dropdown** the user can override
  (defaults to the recommended room); **Confirm** → `/api/schedule` with the chosen `room_id`),
  `DocModal` (fetches `/api/doc/{id}`), `Chat` (concierge; replies also rendered with
  `renderRich()` so `**bold**` from the model displays as bold instead of literal asterisks).
- **Live highlight:** `hooks/useFreshTracker(ids)` flags ids new since the previous fetch
  (initial seed never flashes) so assistant-created bookings/issues/activities briefly highlight.
- **Dev proxy:** `vite.config.ts` proxies `/api` → `http://localhost:8000`.

## 7. Shared data contracts

```
Room            { id, name, building, floor, capacity, equipment[], av }
Booking         { id, room_id, event_title, date, start(ISO), end(ISO), organizer }
EmployeeLocation{ email, name, building, floor, seat }
CalendarEvent   { id, date, title, start, end, location, description, attendees[],
                  meeting_type: "internal"|"customer"|"external", video_link }
Suggestion      { id, title, rationale, suggested_attendees[], suggested_duration_min,
                  priority, suggested_date, source_email_id, meeting_type }
MeetingPrep     { meeting, is_customer_meeting, customer_profile|null,
                  recent_emails[], related_documents[],
                  objective?, agenda?[], talking_points?[], anticipated_questions?: AnticipatedQuestion[] }
AnticipatedQuestion { question, answer? }
JiraIssue       { id, key, project, title, description, assignee, status, priority, created }
JiraBoard       { project, columns: ["To Do","In Progress","Done"], issues[] }
SF.account      { id, name, type, aum, owner, status }
SF.opportunity  { id, account, name, stage, amount, close_date }
SF.activity     { id, account, type, summary, date }
```
`meeting_type` derivation: any attendee domain outside `statestreet.com` /
`chenkeamonwang.altostrat.com` ⇒ `customer`.

## 8. Cross-agent integration map

```
Daily Briefing ──(suggest)──► schedule_meeting ──► Meeting Room (assign+book) ──► Calendar + Rooms
Meeting Prep ──(folded)──► Daily Briefing expandable per-meeting brief
Concierge ──routes──► briefing · prep · rooms/scheduling · Jira(create) · Salesforce(log/update)
(roadmap) Post-Meeting ──► CRM (Sales reads) · Jira (Proj Mgmt reads) · next-day Briefing
(roadmap) Compliance ──gates──► RFP drafts · Sales proposals/emails
(roadmap) Research ──feeds──► Meeting Prep · Sales · RFP · Daily Briefing
```
v1 shares state via the backend `STORE`; the standalone agents remain self-contained
(intentional room-logic duplication). Roadmap: a shared CRM/Jira service layer.

## 9. Security & identity

- **v1:** mock/synthetic data; ADC for Vertex; no per-employee identity; write actions
  confirmed by the assistant. CORS open for local dev.
- **Roadmap:** per-employee OAuth to scope Gmail/Calendar/Drive; authz on write actions;
  audit trail for CRM/Jira writes; secret management for real Jira/Salesforce credentials;
  tighten CORS for deployed origins.

## 10. Testing & evaluation

- **Unit:** room-assignment ranking + conflict detection; `suggest_meetings_to_schedule`
  filtering; `meeting_prep` composition; store mutations (jira/sf/schedule). Replace each
  agent's `tests/unit/test_dummy.py`.
- **Integration:** `tests/integration/test_agent.py` (Runner stream) and
  `test_agent_engine_app.py` per agent; backend: FastAPI TestClient over each endpoint +
  one chat turn asserting a store mutation.
- **Eval:** ADK evalsets per agent (`tests/eval`), rubric-based response quality; add cases
  for scheduling, prep, and write-back correctness. Run via `agents-cli eval`.
- **Frontend:** `npm run build` (tsc + vite) in CI as a smoke gate.

## 11. Deployment

- **Local (v1):** backend `uv run uvicorn server.main:app --port 8000`; frontend
  `npm run dev` (proxy) or `npm run build` + static serve. Requires ADC for the chat.
- **Agent Engine (roadmap):** `agents-cli deploy` per agent folder (`meeting_room` and the
  updated `daily_briefing` first). Existing agents already deployed in `us-central1`
  (reasoning-engine location) — re-deploy after the model change; note the model now serves
  from `us` multi-region.
- **Cloud Run (shipped):** one combined service — root `Dockerfile` (two-stage: `node:20-slim`
  builds `webapp/frontend` → `dist/`, then `python:3.12-slim` + `uv sync`s `webapp/backend`,
  copies the built frontend into `webapp/backend/static/`, and copies
  `daily_briefing/app/mock_data.py` into the image at the same relative path `seed.py` expects).
  FastAPI serves `/api/*` and the built SPA from the same origin (no CORS, no cross-service
  IAM). Deployed as `ssim-assistant` in `us-central1`, `--no-allow-unauthenticated` with
  `roles/run.invoker` granted to `domain:chenkeamonwang.altostrat.com` (matches the IAM pattern
  on sibling Cloud Run services in this project), `--max-instances=1` / `--min-instances=0`
  since `STORE` is still in-process (single-instance demo) — revisit both the instance cap and
  a shared datastore together if multi-instance is ever needed. Credentials: the project's
  default compute service account already has `roles/aiplatform.user`; `agent.py`/`llm.py`
  resolve the project via `google.auth.default()`, so no extra IAM/secrets wiring was needed.

## 12. Observability

- Agent Engine apps ship telemetry to Cloud Trace / BigQuery / Cloud Logging via `app_utils/
  telemetry.py`; `AgentEngineApp.register_feedback` logs structured feedback.
- Backend: standard logging; add request/latency metrics and per-tool call logging when
  deployed. Frontend: capture chat errors surfaced to the user.

## 13. Future technical work

- Shared CRM/Jira **service layer** replacing per-agent mocks; real API integrations behind
  the same tool contracts.
- **Orchestration:** promote the single-agent concierge to agent-as-tool / `sub_agents`
  routing across specialists (Project Mgmt, Sales, RFP, Compliance, Research) as they are
  onboarded.
- **New agents:** Compliance (gating), Post-Meeting (closes the loop into CRM/Jira/briefing),
  Investment Research; then Tier 2/3 employee agents.
- Persist store to a datastore for multi-instance Cloud Run; per-employee auth; eval-in-CI.
