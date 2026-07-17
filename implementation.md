# SSIM Employee Digital Assistant — Implementation Plan & Checklist

> Status: Living document · Version 0.8 · Date: 2026-07-17
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

### C. Web app backend (`webapp/backend`, package `server`)
- [x] `store.py` shared mutable `STORE` + `reset()`
- [x] `seed.py` loads `daily_briefing/app/mock_data.py` by path (single source of truth) + demo Jira/Salesforce
- [x] `logic.py` pure functions (rooms, briefing, suggestions, prep, schedule, jira, salesforce)
- [x] `tools.py` ADK tool wrappers (scalar/string args for reliable function-calling)
- [x] `agent.py` concierge Agent (all tools) — `gemini-3.5-flash`@`us`
- [x] `main.py` FastAPI: `/api/assistant` (lazy Runner) + read endpoints + `/api/schedule` + `/api/reset`
- [x] Graceful empty/error reply fallback
- [x] `pyproject.toml`, `uv sync`, endpoint + chat smoke tests (Jira & Salesforce writes verified)
- [ ] FastAPI TestClient integration tests

### D. Web app frontend (`webapp/frontend`, React+Vite+TS)
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
- [ ] `.gitignore` review for `webapp/` (`node_modules`, `.venv`, `dist`, `__pycache__`)

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

- [ ] Deploy `meeting_room` and updated `daily_briefing` to Agent Engine (`agents-cli deploy`) — **needs approval**
- [x] Containerize `webapp/backend` (FastAPI) → Cloud Run — single combined service, root
      `Dockerfile`; see `spec.md` §11
- [x] Build + serve `webapp/frontend` (static) → Cloud Run — bundled into the backend image and
      served same-origin by FastAPI, so the "tighten CORS to deployed origin" item is moot
      (no cross-origin requests left to tighten)
- [ ] **Compliance & Regulatory agent** (gates RFP/Sales drafts) — new agent + UI compliance badge
- [ ] **Post-Meeting / Follow-up agent** (writes CRM/Jira/next-day briefing) — closes the loop
- [ ] Surface Project Mgmt & Sales journeys in the concierge (add their tools/tabs)

## Phase 3 — research + real data  ⏳

- [ ] **Investment Research / Market Intelligence agent**
- [ ] Real integrations behind existing tool contracts (Gmail/Calendar/Drive, then Jira/Salesforce)
- [ ] Per-employee OAuth identity + scoped access; authz on writes; audit trail
- [ ] Shared CRM/Jira **service layer** replacing per-agent mocks
- [ ] Eval-in-CI + observability dashboards

## Phase 4 — broader employee agents  ⏳

- [ ] Client Reporting / review-pack generator; Knowledge/Policy (HR/IT) Q&A
- [ ] IT helpdesk; Expense & Travel; New-hire onboarding

---

## Backlog / tech debt

- Room-assignment logic is duplicated across `meeting_room/`, `daily_briefing/`, and
  `webapp/backend/server/logic.py` (deployability > DRY for v1). Consolidate when a shared
  service layer exists.
- Concierge is a single agent with all tools; promote to agent-as-tool / `sub_agents` routing
  as specialists are onboarded.
- Backend store is in-process (single-instance); the deployed Cloud Run service is capped at
  `--max-instances=1` as a stopgap. For multi-instance Cloud Run, persist to a datastore.
- Replace `test_dummy.py` placeholders with real unit tests across agents.
- Transient model `400 INVALID_ARGUMENT` is not auto-retried by ADK — monitor; add handling
  if it recurs in the deployed backend.

## How to use this doc

1. Before coding, find or add the item here.
2. As work lands, flip `[ ]`→`[x]` (or `[~]`), and update `prd.md`/`spec.md` per CLAUDE.md.
3. File new discoveries under Backlog. Bump the Version/Date header on substantive edits.
