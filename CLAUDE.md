# CLAUDE.md — SSIM Employee Digital Assistant

Project guidance for Claude Code working in this repo. These instructions override default
behavior; follow them exactly.

## What this repo is

The **SSIM Employee Digital Assistant**: a set of Google ADK agents for State Street
Investment Management (~$4.1T AUM, institutional) plus a concierge web app that unifies them.
See the doc chain below for the full picture.

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
daily_briefing/ meeting_prep/ meeting_room/ proj_ma/ rfp/ sales/   # 6 ADK agents (deployable)
  app/{agent.py, mock_data.py, agent_engine_app.py, app_utils/}  tests/  pyproject.toml
webapp/
  backend/  server/{main,agent,tools,logic,store,seed}.py         # FastAPI + concierge agent
  frontend/ src/{App,api,types}.tsx  src/{tabs,components,hooks}   # React + Vite + TS (4 tabs)
```

## Conventions (match existing code exactly)

- **Agents:** each folder is self-contained and independently deployable. Tools are plain
  functions returning **JSON strings** with a `try:` real-Google-API path and an `except:`
  mock fallback tagged `"source": "mock"`. Expose `root_agent = Agent(...)` and
  `app = App(root_agent=..., name=...)`.
- **System prompts:** Markdown, and use `[Variable]` placeholders — never `{Variable}` (ADK
  reads `{...}` as session-state lookups).
- **Write actions** (schedule/book/create Jira/log Salesforce): confirm before writing.
- **File headers:** keep the `# ruff: noqa` + Apache license header on agent files.
- **Domain mock data has a single source of truth:** `daily_briefing/app/mock_data.py`. The
  webapp backend loads it (via `server/seed.py`); don't fork it — extend it there.

## Model / Vertex config (important)

- Model: **`gemini-3.5-flash`**; location: **`GOOGLE_CLOUD_LOCATION="us"`** (US multi-region);
  `GOOGLE_GENAI_USE_VERTEXAI="True"`; project from `google.auth.default()` (`logical-vim-478515-b1`).
- **Do not** use `gemini-2.0-flash-001` (404 for this project) or `global`/`us-central1` for
  `gemini-3.5-flash` (429 / 404 respectively). Details in memory `vertex-gemini-model-availability`.
- Don't change the model without being asked; if a 404 appears, check location before the model.

## Run it locally

- **An agent in isolation:** `cd <agent> && agents-cli install && agents-cli dev`.
- **Web app:** backend `cd webapp/backend && uv run uvicorn server.main:app --reload --port 8000`;
  frontend `cd webapp/frontend && npm install && npm run dev` → http://localhost:5173
  (Vite proxies `/api` → :8000). Chat needs Vertex ADC; read endpoints don't.

## Testing

- Agents: `agents-cli test` (unit + integration in `tests/`); `agents-cli eval` for evalsets.
- Frontend: `npm run build` (tsc + vite) is the smoke gate.
- Verify runtime behavior end-to-end (drive the flow), not just imports, for nontrivial changes.

## Deployment (approval-gated)

Never deploy without explicit user approval. Agents → Agent Engine via `agents-cli deploy`
(run in the agent folder). Web app → Cloud Run (see `spec.md` §11). Existing agents were
deployed in `us-central1`; re-deploy after the model change.

## Operational notes

- Use `uv` for Python (`uv run …`, `uv sync`); `npm` for the frontend.
- Prefer editing over rewriting; preserve surrounding code, comments, and config.
- If the same error recurs 3+ times, fix the root cause instead of retrying.

## Source control

- GitHub: [chenw-google/ai_assistant](https://github.com/chenw-google/ai_assistant) — remote
  `origin`, single branch `main`. Push here when asked to sync/push changes.
- Every agent folder + `webapp/backend` + `webapp/frontend` has its own `.gitignore`
  (`.venv`/`node_modules`/build output); when staging new folders, add them directly rather
  than `git add -A` so those ignores are respected and nothing large or generated slips in.
