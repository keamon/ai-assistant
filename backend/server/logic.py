# Copyright 2026 Google LLC
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

"""
Pure business logic over a :class:`server.store.Store`. Shared by the ADK agent
tools (:mod:`server.tools`) and the FastAPI read endpoints (:mod:`server.main`)
so behaviour is identical whether triggered by chat or by a UI button.
"""

import datetime
from zoneinfo import ZoneInfo

EASTERN = ZoneInfo("America/New_York")
OWNER_EMAIL = "dev@chenkeamonwang.altostrat.com"
_INTERNAL_DOMAINS = ("chenkeamonwang.altostrat.com", "statestreet.com")


# ─── datetime + room helpers ────────────────────────────────────────────────

def to_dt(date: str, time_str: str) -> datetime.datetime:
    time_part = time_str.strip()
    if "T" in time_part:
        time_part = time_part.split("T", 1)[1]
    time_part = time_part[:8] if len(time_part) >= 8 else time_part[:5]
    fmt = "%H:%M:%S" if time_part.count(":") == 2 else "%H:%M"
    t = datetime.datetime.strptime(time_part, fmt).time()
    d = datetime.date.fromisoformat(date)
    return datetime.datetime(d.year, d.month, d.day, t.hour, t.minute, tzinfo=EASTERN)


def _room_free(store, room_id, date, start, end) -> bool:
    for bk in store.room_bookings:
        if bk.get("room_id") != room_id or bk.get("date") != date:
            continue
        try:
            b_start = datetime.datetime.fromisoformat(bk["start"])
            b_end = datetime.datetime.fromisoformat(bk["end"])
        except Exception:
            continue
        if start < b_end and b_start < end:
            return False
    return True


def _seat_for(store, email):
    email = email.strip().lower()
    for loc in store.employee_locations:
        if loc["email"].lower() == email:
            return loc
    return None


def _room_penalty(room, seats) -> float:
    if not seats:
        return 0.0
    penalty = 0.0
    for loc in seats:
        if loc["building"] != room["building"]:
            penalty += 10.0
        elif loc["floor"] != room["floor"]:
            penalty += 1.0 + 0.1 * abs(loc["floor"] - room["floor"])
    return penalty


def _is_customer(attendees) -> bool:
    domains = {a.split("@")[-1] for a in attendees if "@" in a}
    return any(d not in _INTERNAL_DOMAINS for d in domains)


# ─── Rooms ──────────────────────────────────────────────────────────────────

def list_available_rooms(store, date, start_time, end_time, min_capacity=0, building=""):
    start, end = to_dt(date, start_time), to_dt(date, end_time)
    rooms = []
    for room in store.rooms:
        if building and building.lower() not in room["building"].lower():
            continue
        if room["capacity"] < min_capacity:
            continue
        if _room_free(store, room["id"], date, start, end):
            rooms.append(room)
    return rooms


def assign_room(store, attendees, date, start_time, end_time, min_capacity=0):
    start, end = to_dt(date, start_time), to_dt(date, end_time)
    seats = [s for s in (_seat_for(store, e) for e in attendees) if s]
    n_remote = len(attendees) - len(seats)
    required = max(min_capacity, len(seats), 1)

    candidates = [
        r for r in store.rooms
        if r["capacity"] >= required and _room_free(store, r["id"], date, start, end)
        and (r.get("av") or n_remote == 0)
    ]
    if not candidates:
        candidates = [
            r for r in store.rooms
            if r["capacity"] >= required and _room_free(store, r["id"], date, start, end)
        ]
    if not candidates:
        return {"assigned": None, "reason": "No suitable room is free in that window.",
                "required_capacity": required}

    ranked = sorted(
        candidates,
        key=lambda r: (_room_penalty(r, seats), r["capacity"] - required, 0 if r.get("av") else 1),
    )
    best = ranked[0]
    here = sum(1 for s in seats if s["building"] == best["building"])
    rationale = (
        f"Seats {best['capacity']} (need {required}). {best['building']}, floor "
        f"{best['floor']}. {here}/{len(seats)} in-person attendee(s) sit in "
        f"{best['building']}." + (f" {n_remote} remote — AV equipped." if n_remote else "")
    )
    return {"assigned": best, "rationale": rationale, "required_capacity": required,
            "in_person_count": len(seats), "remote_count": n_remote,
            "alternatives": ranked[1:3]}


def book_room(store, room_id, event_title, date, start_time, end_time, organizer=""):
    room = next((r for r in store.rooms if r["id"] == room_id), None)
    if not room:
        return {"booked": False, "error": f"Unknown room '{room_id}'."}
    start, end = to_dt(date, start_time), to_dt(date, end_time)
    if not _room_free(store, room_id, date, start, end):
        return {"booked": False, "error": f"{room['name']} is already booked in that window."}
    booking = {
        "id": f"bk_{len(store.room_bookings) + 1:03d}",
        "room_id": room_id, "event_title": event_title, "date": date,
        "start": start.isoformat(), "end": end.isoformat(), "organizer": organizer,
    }
    store.room_bookings.append(booking)
    location = f"{room['name']} ({room['building']}, fl {room['floor']})"
    event = _find_event(store, title=event_title)
    if event:
        event["location"] = location
    return {"booked": True, "booking": booking, "room": room, "location": location}


# ─── Briefing / suggestions / prep ──────────────────────────────────────────

def suggest_meetings(store):
    existing = " ".join(e.get("title", "").lower() for e in store.calendar_events)
    return [
        s for s in store.meeting_suggestions
        if s["title"].split("—")[0].strip().lower() not in existing
    ]


def briefing_summary(store):
    today = store.date
    todays = [e for e in store.calendar_events if e.get("date") == today] or store.calendar_events
    upcoming = sorted(
        (e for e in store.calendar_events if e.get("date") and e["date"] > today),
        key=lambda e: e["start"],
    )
    return {
        "date": today,
        "events": todays,
        "upcoming_events": upcoming,
        "priority_emails": [e for e in store.emails if e.get("needs_action")],
        "starred_emails": [e for e in store.emails if e.get("starred")],
        "market": store.market,
        "suggestions": suggest_meetings(store),
    }


def _find_event(store, event_id="", title=""):
    if event_id:
        for e in store.calendar_events:
            if e.get("id") == event_id:
                return e
    if title:
        t = title.lower()
        for e in store.calendar_events:
            if t in e.get("title", "").lower():
                return e
    return None


def meeting_prep(store, event_id="", title=""):
    event = _find_event(store, event_id, title)
    if not event:
        return {"error": "Meeting not found", "event_id": event_id, "title": title}
    attendees = event.get("attendees", [])
    external = [a for a in attendees if "@" in a and a.split("@")[-1] not in _INTERNAL_DOMAINS]
    is_customer = bool(external) or event.get("meeting_type") == "customer"

    contacts = [a for a in attendees if a != OWNER_EMAIL] or attendees
    recent_emails = [e for e in store.emails if any(c in e.get("from", "") for c in contacts)]

    title_words = [w.lower() for w in event.get("title", "").replace("—", " ").split() if len(w) > 3]
    related = []
    for d in store.drive_docs:
        hay = d.get("name", "").lower() + " " + " ".join(d.get("tags", []))
        if any(w in hay for w in title_words):
            related.append({k: d[k] for k in ("id", "name", "webViewLink", "category") if k in d})

    profile = None
    if is_customer:
        hay = event.get("title", "").lower() + " " + " ".join(external).lower()
        for p in store.customer_profiles:
            if any(kw in hay for kw in p.get("keywords", [])):
                profile = p
                break

    return {
        "meeting": {
            "id": event.get("id"), "title": event.get("title"),
            "start": event.get("start"), "end": event.get("end"),
            "location": event.get("location", ""), "attendees": attendees,
            "meeting_type": event.get("meeting_type", "internal"),
            "video_link": event.get("video_link", ""), "description": event.get("description", ""),
        },
        "is_customer_meeting": is_customer,
        "customer_profile": profile,
        "recent_emails": recent_emails,
        "related_documents": related,
    }


def schedule_meeting(store, title, attendees, date, start_time, end_time, room_id=None):
    start, end = to_dt(date, start_time), to_dt(date, end_time)
    rationale = None
    room = next((r for r in store.rooms if r["id"] == room_id), None) if room_id else None
    if not room:
        result = assign_room(store, attendees, date, start_time, end_time)
        room = result.get("assigned")
        rationale = result.get("rationale")
    event = {
        "id": f"cal_{len(store.calendar_events) + 1:03d}",
        "date": date, "title": title,
        "start": start.isoformat(), "end": end.isoformat(),
        "location": f"{room['name']} ({room['building']}, fl {room['floor']})" if room else "TBD",
        "description": "Scheduled via SSIM assistant.",
        "attendees": attendees,
        "meeting_type": "customer" if _is_customer(attendees) else "internal",
        "video_link": "",
    }
    store.calendar_events.append(event)
    booking = None
    if room:
        booking = {
            "id": f"bk_{len(store.room_bookings) + 1:03d}",
            "room_id": room["id"], "event_title": title, "date": date,
            "start": start.isoformat(), "end": end.isoformat(), "organizer": OWNER_EMAIL,
        }
        store.room_bookings.append(booking)
    return {"scheduled": True, "event": event, "room": room,
            "rationale": rationale, "booking": booking}


# ─── Jira ───────────────────────────────────────────────────────────────────

def create_jira_tasks(store, project, task_titles, assignee="", priority="Medium"):
    board = store.jira
    titles = [t.strip() for t in task_titles.replace(";", "\n").split("\n") if t.strip()]
    n = len(board["issues"])
    created = []
    for i, t in enumerate(titles):
        issue = {
            "id": f"{board['project']}-{200 + n + i}",
            "key": f"{board['project']}-{200 + n + i}",
            "project": board["project"], "title": t, "description": "",
            "assignee": assignee or "Unassigned", "status": "To Do",
            "priority": priority, "created": store.date,
        }
        board["issues"].append(issue)
        created.append(issue)
    return {"created_count": len(created), "issues": created}


# ─── Salesforce ─────────────────────────────────────────────────────────────

def log_salesforce_activity(store, account, activity_type, summary):
    sf = store.salesforce
    activity = {
        "id": f"act_{len(sf['activities']) + 1:03d}",
        "account": account, "type": activity_type or "Note",
        "summary": summary, "date": store.date,
    }
    sf["activities"].insert(0, activity)
    return {"logged": True, "activity": activity}


def get_doc(store, doc_id):
    for d in store.drive_docs:
        if d.get("id") == doc_id:
            return {
                "id": d.get("id"),
                "name": d.get("name"),
                "content": d.get("content", "Content not available."),
                "webViewLink": d.get("webViewLink", ""),
                "category": d.get("category", ""),
            }
    return {"error": f"Document '{doc_id}' not found."}


def update_opportunity(store, opportunity_id, stage="", amount=""):
    for opp in store.salesforce["opportunities"]:
        if opp["id"] == opportunity_id or opp["name"].lower() == opportunity_id.lower():
            if stage:
                opp["stage"] = stage
            if amount:
                opp["amount"] = amount
            return {"updated": True, "opportunity": opp}
    return {"updated": False, "error": f"Opportunity '{opportunity_id}' not found."}
