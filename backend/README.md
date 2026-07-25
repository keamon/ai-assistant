# SSIM Assistant — Backend

FastAPI backend for the SSIM Employee Digital Assistant demo. It runs a single ADK
concierge agent locally (Vertex AI, `gemini-2.0-flash-001`) whose tools read and write a
shared in-process store. Because the store is shared, an assistant action (booking a room,
creating Jira tasks, logging Salesforce activity) is immediately visible on the other tabs.

## Run locally

```bash
uv sync                      # install deps
gcloud auth application-default login   # if not already authenticated (for Vertex)
uv run uvicorn server.main:app --reload --port 8000
```

Read endpoints (`/api/briefing`, `/api/rooms`, `/api/jira`, `/api/salesforce`, ...) work even
without Vertex credentials; only the chat endpoint (`/api/assistant`) needs Vertex access.

## API

| Method | Path | Purpose |
| ------ | ---- | ------- |
| POST | `/api/assistant` | Chat turn `{message, session_id?}` → `{reply, session_id}` |
| GET | `/api/briefing` | Today's schedule, priority emails, market, suggestions |
| GET | `/api/prep/{event_id}` | Full prep brief for a meeting |
| POST | `/api/schedule` | Create event + auto-book a room (Schedule button) |
| GET | `/api/rooms` | Rooms, bookings, seat directory |
| GET | `/api/calendar` | Calendar events |
| GET | `/api/jira` | Jira board (columns + issues) |
| GET | `/api/salesforce` | Accounts, opportunities, activities |
| POST | `/api/reset` | Reset the demo store |
| GET | `/api/health` | Health check |

## Deploy

Cloud Run: single combined service built from the repo-root `Dockerfile` (bundles the built
frontend into this backend's image, served same-origin). See `spec.md` §11 for the deploy
command and IAM/scaling settings.

The SSIM domain data (calendar, emails, rooms, seats, Drive docs, customer profiles) is
loaded from `daily_briefing/app/mock_data.py` so the demo never drifts from the agent.
Jira and Salesforce state are demo-only (`server/seed.py`).
