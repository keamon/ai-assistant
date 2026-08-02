# FinTechCo Employee Digital Assistant — Technical Specification (SPEC)

> Status: Living document · Version 1.7 · Date: 2026-08-01
> Chain: [`ideas.md`](ideas.md) → [`prd.md`](prd.md) → **this spec** → [`implementation.md`](implementation.md) → code · Conventions: [`CLAUDE.md`](CLAUDE.md)
> Scope: the whole solution — agent layer (6 ADK agents) + concierge web app (backend +
> frontend) + shared mock data/state, plus the deployment path.
> ⚠️ Keep in sync with code (see CLAUDE.md): agent / tool / endpoint / data-contract / model / architecture changes land here.

> 📦 **Repository scope note (2026-07-25):** The **6 standalone ADK agents** described below
> (§1 architecture, §2 layout, §4 catalog) were **removed from source** — the repo now ships
> only the concierge web app (`backend/` + `frontend/`), which is fully self-contained: its in-process
> concierge agent (`server/agent.py` + `tools.py` + `logic.py`) reproduces the agents' user-facing
> capabilities, and domain mock data lives in `backend/server/mock_data.py`
> (was `daily_briefing/app/mock_data.py`). The agent-layer sections are **retained as the
> product vision / design of record**; the Agent Engine / Agent Runtime deployment notes in §11
> describe a prior deployment, not the current source tree.

---

## 1. Architecture overview

Two layers:

1. **Agent layer** — independent, deployable ADK agents (one folder each). Each is a
   self-contained, independently deployable managed agent-runtime app with mock-data fallback.
2. **Experience layer** — `backend/` + `frontend/`: a FastAPI backend running a single ADK **concierge**
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
   Web app backend      │ FastAPI (server/main.py)                                               │
   (local; → Cloud Run) │   ├── ADK Runner → concierge Agent (server/agent.py)                    │
                        │   │        └── tools (server/tools.py) ── read/write ──┐                │
                        │   └── read endpoints ─────────────────────────────────┤                │
                        │                              shared STORE (server/store.py) ◄───────────┤
                        │                              seeded by server/seed.py + logic (logic.py)│
                        └───────────────────────────────────────────────────────────────────────┘
                                    │ imports domain mock (single source of truth)
                        ┌───────────┴───────────────────────────────────────────────────────────┐
   Agent layer          │ daily_briefing · meeting_prep · meeting_room · proj_ma · rfp · sales    │
   (managed agent runtime)│ each: app/agent.py (tools + Agent+App), app/mock_data.py, app_utils/, │
                        │        agent_engine_app.py, tests/, pyproject.toml                       │
                        │        (+ Dockerfile, app/fast_api_app.py on daily_briefing/meeting_prep)│
                        └───────────────────────────────────────────────────────────────────────┘
```

## 2. Repository layout

The repo ships the concierge web app only (`backend/` + `frontend/` at the root). The 6
standalone ADK agents described in §4 were removed from source (see the scope note at top).

```
ai_assist/
├── ideas.md prd.md spec.md implementation.md README.md CLAUDE.md
├── Dockerfile .dockerignore .gcloudignore            # Cloud Run build (§11)
├── backend/   pyproject.toml, uv.lock, README.md, .env (gitignored — FRED_API_KEY),
│              server/{main,agent,tools,logic,store,seed,mock_data,llm,__init__}.py,
│              server/{market_data,fred_data,spacex_reference_data,spacex_case_study}.py
└── frontend/  package.json, vite.config.ts, src/{App,api,types,styles,richText}.tsx/ts,
               src/components/*, src/tabs/*, src/pages/*, src/styles/*.css,
               src/lib/caseStudyReportPdf.ts, src/hooks/useFreshTracker.ts
               (src/pages/SpacexAnalyticsPage.tsx — see PRD §6.8)
```

## 3. Model configuration

> Historical note: the removed 6-agent layer below was originally pinned to a hosted
> flash-tier model with region-scoped retry/availability handling. The current concierge
> agent's model configuration (Claude Haiku 4.5 via the Anthropic API) is documented in
> CLAUDE.md's "Model config" section — that's the source of truth for the live source tree.

- **Prompt convention:** system prompts are Markdown and use `[Variable]` placeholders (never
  `{Variable}`, which ADK treats as session-state lookups).

## 4. Agent layer

### 4.1 Conventions (all agents)
- Tools are plain Python functions returning **JSON strings**, with a `try:` real-API
  path and an `except:` mock fallback tagged `"source": "mock"`.
- Module exposes `root_agent = Agent(...)` and `app = App(root_agent=..., name=...)`;
  `app/__init__.py` re-exports `app`; `agent_engine_app.py` wraps it as `AgentEngineApp(AdkApp)`
  with telemetry + feedback.
- Packaging: `uv` + `pyproject.toml` (`google-adk>=1.15,<2`, plus per-agent API client libs).
- **Agent Runtime container entrypoint** (`daily_briefing`, `meeting_prep` — see §11): root
  `Dockerfile` builds the project and runs `app/fast_api_app.py` (a FastAPI app exposing
  `/api/reasoning_engine` + `/api/stream_reasoning_engine`, the `{class_method, input}`
  contract Agent Runtime's managed frontend forwards `:query`/`:streamQuery` calls to) plus
  `/feedback` and `/health`. It dispatches through the same `agent_engine` (`AgentEngineApp`)
  instance from `agent_engine_app.py` — no duplicated agent-wiring logic.

### 4.2 Agent catalog

| Agent (folder) | `Agent` name | Tools | Primary data sources | Output |
|---|---|---|---|---|
| **Daily Briefing** (`daily_briefing`) | `daily_briefing_agent` | `get_todays_calendar_events`, `get_recent_emails`, `get_starred_emails`, `get_market_context`, `suggest_meetings_to_schedule`, `get_meeting_prep`, `schedule_meeting`, + folded prep: `search_emails_by_attendees`, `search_drive_documents`, `get_drive_document_content`, `get_customer_profile` | Gmail, Calendar, payments & risk context (TPV, fraud/risk alerts, regulatory reminders); Drive + CRM profiles (folded); rooms/seats (for scheduling) | Morning briefing; per-meeting prep; scheduled event + room booking |
| **Meeting Prep** (`meeting_prep`) | `meeting_prep_agent` | `search_calendar_events`, `get_meeting_by_id`, `search_emails_by_attendees`, `search_drive_documents`, `get_drive_document_content`, `get_customer_profile` | Calendar, Gmail, Drive, customer profiles | Pre-meeting brief |
| **Meeting Room** (`meeting_room`) — NEW | `meeting_room_agent` | `list_available_rooms`, `get_attendee_locations`, `assign_meeting_room`, `book_room` | Room inventory, seat directory, booking ledger (mock) | Auto-assigned room + booking |
| **Project Mgmt** (`proj_ma`) | `project_management_agent` | `list_jira_projects`, `get_jira_project_summary`, `get_jira_issues`, `get_team_members`, `get_workload_analysis`, `create_project_plan_sheet` | Jira (mock), Sheets | Workload analysis; exported plan sheet |
| **RFP Response** (`rfp`) | `rfp_response_agent` | `read_rfp_from_drive`, `read_rfp_from_local_file`, `search_internal_documents`, `get_internal_document_content`, `create_rfp_response_document` | Drive docs | Drafted RFP → shared doc |
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
- `suggest_meetings_to_schedule()` → curated suggestions grounded in email/payments-risk signals,
  filtered to drop any whose subject already matches a calendar event.
- `get_meeting_prep(event_id|title)` → `{meeting, is_customer_meeting, customer_profile,
  recent_emails, related_documents}` (recent_emails exclude the owner to surface the other
  parties' threads).
- `schedule_meeting(title, attendees, date, start, end)` → creates a calendar event and
  auto-assigns/books a room using an embedded copy of the room logic (self-contained so the
  agent stays independently deployable).

## 5. Web app — backend (`backend`, package `server`)

- **`store.py`** — process-wide `STORE = Store()` holding mutable: `calendar_events`,
  `emails`, `market`, `drive_docs`, `customer_profiles`, `rooms`, `employee_locations`,
  `room_bookings`, `meeting_suggestions`, `jira`, `salesforce`, plus LLM caches
  `briefing_narrative` and `prep_cache[event_id]`, plus market-data caches
  `sec_cache[ticker:form]` and `stock_cache[ticker]`. `reset()` re-seeds and clears all caches.
- **`market_data.py`** — **live public-company market intelligence, stdlib only** (no
  `yfinance`/`pandas`; `urllib` + `http.cookiejar`), so the container stays slim.
  `get_sec_filings(ticker, cik, form_type="", limit=6)` GETs SEC EDGAR
  `data.sec.gov/submissions/CIK{cik:010d}.json` (descriptive `User-Agent` required) and parses
  `filings.recent` into recent 10-K/10-Q/8-K rows; `get_stock_snapshot(ticker)` performs Yahoo's
  cookie+crumb handshake and reads v7 quote + v10 `calendarEvents` (next earnings) + v1 search
  (headlines). **Live with graceful mock fallback**: on any error/timeout each function
  returns the baked-in fixtures from `mock_data` (`MOCK_SEC_FILINGS` / `MOCK_YAHOO_FINANCE`);
  every response is tagged `source: "live"|"mock"` (the API/data layer keeps this tag even though
  the UI no longer displays it — see §5.1/§9). Setting `DEMO_DISABLE_LIVE_MARKET=1` skips all
  network calls and always returns mock (used by tests/CI and for
  offline demos). No `Store` dependency — store-aware caching lives in `logic.py`.
- **`llm.py`** — direct Anthropic API client (Claude Haiku 4.5, see CLAUDE.md's "Model config"
  section): `generate_briefing_narrative(summary)` (prompt explicitly forbids opening with a
  greeting like "Good morning" — starts directly with the substance of the day; the composed
  no-model fallback matches) and `generate_meeting_prep(prep) ->
  {objective, agenda[], talking_points[], anticipated_questions[]}`, where each
  `anticipated_questions[]` entry is a normalized `{question, answer}` object (`_normalize_qa`
  coerces model output — dict, or a `"question — answer"` string — into that shape, so the UI
  never renders raw JSON). JSON parsed with a safe fallback; both degrade to composed text if
  the model is unavailable. Results cached by callers.
- **`seed.py`** — `build_seed()` imports `server.mock_data` (single source of truth for
  FinTechCo domain data; that module imports only `datetime`), deep-copies it, and adds
  demo-only `jira` and `salesforce` state.
- **`logic.py`** — pure functions over a `Store`: room availability/assignment/booking,
  `briefing_summary`, `suggest_meetings`, `meeting_prep`, `schedule_meeting`,
  `create_jira_tasks`, `log_salesforce_activity`, `update_opportunity`, `get_doc`, plus the
  market-intelligence wrappers `sec_filings(store, query, form_type="")`,
  `stock_snapshot(store, query)`, and `public_company_watch(store)` (`_resolve_company` matches a
  free-text ticker/name/keyword to a customer profile; private or unknown companies return a
  `{public: False, message}` / `{error}` shape rather than calling out). These wrap
  `market_data` and cache per ticker in the store. `briefing_summary` now includes
  `public_company_watch` (one compact row per public customer), and `meeting_prep` attaches
  `stock_snapshot` + `latest_filing` when the matched customer is public. Shared by
  tools and read endpoints so chat and UI-button paths behave identically. `book_room`
  (booking a room for an **existing** calendar meeting, as opposed to `schedule_meeting`
  which creates a new one) matches `event_title` against `calendar_events` and writes the
  new room into that event's `location`, so the meeting's prep/briefing views immediately
  reflect the booked room instead of the meeting's original (or empty) location.
- **`tools.py`** — ADK function tools (JSON-string wrappers over `logic` + `STORE`):
  `get_daily_briefing`, `suggest_meetings_to_schedule`, `get_meeting_prep`,
  `get_sec_filings(company_or_ticker, form_type="")`, `get_stock_snapshot(company_or_ticker)`,
  `list_available_rooms`, `assign_meeting_room`, `book_room`, `schedule_meeting` (optional
  `room_id` to override the auto-pick), `create_jira_tasks`, `log_salesforce_activity`,
  `update_opportunity`. Simple scalar/string args for reliable automatic function-calling
  (e.g., `task_titles` newline/`;`-separated).
- **`agent.py`** — single concierge `Agent` (`concierge_assistant`, Claude Haiku 4.5 via
  `LiteLlm`) with all tools; system prompt describes each capability (including the
  market-intelligence tools for public-company customers) and the confirm-before-write rule.
- **`main.py`** — FastAPI, CORS `*`, lazy `Runner` (`InMemorySessionService`, session per
  `session_id`). Endpoints below. Chat runs the sync ADK runner in FastAPI's threadpool;
  empty/failed turns return a friendly retry so the UI never breaks. If `backend/static/`
  exists (the Cloud Run image only — see §11), mounts the built frontend there and serves it at
  `/`, so `/` returns `index.html` and any other non-`/api` path falls through to it.
- **`fred_data.py`** — live macro context from the **FRED API** (Federal Reserve Bank of St.
  Louis), stdlib-only (`urllib`), reading `FRED_API_KEY` from `backend/.env` via
  `python-dotenv` (loaded at import time, path resolved relative to the module so it works
  regardless of CWD). `get_economic_snapshot()` returns fed funds (`DFF`), 10Y/2Y Treasury
  (`DGS10`/`DGS2`), unemployment (`UNRATE`), and a computed CPI YoY (`CPIAUCSL`, latest vs. a
  year prior) plus the 10Y–2Y `yield_curve_10y2y` spread. Same live/mock-fallback and
  `DEMO_DISABLE_LIVE_MARKET` convention as `market_data.py`; the mock snapshot is a real FRED
  pull captured 2026-07-28, not placeholder numbers.
- **`market_data.get_price_history(ticker, range_, interval)`** — new function alongside the
  existing SEC/Yahoo-quote helpers: Yahoo's `v8/finance/chart/{ticker}` endpoint (no
  cookie/crumb handshake needed, unlike the quote endpoint) for daily close-price history.
  Live-only (raises on failure) — callers with a specific ticker in mind supply their own mock
  fallback, since the generic `mock_data` fixtures don't carry time series.
- **`spacex_case_study.py`** ✅ — the **SpaceX (NASDAQ: SPCX) index-inclusion market-intelligence
  dashboard**, a self-contained case study independent of the FinTechCo customer domain
  (`mock_data.py`/`seed.py`); imports the pre-verified facts in `spacex_reference_data.py` as
  its mock/offline fallback. SpaceX IPO'd 2026-06-12 (ticker `SPCX`, CIK `0001181412`) and was
  fast-tracked into the Nasdaq-100 on 2026-07-06 — real, dated facts (see PRD §6.8; reference
  dates/CIK verified against sec.gov and public reporting as of 2026-07-28).
  - `get_price_series(ticker, fallback)` — SPCX/`^NDX` price history via
    `market_data.get_price_history`, falling back to the `fallback` list passed in (callers
    pass `spacex_reference_data.SPCX_PRICES`/`NDX_PRICES`) rather than `mock_data.py`.
  - `get_filings(limit=12)` — its own SEC EDGAR fetch (broader form set than
    `market_data.get_sec_filings`: whatever the live feed returns, not filtered to
    10-K/10-Q/8-K, since S-1/424B4/8-A12B/S-8 tell the IPO story), with descriptions backfilled
    from `spacex_reference_data.FILINGS` by `(form, filed)` match (SEC's own
    `primaryDocDescription` is usually just the form code repeated) — falls back to a generic
    `"{form} filing"` description for live filings outside the curated set (observed live for
    forms `3`/`4`/`EFFECT`, which the curated list doesn't cover), and to
    `spacex_reference_data.FILINGS` wholesale on total fetch failure.
  - `compute_event_study(spcx_prices, ndx_prices)` — offer-price/first-close/peak/latest/
    inclusion-date prices and their % changes, plus `excess_return_since_ipo_pct` (SPCX return
    net of the index's own move) and `drawdown_from_peak_pct`.
  - `compose_insights(metrics)` — deterministic, data-driven bullet insights (also the
    LLM narrative's fallback).
  - `bank_impact_sections(metrics)` — six categorized "impact on bank operations" sections
    (equity capital markets, index-fund/ETF flows, prime brokerage & securities-based lending,
    wealth/private banking, corporate banking, risk management), with points referencing the
    computed metrics.
  - `get_dashboard_payload()` — assembles everything (`timeline`, `prices`, `metrics`,
    `insights`, `filings`, `fred`, `bank_impact`) for the API/PDF; narrative is added by the
    endpoint layer, not this function.
  - `llm.generate_spacex_narrative(payload)` — 2-3 paragraph analyst narrative from the
    computed metrics, degrading to `"\n\n".join(payload["insights"])` if the model is
    unavailable (same try/except-compose pattern as `generate_briefing_narrative`).
  - `store.py` caches `spacex_cache`/`spacex_narrative` (cleared on `reset()`), same pattern as
    `sec_cache`/`stock_cache`.
  - Verified live end-to-end (2026-08-01): `prices`/`filings`/`fred` all returned
    `source: "live"` (real Yahoo Finance, SEC EDGAR, and FRED data) once `backend/.env` was
    populated — note that a fresh `git worktree` only checks out tracked files, so a gitignored
    `.env` from another checkout has to be copied over manually, it isn't inherited
    automatically. The mock-fallback branch is exercised separately by the backend test suite
    (`DEMO_DISABLE_LIVE_MARKET=1`, set in `conftest.py`).

### 5.1 HTTP API

| Method | Path | Body → Response |
|---|---|---|
| POST | `/api/assistant` | `{message, session_id?}` → `{reply, session_id}` (tools mutate STORE) |
| GET | `/api/briefing` | → `{date, events, upcoming_events, priority_emails, starred_emails, market, suggestions, public_company_watch, narrative}` (`events` = today only, `upcoming_events` = later dates sorted by start; `public_company_watch` = one row per public customer; narrative LLM-generated + cached) |
| GET | `/api/prep/{event_id}` | → `MeetingPrep` (incl. `stock_snapshot`/`latest_filing` for public customers) + `{objective, agenda[], talking_points[], anticipated_questions: {question, answer}[]}` (LLM, cached per event) |
| GET | `/api/stock/{query}` | → `StockSnapshot` for a public-company customer (ticker/name/keyword); private/unknown → `{public:false,message}` / `{error}` |
| GET | `/api/sec/{query}?form_type=` | → `SecFilingsResult` (recent 10-K/10-Q/8-K); optional `form_type` filter; private/unknown handled as above |
| POST | `/api/assign-room` | `{attendees[], date, start_time, end_time}` → best-fit room **preview (no write)** for the schedule widget |
| POST | `/api/available-rooms` | `{attendees[], date, start_time, end_time}` → `{available_rooms: Room[]}` — every free room, for the schedule widget's room dropdown |
| GET | `/api/doc/{doc_id}` | → `{name, content, webViewLink, category}` (document popup) |
| POST | `/api/schedule` | `{title, attendees[], date, start_time, end_time, room_id?}` → `{scheduled, event, room, rationale, booking}` — `room_id` overrides the auto-pick; `rationale` is `null` when a room is explicitly chosen |
| GET | `/api/calendar` | → `{date, events}` |
| GET | `/api/jira` | → `{project, columns, issues}` |
| GET | `/api/salesforce` | → `{accounts, opportunities, activities}` |
| GET | `/api/spacex-analytics` | → SpaceX index-inclusion dashboard payload (`timeline`, `prices: {spcx, index}`, `metrics`, `insights[]`, `filings`, `fred`, `bank_impact[]`, `narrative`) — cached per process, cleared on `/api/reset` |
| POST | `/api/reset` | → re-seed store, clear sessions |
| GET | `/api/health` | → `{status, service, date}` |
| GET | `/` | deployed container only: built SPA (`index.html`); no-op locally without a frontend build |

## 6. Web app — frontend (`frontend`, React + Vite + TS)

- **Routing (`App.tsx`):** a dependency-free **hash router** (listens to `hashchange`).
  Default renders the assistant app; `#/jira`, `#/salesforce`, and `#/spacex` render standalone
  full-page views (no assistant chrome), opened in a **new browser tab** via header buttons
  (`window.open('#/spacex','_blank')`). Hash routing keeps deep links / static hosting simple.
- **`pages/SpacexAnalyticsPage.tsx`** ✅ — fetches `/api/spacex-analytics` once on mount and
  renders key-metric stat tiles, the indexed price chart, the analyst narrative (via
  `richText.tsx`'s `renderRich` for `**bold**` lead-ins), the timeline, FRED macro tiles, the
  SEC filings list, and the "Impact on bank operations" card grid, plus a "Download PDF report"
  button. Uses two components that **already existed and were reused as-is**:
  - `components/IndexedPriceChart.tsx` — a generic, reusable 2-series indexed-line-chart (no
    charting library, built per the dataviz skill's method: single axis, both series rebased to
    100 at a shared start date, validated categorical color pair `#2a78d6`/`#eb6834`, legend +
    direct end-labels, hover crosshair+tooltip, and a "View as table" accessible fallback). Takes
    generic `seriesALabel`/`indexLabel` props — no SpaceX-specific text.
  - `lib/caseStudyReportPdf.ts` (`jspdf`, the only new frontend dependency) — a generic
    client-side PDF report generator (`downloadCaseStudyReport(report: CaseStudyReport)`,
    locally-typed, no dependency on any SpaceX-specific type) that redraws a chart/metrics/
    timeline/filings/FRED/bank-impact layout as a multi-page PDF **entirely client-side** — no
    server round-trip, no backend PDF dependency (kept off the backend deliberately, matching
    this project's stated preference for a slim container — see the `market_data.py`
    stdlib-only rationale in this section).
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
                  stock_snapshot?: StockSnapshot|null, latest_filing?: SecFiling|null,
                  recent_emails[], related_documents[],
                  objective?, agenda?[], talking_points?[], anticipated_questions?: AnticipatedQuestion[] }
AnticipatedQuestion { question, answer? }
CustomerProfile { name, full_name, type, keywords[], public: bool,
                  ticker?, exchange?, cik?, investment_profile{...}, fintechco_relationship{...}, ... }
SecFiling       { form, filed, period, accession, primary_doc, url, summary? }
SecFilingsResult{ company, ticker, cik, source: "live"|"mock", filings: SecFiling[] }
                  # private/unknown → { public:false, company, message } / { error, query }
StockSnapshot   { ticker, company, exchange, currency, source: "live"|"mock",
                  quote{ price, change, change_pct, prev_close, day_low, day_high,
                         week52_low, week52_high, volume, market_cap, pe_ratio },
                  next_earnings_date, news: [{ headline, source, date, url }] }
PublicCompanyWatch { name, company, ticker, exchange, currency, price, change, change_pct,
                  next_earnings_date, latest_filing: {form, filed, url}|null, headline, source }
JiraIssue       { id, key, project, title, description, assignee, status, priority, created }
JiraBoard       { project, columns: ["To Do","In Progress","Done"], issues[] }
SF.account      { id, name, type, scale, owner, status }
SF.opportunity  { id, account, name, stage, amount, close_date }
SF.activity     { id, account, type, summary, date }
```
`meeting_type` derivation: any attendee domain outside `fintechco.com` /
`chenkeamonwang.altostrat.com` ⇒ `customer`. Customers are modeled as **real public
companies** — Williams-Sonoma (NYSE: WSM, CIK 0000719955), Etsy (Nasdaq: ETSY, 0001370637),
Dave (Nasdaq: DAVE, 0001841408) — plus one private firm, Glenbrook Partners (`public:false`,
no ticker). `mock_data.py` also carries `TICKER_CIK`, `MOCK_SEC_FILINGS`, `MOCK_YAHOO_FINANCE`
as the offline fallback fixtures.

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

- **v1:** mock/synthetic data; API-key auth to the model provider; no per-employee identity;
  write actions confirmed by the assistant. CORS open for local dev.
- **Roadmap:** per-employee OAuth to scope Gmail/Calendar/Drive; authz on write actions;
  audit trail for CRM/Jira writes; secret management for real Jira/Salesforce credentials;
  tighten CORS for deployed origins.

## 10. Testing & evaluation

Automated tests run in **GitHub Actions** (`.github/workflows/ci.yml`) on every pull request
and on pushes to `main`, so changes are tested before merge. Two independent jobs:

- **Backend (`backend/tests/`, pytest):** run hermetically with `DEMO_DISABLE_LIVE_MARKET=1`
  (set in `conftest.py` and the CI job env) so the market-data layer never hits the network and
  the LLM helpers are monkeypatched (no live model calls). Coverage:
  - `test_market_data.py` — SEC/stock **mock-fallback** (every response `source:"mock"`), form
    filtering, unknown-ticker handling; `get_stock_snapshot`'s Yahoo→mock fallback
    (monkeypatched, no real network calls).
  - `test_logic.py` — `_resolve_company` (ticker/name/keyword), `sec_filings`/`stock_snapshot`
    (public vs private vs unknown) + caching, `public_company_watch`, `briefing_summary`
    includes the watch, `meeting_prep` enrichment (customer vs internal), and demo write
    actions (`log_salesforce_activity`, `create_jira_tasks`).
  - `test_api.py` — FastAPI **TestClient** over `/api/health`, `/api/reset`, `/api/briefing`
    (has `public_company_watch`), `/api/stock/{q}`, `/api/sec/{q}` (public/private/form-filter),
    `/api/prep/{id}` (enriched), `/api/salesforce` (renamed accounts).
  - `test_seed.py` — no stale customer names/domains remain; public profiles carry
    `ticker`/`cik` present in the fixtures; Glenbrook stays private.
  - Config: `pytest` + `httpx` in the `dev` dependency group; `[tool.pytest.ini_options]` sets
    `testpaths`, `pythonpath="."`. Run: `uv sync && uv run pytest`.
- **Frontend (`frontend/src/**/*.test.tsx`, Vitest + React Testing Library, jsdom):**
  `Chat.test.tsx` (starters render incl. the market-intel prompt; clicking sends),
  `AssistantTab.test.tsx` (the Customer market watch card renders from a mocked briefing —
  ticker, price, move, filing — and asserts no "mock"/"live" provenance text is shown),
  `richText.test.tsx` (bold + line-break rendering).
  Test files are excluded from the production `tsc -b` build. Run: `npm run test`
  (`vitest run`); `npm run build` (tsc + vite) remains the smoke gate and also runs in CI.
- **Eval (roadmap):** ADK evalsets / rubric-based response quality for scheduling, prep, and
  write-back correctness.

## 11. Deployment

- **Local (v1):** backend `uv run uvicorn server.main:app --port 8000`; frontend
  `npm run dev` (proxy) or `npm run build` + static serve. Requires an Anthropic API key for
  the chat.
- **Agent Runtime (historical):** `daily_briefing` and `meeting_prep` deployed to a managed
  agent runtime (`deployment_target = "agent_runtime"`) via `agents-cli deploy` (CLI v1.1.0+),
  which builds and deploys the project's `Dockerfile` (container-based) rather than the prior
  source-tarball/introspection path used by the older target name. Both were already deployed
  under the old flow (`reasoningEngines/7580645040108601344` and `.../8231978136217059328` in
  `us-central1`) — `deployment_metadata.json`'s `remote_agent_runtime_id` still points at those
  same resource IDs; re-running `agents-cli deploy` updates them in place to the container
  build. **Not yet migrated:** `meeting_room`, `proj_ma`, `rfp`, `sales` still have
  `deployment_target = "agent_engine"` in `pyproject.toml` and no
  `Dockerfile`/`fast_api_app.py` — since the CLI is now v1.1.0 globally, `agents-cli deploy` on
  those four will fail ("Unknown deployment target: agent_engine") until they get the same
  migration, or are deployed with a pinned CLI version.
- **Managed agent-app registration (historical):** all 6 agents were registered as ADK agents
  in the **FinTechCo Personal AI Assistant** app
  (`projects/799954743226/locations/global/collections/default_collection/engines/
  fintechco-personal-ai-assistant_1778868872170`) as "FinTechCo Daily Briefing", "FinTechCo
  Meeting Prep", "FinTechCo Project Management", "FinTechCo RFP Response", "FinTechCo Sales
  Support" (meeting_room was not registered). Each entry's
  `adkAgentDefinition.provisionedReasoningEngine` points at that agent's
  `remote_agent_runtime_id`/`remote_agent_engine_id`; re-run `agents-cli publish` after any
  redeploy that changes the resource ID, or to refresh display name/description. The same app
  also hosted an unrelated low-code "Daily Financial Briefing Agent" built directly in that
  platform's UI (no `provisionedReasoningEngine` — not connected to our `daily_briefing`
  agent).
- **Cloud Run (shipped):** one combined service — root `Dockerfile` (two-stage: `node:20-slim`
  builds `frontend` → `dist/`, then `python:3.12-slim` + `uv sync`s `backend`,
  copies `backend/server` — including `mock_data.py` — into the image, and copies the
  built frontend into `backend/static/`). The deployable surface is fully self-contained
  under `backend/` + `frontend/`.
  FastAPI serves `/api/*` and the built SPA from the same origin (no CORS, no cross-service
  IAM). Deployed as `fintechco-assistant` in `us-central1`, `--no-allow-unauthenticated` with
  `roles/run.invoker` granted to `domain:chenkeamonwang.altostrat.com` (matches the IAM pattern
  on sibling Cloud Run services in this project), `--max-instances=1` / `--min-instances=0`
  since `STORE` is still in-process (single-instance demo) — revisit both the instance cap and
  a shared datastore together if multi-instance is ever needed. Credentials: `ANTHROPIC_API_KEY`
  is provided to the container as a secret/env var; no cloud-provider IAM/ADC wiring is needed
  for the chat path.

## 12. Observability

- Agent Runtime apps ship telemetry via `app_utils/telemetry.py`;
  `AgentEngineApp.register_feedback` logs structured feedback (reached over
  HTTP via `/feedback` on the container-deployed agents).
- Backend: standard logging; add request/latency metrics and per-tool call logging when
  deployed. Frontend: capture chat errors surfaced to the user.

## 13. Future technical work

- Shared CRM/Jira **service layer** replacing per-agent mocks; real API integrations behind
  the same tool contracts.
- **Orchestration:** promote the single-agent concierge to agent-as-tool / `sub_agents`
  routing across specialists (Project Mgmt, Sales, RFP, Compliance, Research) as they are
  onboarded.
- **New agents:** Compliance (gating), Post-Meeting (closes the loop into CRM/Jira/briefing),
  Payments & Risk Intelligence; then Tier 2/3 employee agents.
- Persist store to a datastore for multi-instance Cloud Run; per-employee auth; eval-in-CI.
- Migrate `meeting_room`, `proj_ma`, `rfp`, `sales` to Agent Runtime the same way as
  `daily_briefing`/`meeting_prep` (see §11) — needed before `agents-cli deploy` works for
  them again under the now-global CLI v1.1.0.
