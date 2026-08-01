# Copyright 2026 FinTechCo
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""FastAPI app for the FinTechCo assistant demo: chat endpoint (ADK) + store reads."""

import logging
import uuid
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from server import llm, logic
from server.store import STORE

logger = logging.getLogger("concierge_assistant")

app = FastAPI(title="FinTechCo Employee Digital Assistant — Demo API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── ADK runner (lazy so the read endpoints work even without model creds) ──

_RUNNER = None
_SESSIONS: dict[str, str] = {}
APP_NAME = "concierge_assistant"
USER_ID = "demo_user"


def _get_runner():
    global _RUNNER
    if _RUNNER is None:
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService

        from server.agent import root_agent

        _get_runner.session_service = InMemorySessionService()
        _RUNNER = Runner(
            agent=root_agent, app_name=APP_NAME,
            session_service=_get_runner.session_service,
        )
    return _RUNNER


def _run_turn(session_id: str, message: str) -> str:
    from google.genai import types

    runner = _get_runner()
    if session_id not in _SESSIONS:
        s = _get_runner.session_service.create_session_sync(
            app_name=APP_NAME, user_id=USER_ID
        )
        _SESSIONS[session_id] = s.id
    adk_sid = _SESSIONS[session_id]
    content = types.Content(role="user", parts=[types.Part.from_text(text=message)])
    reply = ""
    for event in runner.run(user_id=USER_ID, session_id=adk_sid, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            txt = "".join(p.text for p in event.content.parts if getattr(p, "text", None))
            if txt:
                reply = txt
    return reply.strip()


# ─── Schemas ────────────────────────────────────────────────────────────────

class AssistantRequest(BaseModel):
    message: str
    session_id: str | None = None


class ScheduleRequest(BaseModel):
    title: str
    attendees: list[str]
    date: str
    start_time: str
    end_time: str
    room_id: str | None = None


class AssignRoomRequest(BaseModel):
    attendees: list[str]
    date: str
    start_time: str
    end_time: str


class AvailableRoomsRequest(BaseModel):
    attendees: list[str] = []
    date: str
    start_time: str
    end_time: str


# ─── Chat ───────────────────────────────────────────────────────────────────

@app.post("/api/assistant")
def assistant(req: AssistantRequest) -> dict:
    session_id = req.session_id or str(uuid.uuid4())
    try:
        reply = _run_turn(session_id, req.message)
    except Exception as exc:  # keep the UI usable if the model backend is unavailable
        logger.exception("assistant turn failed")
        reply = f"⚠️ The assistant backend hit an error: {exc}"
    if not reply:
        # ADK logs model errors (e.g. a transient 400) and ends the turn without a
        # final response; surface a friendly retry instead of an empty bubble.
        reply = "⚠️ I didn't get a response from the model just now (possibly a transient error). Please try again."
    return {"session_id": session_id, "reply": reply}


# ─── Store reads (for the tabs; also used for polling) ───────────────────────

@app.get("/api/briefing")
def briefing() -> dict:
    summary = logic.briefing_summary(STORE)
    if STORE.briefing_narrative is None:
        STORE.briefing_narrative = llm.generate_briefing_narrative(summary)
    summary["narrative"] = STORE.briefing_narrative
    return summary


@app.get("/api/prep/{event_id}")
def prep(event_id: str) -> dict:
    data = logic.meeting_prep(STORE, event_id=event_id)
    if data.get("error"):
        return data
    if event_id not in STORE.prep_cache:
        STORE.prep_cache[event_id] = llm.generate_meeting_prep(data)
    data.update(STORE.prep_cache[event_id])
    return data


@app.post("/api/assign-room")
def assign_room(req: AssignRoomRequest) -> dict:
    """Preview the best-fit room WITHOUT booking (for the schedule widget)."""
    return logic.assign_room(STORE, req.attendees, req.date, req.start_time, req.end_time)


@app.post("/api/available-rooms")
def available_rooms(req: AvailableRoomsRequest) -> dict:
    """List every room free in the window (for the schedule widget's room dropdown)."""
    rooms = logic.list_available_rooms(STORE, req.date, req.start_time, req.end_time)
    return {"available_rooms": rooms}


@app.get("/api/stock/{query}")
def stock(query: str) -> dict:
    """Live stock snapshot (quote, next earnings, news) for a public-company customer."""
    return logic.stock_snapshot(STORE, query)


@app.get("/api/sec/{query}")
def sec(query: str, form_type: str = "") -> dict:
    """Recent SEC EDGAR filings (10-K / 10-Q / 8-K) for a public-company customer."""
    return logic.sec_filings(STORE, query, form_type)


@app.get("/api/doc/{doc_id}")
def doc(doc_id: str) -> dict:
    return logic.get_doc(STORE, doc_id)


@app.post("/api/schedule")
def schedule(req: ScheduleRequest) -> dict:
    return logic.schedule_meeting(
        STORE, req.title, req.attendees, req.date, req.start_time, req.end_time, req.room_id
    )


@app.get("/api/calendar")
def calendar() -> dict:
    return {"date": STORE.date, "events": STORE.calendar_events}


@app.get("/api/jira")
def jira() -> dict:
    return STORE.jira


@app.get("/api/salesforce")
def salesforce() -> dict:
    return STORE.salesforce


@app.post("/api/reset")
def reset() -> dict:
    STORE.reset()
    _SESSIONS.clear()
    return {"reset": True, "date": STORE.date}


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "fintechco-assistant", "date": STORE.date}


# ─── Static frontend (deployed container only; see README.md) ─

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if _STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="static")
