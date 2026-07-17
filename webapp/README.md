# SSIM Employee Digital Assistant — Web App (local demo)

A tabbed web app over the SSIM agents, plus interactive **mock Jira** and **mock Salesforce**
boards that update live when the assistant acts.

```
webapp/
├── backend/    # FastAPI + ADK concierge agent + shared in-process store
└── frontend/   # React + Vite + TypeScript (4 tabs)
```

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

**1. Backend** (needs Google ADC for Vertex; uses `gemini-3.5-flash` in the `us` region):

```bash
cd webapp/backend
uv sync
gcloud auth application-default login   # if not already authenticated
uv run uvicorn server.main:app --reload --port 8000
```

**2. Frontend:**

```bash
cd webapp/frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The Vite dev server proxies `/api/*` to the backend on
`:8000`. Use **Reset demo** (top-right) to restore the seed state.

## Notes

- The SSIM domain data (calendar, emails, rooms, seats, Drive docs, customer profiles) is
  loaded from `daily_briefing/app/mock_data.py` so the app stays in sync with the agent.
  Jira / Salesforce state is demo-only (`backend/server/seed.py`).
- Read endpoints work without Vertex credentials; only the chat needs Vertex access.
- Model note: `gemini-2.0-flash-001` 404s at `global` for this project; `gemini-3.5-flash`
  is served from the `us` multi-region (404s in `us-central1`/`us-east4`). All agents +
  backend are set to `gemini-3.5-flash` @ `us`.

## Later: deployment (approval-gated)

- Agents → Agent Engine: `agents-cli deploy` in `meeting_room/` and `daily_briefing/`.
- Web app → Cloud Run: containerize `backend` (FastAPI) and serve the built `frontend`.
