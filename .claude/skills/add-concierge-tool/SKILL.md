---
name: add-concierge-tool
description: Scaffold a new tool for the FinTechCo concierge agent (backend/server/logic.py + tools.py + agent.py registration), following this repo's exact ADK tool conventions, then flag the prd.md/spec.md/implementation.md updates the golden rule requires. Use when adding a new capability, action, or data lookup to the concierge agent.
---

# Add a concierge tool

This repo has one ADK agent (`backend/server/agent.py`) whose tools are plain functions in
`backend/server/tools.py`. Every tool follows the same shape; don't invent a new one. See
`CLAUDE.md` → "Conventions" for the full rationale.

## Steps

1. **Pure logic in `backend/server/logic.py`.** Add a plain function `fn(store, ...)` that
   reads/writes the shared in-process `Store` (`backend/server/store.py`) and returns plain
   Python data (dict/list) — no JSON encoding here, no ADK types. If the tool needs new domain
   data, add it to `backend/server/mock_data.py` (the single source of truth — never fork data
   into `logic.py` or `seed.py` directly). `seed.py` deep-copies `mock_data.py` and layers on
   demo-only Jira/Salesforce state; extend `mock_data.py` if the new data belongs there.

2. **Wrapper in `backend/server/tools.py`.** Add a thin plain function (this is what the ADK
   agent calls) that calls the `logic.py` function and returns
   `json.dumps(result, indent=2, default=str)` — tools return **JSON strings**, not dicts. Most
   tools stop here; the docstring's first line is what the agent sees, so state clearly what the
   tool does and, for a **write action** (schedule/book/create Jira/log Salesforce), tag it
   `(WRITE — confirm first)` like `schedule_meeting`/`create_jira_tasks`/
   `log_salesforce_activity`/`update_opportunity` do — the agent's system prompt (see step 3)
   is what actually enforces confirming with the user before calling it.

   **Only if the tool depends on a live external data source** (as `get_sec_filings` /
   `get_stock_snapshot` do for SEC EDGAR / Yahoo Finance), add a fetch function in
   `market_data.py` (or a sibling data module) that `try:`s the live call and `except:`s to a
   mock builder, tagging the result `"source": "live"` or `"source": "mock"` — follow that
   file's existing pattern exactly, including caching the result on the `Store` (see
   `store.sec_cache` / `store.stock_cache`) so repeated calls in one session don't re-fetch.

3. **Register in `backend/server/agent.py`.**
   - Add the new tool to the agent's tool list.
   - Update the system prompt to describe when to use it. System prompts are Markdown and use
     `[Variable]` placeholders — **never** `{Variable}` (ADK reads `{...}` as a session-state
     lookup and will error or silently misbehave).

4. **File header.** If the new/edited backend file already carries the Apache license header,
   keep it. Don't strip it, don't add it to files that never had it.

5. **Docs — required, same session (CLAUDE.md golden rule):**
   - New/changed user-facing capability → update `prd.md`.
   - New tool / data contract / API surface → update `spec.md` (tool list, data contracts).
   - Any code change → tick/append the item in `implementation.md`'s build checklist, and add
     follow-ups to its backlog if any surfaced. Bump the doc's `Version`/`Date` header.
   - If a doc and the new code disagree, fix the doc — don't leave it stale.

6. **Verify end-to-end**, not just import-clean:
   - `cd backend && uv run pytest` (add/extend a test in `backend/tests/` for the new logic
     function if one doesn't already cover it).
   - Drive it live: `uv run uvicorn server.main:app --reload --port 8000`, then exercise the new
     tool through the chat endpoint (or the matching read endpoint) and confirm the mock
     fallback triggers correctly when forced (e.g. by making the live path raise).
   - `cd frontend && npm run build` if the frontend surfaces the new data/action.

## Common mistakes this skill exists to prevent

- Returning a dict from a tool instead of a JSON string.
- A live-data tool with no mock fallback (breaks the demo the moment the external dependency is
  unavailable — see `market_data.py` for the pattern to copy).
- `{Variable}` in a system prompt instead of `[Variable]` (ADK session-state collision).
- Forking mock data into `logic.py`/`seed.py` instead of extending `mock_data.py`.
- Landing the code change without touching `prd.md`/`spec.md`/`implementation.md` in the same
  session.
