# FinTechCo Employee Digital Assistant — Implementation Plan & Checklist

> Status: Living document · Version 1.6 · Date: 2026-07-28
> Upstream: [`prd.md`](prd.md) · [`spec.md`](spec.md) · Convention: [`CLAUDE.md`](CLAUDE.md)
>
> Purpose: bridge spec → code. Track what's built, what's left, and the running backlog.
> **Keep this in sync with every code change** (per CLAUDE.md golden rule). Check items off
> as they land; add new work to the roadmap/backlog sections.

Legend: `[x]` done · `[~]` partial/in progress · `[ ]` not started

---

## Phase 1 — v1 concierge demo  ✅ (delivered 2026-07-16)

### A. Meeting Room Booking agent (`meeting_room/`)
- [x] Scaffold folder mirroring existing agents (`app_utils/`, `agent_engine_app.py`, tests, `pyproject.toml`, `GEMINI.md`, `README.md`)
- [x] `mock_data.py`: `MOCK_ROOMS`, `MOCK_EMPLOYEE_LOCATIONS`, `MOCK_ROOM_BOOKINGS` (One Congress / Channel Center / Toronto)
- [x] Tools: `list_available_rooms`, `get_attendee_locations`, `assign_meeting_room`, `book_room`
- [x] Assignment algorithm: capacity + proximity (building→floor), tightest fit, AV-if-remote; no double-book
- [x] `agents-cli install` + tool-logic smoke test + standalone Runner turn
- [ ] Real unit tests replacing `tests/unit/test_dummy.py`
- [ ] Evalset cases in `tests/eval`

### B. Daily Briefing upgrades (`daily_briefing/`)
- [x] Add `suggest_meetings_to_schedule` (+ `MOCK_MEETING_SUGGESTIONS`, filtered vs calendar)
- [x] Add `schedule_meeting` (creates event + auto-books room; embedded room logic + rooms/seats mock)
- [x] Fold in Meeting Prep: copy `search_emails_by_attendees`, `search_drive_documents`, `get_drive_document_content`, `get_customer_profile` + `MOCK_DRIVE_DOCS`/`MOCK_CUSTOMER_PROFILES`
- [x] Add `get_meeting_prep(event_id|title)` composing the prep brief (owner excluded from recent emails)
- [x] Update system prompt (suggested-meetings section, expandable prep, scheduling) + register tools
- [x] Tool-logic smoke test + standalone Runner turn
- [ ] Real unit tests; evalset cases for scheduling/prep
- [ ] Decide long-term: retire standalone `meeting_prep/` once folded version is proven (kept for now)

### C. Web app backend (`backend`, package `server`)
- [x] `store.py` shared mutable `STORE` + `reset()`
- [x] `seed.py` loads `daily_briefing/app/mock_data.py` by path (single source of truth) + demo Jira/Salesforce
- [x] `logic.py` pure functions (rooms, briefing, suggestions, prep, schedule, jira, salesforce)
- [x] `tools.py` ADK tool wrappers (scalar/string args for reliable function-calling)
- [x] `agent.py` concierge Agent (all tools) — `gemini-3.5-flash`@`us`
- [x] `main.py` FastAPI: `/api/assistant` (lazy Runner) + read endpoints + `/api/schedule` + `/api/reset`
- [x] Graceful empty/error reply fallback
- [x] `pyproject.toml`, `uv sync`, endpoint + chat smoke tests (Jira & Salesforce writes verified)
- [ ] FastAPI TestClient integration tests

### D. Web app frontend (`frontend`, React+Vite+TS)
- [x] Scaffold (package.json, vite proxy `/api`→:8000, tsconfig, index.html)
- [x] `types.ts`, `api.ts`, `styles.css` design system
- [x] `App.tsx` shell: tabs, `refreshKey` + 5s poll, chat state, Reset
- [x] `components/Chat.tsx` concierge chat (starters, busy state, refresh-after-turn)
- [x] `tabs/AssistantTab.tsx` (stat tiles, expandable per-meeting prep, Schedule buttons)
- [x] `tabs/RoomsTab.tsx`, `tabs/JiraTab.tsx` (kanban), `tabs/SalesforceTab.tsx`
- [x] `hooks/useFreshTracker.ts` (flash newly created items)
- [x] `npm run build` clean (tsc + vite)

### E. Cross-cutting
- [x] Model/location switched to `gemini-3.5-flash`@`us` across all 6 agents + backend
- [x] Docs: `prd.md`, `spec.md`, `CLAUDE.md`, `implementation.md`
- [x] End-to-end verification via Vite proxy: chat→Jira (5→7), chat→Salesforce (+1), Schedule→rooms/calendar, expand→prep
- [ ] `.gitignore` review for `backend/` + `frontend/` (`node_modules`, `.venv`, `dist`, `__pycache__`)

---

## Phase 1.5 — UX polish  ✅ (delivered 2026-07-16)

- [x] **Standalone Jira page** (`pages/JiraPage.tsx` + `styles/jira.css`) — realistic board
      (sidebar, top bar, columns, issue-type/priority icons, avatars, points); opened in a new tab
- [x] **Standalone Salesforce page** (`pages/SalesforcePage.tsx` + `styles/salesforce.css`) —
      Lightning-style (global header, object nav, list views, activity timeline); new tab
- [x] Hash router in `App.tsx` (`#/jira`, `#/salesforce`); reduced tabs to Assistant · Rooms;
      header **Open Jira ↗ / Open Salesforce ↗** buttons; deleted old `tabs/JiraTab`, `SalesforceTab`
- [x] **Schedule confirmation widget** (`components/ScheduleModal.tsx`) — pre-filled fields +
      room preview via `POST /api/assign-room`; Confirm → `POST /api/schedule`
- [x] **Auto daily briefing** — LLM narrative (`llm.generate_briefing_narrative`, cached) shown
      on load in `AssistantTab`
- [x] **Document popups** (`components/DocModal.tsx` + `GET /api/doc/{id}`)
- [x] **Per-meeting prep + talking points** — `llm.generate_meeting_prep` (objective/agenda/
      talking_points/anticipated_questions), cached per event; rendered on meeting expand
- [x] `components/Modal.tsx` generic modal; store caches + `reset()` clears them
- [x] `npm run build` clean (43 modules); backend endpoints verified
- [ ] Restart deployed backend after these edits when deploying (Phase 2)
- [ ] Frontend component tests for the schedule/doc modals

## Phase 1.6 — bug fixes / polish  ✅ (delivered 2026-07-16)

- [x] **Upcoming meetings fix** — `logic.briefing_summary` now returns `upcoming_events`
      (calendar events after today, sorted by start); `AssistantTab` renders them in a new
      "Upcoming meetings" card so a confirmed meeting scheduled for a non-today date (e.g.
      from a suggestion) no longer disappears. `MeetingRow` gained a `showDate` prop.
- [x] **Room override dropdown** — `POST /api/available-rooms` (new endpoint, wraps
      `logic.list_available_rooms`); `logic.schedule_meeting` + `/api/schedule` +
      the `schedule_meeting` ADK tool all accept an optional `room_id` to book a specific
      room instead of the auto-pick. `ScheduleModal` now shows a `<select>` of every free
      room for the slot (defaulting to the recommended one, editable before Confirm).
- [x] **Salesforce logo** — replaced the `☁` text glyph in `SalesforcePage`'s global header
      with an inline SVG cloud logomark (`styles/salesforce.css` `.sf-cloud` updated for sizing).
- [x] `npm run build` clean; backend endpoints verified end-to-end (see verification below)

## Phase 1.7 — remove Meeting Rooms tab  ✅ (delivered 2026-07-17)

- [x] Deleted `tabs/RoomsTab.tsx` — it only ever rendered backend state (room inventory,
      seat directory, today's bookings) that the concierge agent already owns via
      `list_available_rooms`/`assign_meeting_room`/`book_room`; the Schedule widget's room
      dropdown (Phase 1.6) is the only UI surface for it now
- [x] `App.tsx`: removed the tab nav entirely (single view remained once Rooms was cut) —
      dropped `TabId`/`TABS`, `tab` state, and the `<nav className="tabs">` block
- [x] Removed now-dead code: `GET /api/rooms` (backend), `api.rooms()`, `RoomsData` /
      `Booking` / `EmployeeLocation` types, `.tabs`/`.tab`/`.grid-cards`/`.room`/`.booking`/
      `table.tbl` CSS
- [x] `npm run build` clean; confirmed `/api/rooms` now 404s and nothing else regressed

## Phase 1.8 — bug fixes / polish  ✅ (delivered 2026-07-17)

- [x] **Anticipated questions rendered as raw JSON** — `llm.generate_meeting_prep` asked the
      model for `anticipated_questions[]` as free-form strings-or-objects and stringified
      whatever came back with `json.dumps`, so the UI showed literal `{"question": ...,
      "answer": ...}` text. Added `llm._normalize_qa()` to coerce any model output (dict,
      or a `"question — answer"` string) into a `{question, answer}` object; updated the
      prompt to request that shape explicitly; updated the exception fallback to match.
      `types.ts` gained `AnticipatedQuestion { question, answer? }` and
      `MeetingPrep.anticipated_questions` is now typed as `AnticipatedQuestion[]`.
      `AssistantTab.tsx` renders each as a `.qa-item` card (Q/A lines) instead of a flat
      `<li>`. Verified end-to-end against a live browser session (Playwright) across all 6
      seeded meetings.
- [x] **Salesforce logo realism** — swapped the hand-drawn 3-circle+rect cloud SVG for a
      smooth path-based cloud glyph (from Bootstrap Icons' `cloud-fill`, MIT-licensed),
      colored white (`.sf-cloud`) to match the real Lightning nav bar; removed the "Sales"
      wordmark text next to it per request (the icon now stands alone, as in the real
      Salesforce app switcher header).
- [x] `npm run build` clean; verified both fixes visually via a headless Playwright session
      against the running dev server.

## Phase 1.9 — bug fixes / polish  ✅ (delivered 2026-07-17)

- [x] **Booked room didn't update the meeting card** — `logic.book_room` (booking a room for
      an *existing* calendar meeting via chat, distinct from `schedule_meeting`) only wrote a
      `room_bookings` entry; it never touched the matching `calendar_events` entry, so the
      meeting's `location` — and therefore its prep card and briefing view — kept showing the
      original (or empty) location after the assistant confirmed a room. Fixed by having
      `book_room` look up the event via `_find_event(store, title=event_title)` and write the
      new `"{room name} ({building}, fl {floor})"` string into its `location` (also fixed the
      returned `location` string itself, which previously omitted the room name).
      `AssistantTab.tsx`'s `MeetingRow` also cached its `/api/prep/{id}` response forever once
      fetched, so even with the backend fixed an already-open (or previously-opened) meeting
      card wouldn't pick up the change; it now re-fetches prep on every `refreshKey` bump
      when open, and clears its cached prep when closed so the next open is fresh — reusing
      the existing FR-L1 poll/action-bump mechanism, no new plumbing needed. Verified live via
      Playwright: booked a different room over chat for an already-expanded meeting card and
      watched its location update in place.
- [x] **Salesforce logo color** — `.sf-cloud` now uses `var(--sf-blue)` (`#0176d3`, the same
      brand blue already used for links/active-tab state elsewhere on the page) instead of
      white, so the header cloud icon matches Salesforce's actual brand color.
- [x] `npm run build` clean; verified both fixes visually via a headless Playwright session
      against the running dev server; reset the demo store afterward.

## Phase 1.10 — bug fixes / polish  ✅ (delivered 2026-07-17)

- [x] **Chat widget showed literal `**bold**`** — `AssistantTab.tsx` already had a
      `renderRich()` helper (bold + line breaks) for the daily briefing narrative, but
      `Chat.tsx` rendered `{m.text}` raw, so any `**...**` the model emitted in a reply showed
      as literal asterisks instead of bold. Extracted `renderRich()` into a shared
      `src/richText.tsx` and used it from both `AssistantTab.tsx` and `Chat.tsx`. Verified
      live via Playwright: a "daily briefing" chat reply now renders `<strong>` tags with no
      literal `**` in the text.
- [x] `npm run build` clean.

## Phase 2 — deploy + connective agents  ⏳

- [x] Migrate `daily_briefing` and `meeting_prep` to Agent Runtime (`deployment_target =
      "agent_runtime"`, root `Dockerfile` + `app/fast_api_app.py` container entrypoint
      serving the `{class_method, input}` reasoning_engine contract; `deployment_metadata.json`
      renamed to `remote_agent_runtime_id`) — see `spec.md` §4.1/§11. Verified locally: unit +
      integration tests pass, `docker build` + `docker run` smoke-tested against the live
      `gemini-3.5-flash` model on both `/api/reasoning_engine` and `/api/stream_reasoning_engine`.
      Note: the global `agents-cli` tool was upgraded 0.0.1a1 → 1.1.0 to get Agent Runtime
      support, which means `meeting_room`/`proj_ma`/`rfp`/`sales` (still `deployment_target =
      "agent_engine"`, no Dockerfile) can no longer `agents-cli deploy` until they get the same
      migration — see Backlog.
- [x] Deploy `daily_briefing` and `meeting_prep` to Agent Runtime (`agents-cli deploy`,
      2026-07-17) — updated the existing resources in place to the new container-based build
      (same `remote_agent_runtime_id`s: `reasoningEngines/7580645040108601344` and
      `.../8231978136217059328`, `us-central1`). Verified live via
      `agents-cli run --url ... --mode adk`: both agents respond correctly post-deploy.
- [x] Re-registered both with the **SSIM Personal AI Assistant** Gemini Enterprise app
      (`ssim-personal-ai-assistant_1778868872170`, `agents-cli publish gemini-enterprise`,
      2026-07-17) — updated the existing "SSIM Daily Briefing" and "SSIM Meeting Prep" agent
      entries in place (matched by reasoning-engine ID) to point at the new container-based
      deploy. Same app also hosts `SSIM Sales Support`/`SSIM RFP Response`/`SSIM Project
      Management` (still on the old `agent_engine` deploy — unaffected) and an unrelated
      low-code "Daily Financial Briefing Agent" built in Gemini Enterprise's UI (no
      `provisionedReasoningEngine`, not connected to our `daily_briefing` agent — don't confuse
      the two).
- [ ] Migrate `meeting_room` and deploy it to Agent Runtime — **needs approval**
- [x] Containerize `backend` (FastAPI) → Cloud Run — single combined service, root
      `Dockerfile`; see `spec.md` §11
- [x] Build + serve `frontend` (static) → Cloud Run — bundled into the backend image and
      served same-origin by FastAPI, so the "tighten CORS to deployed origin" item is moot
      (no cross-origin requests left to tighten)
- [ ] **Compliance & Regulatory agent** (gates RFP/Sales drafts) — new agent + UI compliance badge
- [ ] **Post-Meeting / Follow-up agent** (writes CRM/Jira/next-day briefing) — closes the loop
- [ ] Surface Project Mgmt & Sales journeys in the concierge (add their tools/tabs)

## Phase 3 — research + real data  ⏳

- [ ] **Payments & Risk Intelligence agent** (fraud/authorization trends, network/market context)
- [ ] Real integrations behind existing tool contracts (Gmail/Calendar/Drive, then Jira/Salesforce)
- [ ] Per-employee OAuth identity + scoped access; authz on writes; audit trail
- [ ] Shared CRM/Jira **service layer** replacing per-agent mocks
- [ ] Eval-in-CI + observability dashboards

## Phase 4 — broader employee agents  ⏳

- [ ] Client Reporting / review-pack generator; Knowledge/Policy (HR/IT) Q&A
- [ ] IT helpdesk; Expense & Travel; New-hire onboarding

---

## Phase 5 — payments/banking domain re-theme  ✅ (delivered 2026-07-25)

- [x] Re-themed the fictional company's business model from institutional asset management to
      a digital payment services company with a traditional commercial banking division, per
      user request. Company name/brand ("State Street Investment Management (SSIM)",
      `@statestreet.com`) intentionally kept unchanged — only business content/terminology
      changed. *(Superseded by Phase 6 below — the brand was later renamed to FinTechCo.)*
- [x] Reused the existing "$4.1T" headline figure, redefined as total payment volume (TPV)
      processed annually (card/ACH/RTP-FedNow/cross-border), plus a new $85B commercial
      deposits / $40B commercial loans banking-division figure.
- [x] Replaced the CalPERS/OTPP/GIC pension-fund/SWF client roster with three payments/banking
      clients used consistently across all 6 agents and the webapp: **Northwind Retail Group**
      (merchant, existing payments client), **Atlas Marketplace** (merchant, payments+BaaS RFP
      finalist), **Brightline Financial** (fintech BaaS partner).
- [x] Rewrote all 6 agents' `app/agent.py` system prompts and `app/mock_data.py` fixtures
      (`daily_briefing`, `meeting_prep`, `meeting_room` [light touch], `proj_ma`, `rfp`,
      `sales`) to payments/banking terminology (PCI-DSS, BSA/AML, OFAC, Reg E/CC, Durbin
      Amendment, OCC/FDIC/Fed oversight, card network rules) in place of
      ESG/SFDR/MiFID/AIFMD/pension-fund language.
- [x] `daily_briefing`/webapp: renamed the market-context nested keys
      `ssim_aum_snapshot`→`ssim_payments_banking_snapshot`, `total_aum`→`total_tpv`,
      `aum_change_mtd`→`tpv_change_mtd`, `portfolio_alerts`→`risk_alerts`,
      `securities_lending`→`treasury_sweep` (same shapes, new meaning); updated `server/llm.py`
      to read the new keys and reframe its briefing/prep prompts.
- [x] `rfp/app/mock_data.py`: replaced the CalPERS-style investment RFP question bank with an
      enterprise merchant payments/BaaS RFP (Company Overview, Payment Processing Capabilities,
      Risk/Fraud/Chargeback, Security & Compliance, Banking/BaaS Program, Integration,
      Pricing, Implementation, References); ESG DDQ → Compliance & Security DDQ; securities
      lending overview → Merchant Reserve & Treasury Sweep Program overview.
- [x] `sales/app/mock_data.py` + `sales/app/agent.py`: replaced the 6 fund products with 6
      payments/banking products (Payment Gateway, Real-Time Payments Suite,
      Banking-as-a-Service, Cross-Border Payments, Commercial Banking, Merchant Treasury &
      Cash Management, preserving the original product dict schema); replaced the
      CalPERS/OTPP/GIC/ADIA/NYSCRF pension-fund/SWF client roster with the shared
      Northwind Retail Group / Atlas Marketplace / Brightline Financial roster (CRM
      interactions, emails, Drive docs, and customer profiles all rewritten to match);
      replaced BlackRock/Vanguard/PIMCO/Fidelity competitive intel (`INTEL` dict in
      `get_competitive_intelligence`) with Stripe/Adyen/Fiserv/Block (Square); rewrote the
      system prompt's business description, product suite, regulatory-context list, and
      consultant-search-dynamics line (→ Glenbrook-Partners-style payments advisory firms).
- [x] `proj_ma/app/mock_data.py`: replaced trading-systems/model-validation/ESG-data project
      categories and team skills with payments-platform/fraud-BSA-AML/core-banking/KYC
      categories.
- [x] `backend/server/seed.py`: renamed demo Salesforce accounts/opportunities/
      activities and Jira issues to the new client roster; renamed `SF.account.aum` →
      `SF.account.scale` (a display string covering both merchant TPV and banking deposits) —
      updated in `types.ts`, `SalesforcePage.tsx`, and `spec.md` §7.
- [x] `frontend`: updated `App.tsx` subtitle, `AssistantTab.tsx`'s "Total AUM" stat tile
      (now "Total Payment Volume", reading the renamed snapshot keys), `Chat.tsx` starter
      prompts, and `SalesforcePage.tsx`'s "AUM" column to "Scale".
- [x] `prd.md`/`spec.md`: updated the Overview business description, personas (Portfolio
      Manager/Strategist → Payments Product/Risk Manager), roadmap items (Investment Research →
      Payments & Risk Intelligence), and FR-B1 wording; bumped both to v1.0.
- [x] **Follow-up (2026-07-25):** the Daily Briefing dashboard's `ssim_payments_banking_snapshot`
      showed SSIM's ~$4.1T *annual* TPV run-rate as the stat tile — a static company-scale figure
      that never changes day to day, so it wasn't actionable for a daily briefing. Changed
      `daily_briefing/app/mock_data.py`'s snapshot to **yesterday's TPV** instead (`total_tpv`:
      "$11.2 billion", i.e. ≈ annual/365, split card/ACH/real-time/cross-border proportionally;
      `commercial_deposits`/`commercial_loans` are already balance-sheet snapshots, left as-is;
      added an `as_of` field), renamed `tpv_change_mtd` → `tpv_change_dod` with a day-over-day
      value. Updated `backend/server/llm.py`'s narrative prompt ("Yesterday's total
      payment volume") and `AssistantTab.tsx`'s stat tile label to "Payment Volume (Yesterday)"
      reading the renamed `tpv_change_dod` field. The company-scale "~$4.1T annual TPV"
      statement used elsewhere (system prompts, RFP/sales positioning, `App.tsx`'s header
      subtitle, `prd.md` Overview) is intentionally unchanged — that's a legitimate "how big is
      this company" figure, distinct from the operational dashboard metric.

## Phase 5.1 — dead-code cleanup  ✅ (delivered 2026-07-25)

Repo-wide sweep for unused code; no behaviour or API-contract changes (so `prd.md`/`spec.md`
untouched). Verified: `npm run build` + a forced `tsc -b --force` pass, backend `ruff`
`F401/F811/F841` clean, all six agent files `py_compile` clean, live `/api/briefing` unchanged.

- [x] Removed unused imports: `os` in `backend/server/llm.py`, `datetime` in
      `rfp/app/agent.py`, and a dead `from google.oauth2 import credentials as oauth2_credentials`
      in `daily_briefing/app/agent.py` (the calendar tool uses ADC, never that alias).
- [x] Removed the unused `STAGE_ORDER` constant in `frontend/src/pages/SalesforcePage.tsx`.
- [x] Removed the schedule-modal **Description** field end to end: the textarea captured input
      that `confirm()` never sent to `/api/schedule` and no view renders an event description.
      Dropped `description` from `ScheduleInitial`, its state/textarea in `ScheduleModal.tsx`, and
      the `description: s.rationale` pass-through in `AssistantTab.tsx`.
- [x] Turned on `noUnusedLocals` + `noUnusedParameters` in `frontend/tsconfig.json` so
      future dead locals/params fail the build gate.
- [x] Confirmed no dead `MOCK_*` constants (every one is imported by its agent) and no
      orphaned files — the per-agent `app_utils/` scaffolding is live (imported by
      `agent_engine_app.py`/`fast_api_app.py` for deploy), so it stays.

## Phase 5.2 — webapp-only slim-down + repo flatten  ✅ (delivered 2026-07-25)

Reduced the repo to just the deployable web app and flattened its layout. The 6 standalone ADK
agents were never imported by the web app (the concierge agent reproduces their capabilities);
their only remaining tie was `seed.py` loading `daily_briefing/app/mock_data.py` by file path.
Design/vision for the agents is retained in `prd.md`/`spec.md` (scope notes added at the top of
each). Verified end-to-end after each step: live `/api/health`, `/api/reset` (re-runs
`build_seed`), and `/api/briefing` (5 events, 6 priority emails, TPV $11.2 billion); frontend
`npm run build` clean.

- [x] Relocated the domain mock data to the web app: `git mv daily_briefing/app/mock_data.py
      backend/server/mock_data.py`; rewrote `seed.py` to `from server import mock_data` (dropped
      the `importlib`/file-path hack). It's now the true single source of truth in-repo.
- [x] Deleted all 6 standalone agent folders (`daily_briefing`, `meeting_prep`, `meeting_room`,
      `proj_ma`, `rfp`, `sales`) — 136 tracked files.
- [x] Simplified the Cloud Run build: removed the `COPY daily_briefing/app/mock_data.py …` line
      and its comment from the root `Dockerfile` (mock data now ships inside `server/`), and
      removed the agent-folder exclusion block from `.gcloudignore`.
- [x] Flattened `webapp/` away: moved `webapp/backend` → `backend/` and `webapp/frontend` →
      `frontend/` at the repo root, promoted `webapp/README.md` to the root `README.md` (paths
      updated), and removed the empty `webapp/`. Updated all path references in `Dockerfile`,
      `.dockerignore`, `.gcloudignore`, `prd.md`, `spec.md`, `implementation.md`, `CLAUDE.md`,
      and the `backend/server/main.py` static-frontend comment.

## Phase 6 — public-company customer intelligence + automated tests/CI  ✅ (delivered 2026-07-25)

Added external market intelligence on the customers (SEC EDGAR filings + a Yahoo Finance market
snapshot) to the daily briefing, meeting prep, and chat — and modeled the three merchant/BaaS
customers as **real mid-cap public companies** so those filings and quotes are genuinely useful.
Then closed the long-standing "no test suite" gap with backend + frontend suites wired into CI so
changes are tested before merge. Live APIs with graceful mock fallback; every response tagged
`"source": "live" | "mock"`. Verified end-to-end: live SEC returns real `ETSY INC` / `WILLIAMS
SONOMA INC` data; Yahoo falls back to mock when the crumb handshake is refused from this
environment (by design); private Glenbrook reports "no SEC filings"; renames propagate to
Salesforce/Jira; `/api/prep/cal_002` is enriched with a real WSM 8-K URL.

**Real public-company customers (renamed everywhere — mock data, seed, agent, frontend):**

- [x] Northwind Retail Group → **Williams-Sonoma, Inc.** (NYSE: WSM, CIK 0000719955) — merchant client.
- [x] Atlas Marketplace → **Etsy, Inc.** (Nasdaq: ETSY, CIK 0001370637) — marketplace / RFP prospect.
- [x] Brightline Financial → **Dave Inc.** (Nasdaq: DAVE, CIK 0001841408) — consumer fintech / BaaS partner.
- [x] **Glenbrook Partners stays private** (no ticker / `public: False`) — SEC tool reports "no public
      filings," exercising the private-company path. Fictional contacts kept, moved to the real
      domains (`@williams-sonoma.com`, `@etsy.com`, `@dave.com`); SSIM stays the payments/banking provider.

**Market-intelligence feature:**

- [x] New `backend/server/market_data.py` — **stdlib-only** (`urllib` + `http.cookiejar`, no
      `yfinance`/`pandas`) SEC EDGAR submissions fetch (descriptive `User-Agent`, ~6s timeout) +
      Yahoo Finance quote/news/earnings via the crumb handshake. Per-call try/except → baked-in
      mock fixtures. `SSIM_DISABLE_LIVE_MARKET=1` skips all network → deterministic mock (used by tests/CI).
      *(Deviation from the approved plan, confirmed: stdlib instead of `yfinance` to avoid the pandas
      image-size cost — reflected in `spec.md`.)*
- [x] `store.py` — added `sec_cache` + `stock_cache`, cleared on `reset()`.
- [x] `logic.py` — `_resolve_company`, `_private_response`, `sec_filings`, `stock_snapshot`,
      `public_company_watch`; `briefing_summary` now carries `public_company_watch` (so chat &
      read paths match); `meeting_prep` attaches `stock_snapshot` + `latest_filing` for public clients.
- [x] `tools.py` + `agent.py` — `get_sec_filings` / `get_stock_snapshot` tools added to `ALL_TOOLS`;
      "Market intelligence" bullet in the system prompt; example strings updated to the real names.
- [x] `llm.py` — briefing narrative prompt fed a "public-company customer watch" section
      (earnings-soon / notable latest filing) built from the summary.
- [x] `mock_data.py` — customer content renamed; each public profile extended with
      `ticker/exchange/cik/legal_name/public`; added `TICKER_CIK`, `MOCK_SEC_FILINGS`,
      `MOCK_YAHOO_FINANCE` fallback fixtures.
- [x] `seed.py` — demo Jira issues + Salesforce accounts/opportunities/activities renamed to the
      real companies (Glenbrook unchanged).
- [x] `main.py` — `GET /api/stock/{query}` and `GET /api/sec/{query}` (on-demand); watch + prep
      ride the existing `/api/briefing` and `/api/prep/{id}` endpoints.
- [x] Frontend — `types.ts` (SecFiling/StockSnapshot/PublicCompanyWatch + Briefing/MeetingPrep
      fields), `api.ts` (`stock` / `sec` fetchers), `AssistantTab.tsx` ("Customer market watch"
      card + a stock/latest-filing block in the meeting-prep rows), `Chat.tsx` starters, `styles.css`.

**Automated tests + CI (closes the "no test suite" backlog item):**

- [x] Backend `pytest` suite (42 tests) — `tests/conftest.py` (forces `SSIM_DISABLE_LIVE_MARKET=1`,
      monkeypatches the LLM, `TestClient`) + `test_market_data.py` / `test_logic.py` / `test_api.py`
      / `test_seed.py`. Covers mock fallback, company resolution, public/private/unknown, caching,
      the watch, prep enrichment, write actions, `/api/*` endpoints, and rename sanity (no
      Northwind/Atlas/Brightline/old domains linger). Wired via `[dependency-groups] dev` +
      `[tool.pytest.ini_options]` in `pyproject.toml`.
- [x] Frontend **Vitest** + React Testing Library suite (5 tests) — `richText`, `Chat`,
      `AssistantTab`; jsdom env, `src/test/setup.ts`, test files excluded from the `tsc -b` build.
- [x] `.github/workflows/ci.yml` — runs on `pull_request` + `push` to `main` (concurrency
      cancel-in-progress). **Backend** job: `setup-uv` (py 3.12) → `uv sync --frozen` → `uv run
      pytest` with `SSIM_DISABLE_LIVE_MARKET=1`. **Frontend** job: `setup-node` 20 → `npm ci` →
      `npm run test` → `npm run build`.

## Phase 7 — Google Search stock fallback + narrative/UI polish  ✅ (delivered 2026-07-25)

Follow-up polish after Phase 6: a second live-data tier for stock quotes when Yahoo is down, and
two UI/copy cleanups the user asked for directly (no "mock" label, no "Good morning" greeting).

- [x] `market_data.py` — added `_fetch_google_quote(ticker)` / `_parse_google_quote(html)` /
      `_stock_with_google_quote(ticker, quote)`. `get_stock_snapshot` now tries **Yahoo → Google
      Search scrape → mock**, in that order: if Yahoo's crumb handshake fails, it scrapes a live
      price/change/change_pct off Google's search results answer-box HTML (stdlib `urllib`, no
      API key) and layers that real price/move onto otherwise-mock company/exchange/earnings/news
      metadata, tagged `source: "live"`. Best-effort only — Google's markup is undocumented and
      can change or serve a consent interstitial without notice, so failures silently fall
      through to full mock; `SSIM_DISABLE_LIVE_MARKET=1` skips this tier too (tests/CI unaffected).
- [x] Added 7 new backend tests (`test_market_data.py`, now 49 total): pure-parser tests against
      canned Google answer-box HTML (with/without a move, and unrecognized markup → `None`), a
      network-error test for `_fetch_google_quote`, `_stock_with_google_quote`'s metadata-layering,
      and `get_stock_snapshot`'s full Yahoo→Google→mock fallback chain (monkeypatched, no real
      network calls — stays hermetic).
- [x] Removed the `MOCK`/`LIVE` provenance pill from the UI entirely — `AssistantTab.tsx`'s
      `MarketWatchCard` and the meeting-prep "Market snapshot" block now show only the data
      (price, move, earnings date, filing), not its source; the API/data layer still tags every
      response `source: "live"|"mock"` internally (kept for tests/debugging). Deleted the
      now-unused `.src-tag`/`.src-tag.live`/`.src-tag.mock` rules from `styles.css`, and updated
      `AssistantTab.test.tsx` to assert the tag text is absent.
- [x] Removed the "Good morning" greeting from the daily-briefing narrative: the Gemini prompt in
      `llm.py` now explicitly instructs "do NOT open with a greeting ... start directly with the
      substance of the day," and the composed no-Vertex fallback string was reworded to match
      (`**You have N meetings** today...` instead of `**Good morning.** You have...`).
- [x] `mock_data.py` — removed `dev@chenkeamonwang.altostrat.com` (the app's own "you" persona)
      from every `MOCK_CALENDAR_EVENTS[*].attendees` and `MOCK_MEETING_SUGGESTIONS[*]
      .suggested_attendees` list (10 lines, all bare-string array entries), since listing the
      viewer as an attendee of their own meetings reads as a mock-data artifact. Left untouched:
      `OWNER_EMAIL` in `logic.py`, the mailbox-owner `"to"` field on every `MOCK_EMAILS` entry,
      and the `MOCK_EMPLOYEE_LOCATIONS` directory entry — none of those are attendee lists.
      Verified: `uv run pytest` still 49/49 (no test asserted the old attendee counts); room
      assignment and meeting-prep endpoints re-verified live with the new (smaller) attendee
      lists — no errors, no UI text still refers to the removed address.

---

## Phase 8 — company rebrand: SSIM / State Street → FinTechCo  ✅ (delivered 2026-07-25)

- [x] Renamed the fictional company brand from "State Street Investment Management (SSIM)" to
      **FinTechCo** everywhere it is displayed in the app or its mock content, per user request
      (this reverses the Phase 5 decision to keep the brand unchanged). Internal-only Python
      identifiers were deliberately left as-is (not user-visible): the `ssim_relationship` /
      `ssim_aum` / `ssim_payments_banking_snapshot` dict keys in `mock_data.py`/`llm.py`/
      frontend, the `ssim_assistant` ADK agent/app name and logger in `agent.py`/`main.py`, the
      `SSIM_DISABLE_LIVE_MARKET` env var, and module docstrings/comments.
  - **Frontend:** `index.html` tab title, `App.tsx` header brand + subtitle, `Chat.tsx` panel
    header, `JiraPage.tsx` project name/crumb/board title/avatar initials ("SS" → "FT"),
    `AssistantTab.tsx` client-profile "with SSIM" label.
  - **Backend mock data (`mock_data.py`):** every displayed "SSIM" occurrence in email
    subjects/snippets, Drive document names/content, and customer `relationship_manager` /
    `primary_contact` fields → "FinTechCo"; module comments updated for consistency.
  - **Jira demo data (`seed.py`):** project code `SSIM` → `FTC`, issue keys `SSIM-101..105` →
    `FTC-101..105`; matching references updated in `agent.py`'s system prompt and `tools.py`'s
    `create_jira_tasks` docstring so the concierge agent creates new tasks under the same code.
  - **LLM prompts (`agent.py`, `llm.py`):** system prompt and the daily-briefing / meeting-prep
    generation prompts now refer to "FinTechCo" instead of "SSIM" / "State Street Investment
    Management," since this text can surface directly in chat replies and the briefing
    narrative.
  - **Attendee/employee email domain:** `@statestreet.com` → `@fintechco.com` across
    `MOCK_CALENDAR_EVENTS` attendees, `MOCK_EMAILS` from/to, `MOCK_EMPLOYEE_LOCATIONS`,
    `MOCK_ROOM_BOOKINGS` organizers, and `MOCK_MEETING_SUGGESTIONS` attendees (29 addresses).
  - **Tests:** `test_logic.py`'s `create_jira_tasks` test now passes `"FTC"` as the project code.
  - Verified: `python -m ast` syntax-checked all edited backend files; loaded `seed.build_seed()`
    directly and confirmed the Jira project is `FTC` with `FTC-10x` keys, attendee/email domains
    are `fintechco.com` (no `statestreet.com` left), and a full JSON dump of the seed contains no
    "SSIM" or "State Street" substring. `npm run build` (tsc + vite) passed clean.

---

## Phase 9 — SpaceX index-inclusion analytics dashboard  🎬 (demo starting point on this branch)

> This branch (`demo/spacex-live-build-start`) is a **deliberately incomplete** starting point
> for a timed live-build demo — see the "15-minute demo" plan captured 2026-07-29. The fully
> built, tested, and documented version (everything below, as `[x]`) lives on
> `feature/spacex-analytics-dashboard`; that branch's `implementation.md` has the full write-up.
>
> **Kept on this branch** (reusable infra + pre-verified real data, so the live build has
> nothing to research and nothing to fetch over the network):
> - `backend/server/spacex_reference_data.py` — real IPO/index-inclusion timeline, SPCX/Nasdaq-100
>   price history, curated SEC filings (all captured live on 2026-07-28).
> - `backend/server/fred_data.py`, `market_data.get_price_history()` — generic, already reusable.
> - `frontend/src/components/IndexedPriceChart.tsx` — generic 2-series indexed chart, built per
>   the `dataviz` skill (validated color pair `#2a78d6`/`#eb6834`, hover tooltip, table view).
> - `frontend/src/lib/caseStudyReportPdf.ts` — generic client-side PDF report generator (`jspdf`).
> - The FinTechCo rebrand (Phase 8) underneath it all.
>
> **Removed, to be rebuilt live:** `backend/server/spacex_case_study.py` (event-study metrics +
> insights + bank-impact business logic), the `/api/spacex-analytics` endpoint and its store
> caching, `llm.generate_spacex_narrative`, and `frontend/src/pages/SpacexAnalyticsPage.tsx`
> (+ its `#/spacex` route/nav button and the `SpacexAnalytics`/`PriceSeries`/etc. types).
> Regression-checked after removal: 49/49 backend tests, 5/5 frontend tests, both builds clean.

## Backlog / tech debt

- Legal/brand review of the real competitor names retained in `backend/server/mock_data.py`
  (Stripe, Adyen, Fiserv, Block/Square) before any external-facing demo — mirrors the prior use
  of real asset-manager competitor names, but worth a sign-off given the new industry.
- Sweep for any stray asset-management terms (AUM, mandate, ESG, SFDR, MiFID, AIFMD, pension,
  sovereign wealth, securities lending) that the re-theme missed, in the remaining tree
  (`backend/server/*.py`, `frontend/src/*`, docs).
- `customer_profile.ssim_relationship.ssim_aum` / `.strategies` keys (per client, in
  `backend/server/mock_data.py`) were intentionally left named as-is even though their values
  now describe payment volume/deposits and products/services rather than AUM/investment
  strategies — renaming them would require touching `server/llm.py` and the mock data together;
  revisit if the stale key names cause confusion.
- Concierge is a single agent with all tools; promote to agent-as-tool / `sub_agents` routing
  as specialists are onboarded.
- Backend store is in-process (single-instance); the deployed Cloud Run service is capped at
  `--max-instances=1` as a stopgap. For multi-instance Cloud Run, persist to a datastore.
- Transient model `400 INVALID_ARGUMENT` is not auto-retried by ADK — monitor; add handling
  if it recurs in the deployed backend.
- **Yahoo crumb fragility:** the Yahoo Finance quote/news path depends on a cookie+crumb
  handshake that is intermittently refused from some egress environments (observed falling back
  to mock from this dev box). Mitigated for price/move by the Phase 7 Google Search fallback tier,
  but next-earnings-date and headlines still have no second live source and fall straight to mock
  when Yahoo is down.
- **Google Search scrape fragility (Phase 7):** `_fetch_google_quote`/`_parse_google_quote`
  depend on undocumented, unversioned Google SERP markup (the "BNeawe" answer-box classes) —
  Google can change this layout, rate-limit/block server-side requests, or serve a
  cookie-consent interstitial at any time, with no warning and no contract. It's a convenience
  best-effort tier for a demo, not something to depend on for a real production surface; a
  paid quote API (e.g. Yahoo with an API key, IEX Cloud, Alpha Vantage) would be the durable fix.
- **Verify/refresh CIKs periodically:** `TICKER_CIK` (WSM 0000719955, ETSY 0001370637,
  DAVE 0001841408) is hardcoded in `mock_data.py`; re-check against
  `https://www.sec.gov/files/company_tickers.json` if a ticker ever resolves to empty filings.
- **Cloud Run egress must stay open** for the live SEC/Yahoo fetches to work in the deployed
  service; otherwise everything silently serves mock. If locking egress down, set
  `SSIM_DISABLE_LIVE_MARKET=1` explicitly so the intent is clear.
- **CI runs hermetically (no live Vertex/market calls):** the LLM is monkeypatched and
  `SSIM_DISABLE_LIVE_MARKET=1` in CI, so narrative/prep generation and live filings/quotes are
  *not* exercised in CI. A real Vertex-in-CI smoke/eval (gated on ADC) is a roadmap item.
- Legal/brand review of the real **customer** company names now baked into `mock_data.py`
  (Williams-Sonoma, Etsy, Dave) — same sign-off concern as the retained competitor names below.

*Resolved by the Phase 5.2 slim-down (were open while the standalone agents existed):*
room-assignment logic duplicated across the agents + the webapp (now a single copy in
`backend/server/logic.py`); migrating `meeting_room`/`proj_ma`/`rfp`/`sales` to Agent Runtime;
and per-agent `test_dummy.py` placeholders — all moot now that the agents are removed.

## How to use this doc

1. Before coding, find or add the item here.
2. As work lands, flip `[ ]`→`[x]` (or `[~]`), and update `prd.md`/`spec.md` per CLAUDE.md.
3. File new discoveries under Backlog. Bump the Version/Date header on substantive edits.
