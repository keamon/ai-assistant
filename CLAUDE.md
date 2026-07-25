# CLAUDE.md — SSIM Employee Digital Assistant

Project guidance for Claude Code working in this repo. These instructions override default
behavior; follow them exactly.

## What this repo is

The **SSIM Employee Digital Assistant**: a concierge web app for State Street Investment
Management (a digital payments company with a commercial banking division — ~$4.1T annual
payment volume). It's a FastAPI backend running an in-process Google ADK **concierge agent**
plus a React frontend.

> 📦 The project began as **6 standalone ADK agents** (daily briefing, meeting prep, meeting
> rooms, project management, RFP, sales) unified by the web app. Those agents were **removed
> from source** once the concierge agent reproduced their user-facing capabilities; their
> design/vision is retained in the doc chain below (`prd.md` / `spec.md`). The repo now ships
> only `backend/` + `frontend/`.

## 🔴 Golden rule: keep docs in sync with code

The planning docs are the source of truth for intent. **Any change to code must be reflected
in the docs in the same session** — treat the doc update as part of "done". A code change
without the matching doc update is incomplete.

- **New/changed capability, user-facing behavior, scope, requirement, or roadmap item → update [`prd.md`](prd.md).**
- **New/changed agent, tool, API endpoint, data contract, schema, model/config, or architecture → update [`spec.md`](spec.md).**
- **Any code change → tick/append the item in [`implementation.md`](implementation.md)** (the build checklist) and add follow-ups to its backlog.
- Bump the doc `Version`/`Date` header when you make a substantive edit.
- If a code change contradicts a doc, fix the doc (don't leave it stale); if scope is
  genuinely changing, note it in the PRD's scope/roadmap section.

When asked to "change X" in code, the expected deliverable is: **code + prd.md + spec.md +
implementation.md**, consistent with each other.

## Doc chain

```
ideas.md (brainstorm) → prd.md (product requirements) → spec.md (technical spec)
        → implementation.md (build plan + checklist) → code
```

## Repository layout

```
backend/   server/{main,agent,tools,logic,store,seed,mock_data,llm}.py  # FastAPI + concierge agent + seed/mock data
  tests/  pyproject.toml
frontend/  src/{App,api,types}.tsx  src/{tabs,components,pages,hooks}    # React + Vite + TS (4 tabs)
```

(The 6 standalone ADK agent folders were removed — see "What this repo is" above.)

## Conventions (match existing code exactly)

- **Concierge agent:** the backend exposes one ADK agent (`backend/server/agent.py`) whose
  tools (`server/tools.py`) are plain functions returning **JSON strings**, delegating to pure
  functions in `server/logic.py` over a shared in-process `Store` (`server/store.py`). Chat and
  read-endpoint paths call the same logic so they behave identically.
- **System prompts:** Markdown, and use `[Variable]` placeholders — never `{Variable}` (ADK
  reads `{...}` as session-state lookups).
- **Write actions** (schedule/book/create Jira/log Salesforce): confirm before writing.
- **File headers:** keep the Apache license header on backend files that already carry it.
- **Domain mock data has a single source of truth:** `backend/server/mock_data.py` (imports
  only `datetime`). `server/seed.py` imports it, deep-copies it, and adds demo-only Jira /
  Salesforce state; don't fork the domain data — extend it in `mock_data.py`.
- *(Historical, for reference:)* the removed standalone agents were each self-contained and
  independently deployable, exposing `root_agent = Agent(...)` / `app = App(...)` with the same
  JSON-string + `try:`/`except:` mock-fallback (`"source": "mock"`) tool pattern the concierge
  agent still follows.

## Model / Vertex config (important)

- Model: **`gemini-3.5-flash`**; location: **`GOOGLE_CLOUD_LOCATION="us"`** (US multi-region);
  `GOOGLE_GENAI_USE_VERTEXAI="True"`; project from `google.auth.default()` (`logical-vim-478515-b1`).
- **Do not** use `gemini-2.0-flash-001` (404 for this project) or `global`/`us-central1` for
  `gemini-3.5-flash` (429 / 404 respectively). Details in memory `vertex-gemini-model-availability`.
- Don't change the model without being asked; if a 404 appears, check location before the model.

## Run it locally

- **Web app:** backend `cd backend && uv run uvicorn server.main:app --reload --port 8000`;
  frontend `cd frontend && npm install && npm run dev` → http://localhost:5173
  (Vite proxies `/api` → :8000). Chat needs Vertex ADC; read endpoints don't.

## Testing

- Frontend: `npm run build` (tsc + vite) is the smoke gate.
- Backend has no unit-test suite yet (backlog); verify by driving the live API
  (`uvicorn` + `curl /api/health`, `/api/reset`, `/api/briefing`).
- Verify runtime behavior end-to-end (drive the flow), not just imports, for nontrivial changes.

## Deployment (approval-gated)

Never deploy without explicit user approval. Web app → Cloud Run: the root `Dockerfile`
builds `frontend` and serves the built SPA from the FastAPI `backend` as one combined service
(see `spec.md` §11).

## Operational notes

- Use `uv` for Python (`uv run …`, `uv sync`); `npm` for the frontend.
- Prefer editing over rewriting; preserve surrounding code, comments, and config.
- If the same error recurs 3+ times, fix the root cause instead of retrying.

## Source control

- GitHub: [chenw-google/ai_assistant](https://github.com/chenw-google/ai_assistant) — remote
  `origin`, single branch `main`. Push here when asked to sync/push changes.
- `backend` and `frontend` each have their own `.gitignore`
  (`.venv`/`node_modules`/build output); when staging new folders, add them directly rather
  than `git add -A` so those ignores are respected and nothing large or generated slips in.
