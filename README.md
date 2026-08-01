# FinTechCo Employee Digital Assistant — Web App

A tabbed web app for a FinTechCo employee, plus interactive
**mock Jira** and **mock Salesforce** boards that update live when the assistant acts. It pairs
a FastAPI backend running an in-process ADK **concierge agent** with a React + Vite + TypeScript
frontend.

```
backend/    # FastAPI + ADK concierge agent + shared in-process store (package: server)
frontend/   # React + Vite + TypeScript (4 tabs)
```

> 📦 This repo ships **only the web app**. It began as a set of 6 standalone ADK agents
> (daily briefing, meeting prep, meeting rooms, project management, RFP, sales) — those were
> removed from source once the concierge agent reproduced their user-facing capabilities. Their
> design/vision is retained in [`prd.md`](prd.md) / [`spec.md`](spec.md).

## Tabs / user journeys

- **AI Assistant** — concierge chat + Daily Briefing dashboard (today's schedule with an
  expandable per-meeting **prep** view, and **Suggested Meetings** each with a **Schedule**
  button that auto-books a room via the meeting-room logic).
- **Meeting Rooms** — room inventory, today's bookings, and the seat directory used for
  proximity-based assignment.
- **Jira** — kanban board (To Do / In Progress / Done).
- **Salesforce** — accounts, opportunity pipeline, and an activity timeline.

Ask the assistant to book a room, create Jira tasks, or log Salesforce activity, then switch
tabs — the boards reflect the change (new items briefly highlight).

## Run it (two terminals)

**1. Backend** (chat uses Claude Haiku 4.5 via the Anthropic API — set `ANTHROPIC_API_KEY` in
`backend/.env`; read endpoints work without it):

```bash
cd backend
uv sync
uv run uvicorn server.main:app --reload --port 8000
```

**2. Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The Vite dev server proxies `/api/*` to the backend on
`:8000`. Use **Reset demo** (top-right) to restore the seed state.

## Notes

- The FinTechCo domain data (calendar, emails, rooms, seats, Drive docs, customer profiles) is
  the single source of truth in `backend/server/mock_data.py`, loaded via `backend/server/seed.py`.
  Jira / Salesforce state is demo-only (also in `seed.py`).
- Read endpoints work without an Anthropic API key; only the chat needs it.

## Deployment (approval-gated)

Web app → Cloud Run: the root `Dockerfile` builds `frontend` and serves the built SPA from the
FastAPI `backend` as one combined service. See [`spec.md`](spec.md) §11.
