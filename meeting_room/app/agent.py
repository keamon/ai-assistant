# ruff: noqa
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
Meeting Room Booking Agent — State Street Investment Management
Looks at the room inventory and each attendee's seat location, then
auto-assigns the best-fit meeting room (capacity + proximity) and books it.

In this dev environment the room inventory, seat directory, and booking
ledger are served from `app.mock_data`. A production build would replace
these with Google Workspace Calendar *resource* calendars + free/busy
queries; the tool signatures are designed to be a drop-in for that.
"""

import os
import json
import datetime
from zoneinfo import ZoneInfo

import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.mock_data import (
    MOCK_ROOMS,
    MOCK_EMPLOYEE_LOCATIONS,
    MOCK_ROOM_BOOKINGS,
)

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "us"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

EASTERN = ZoneInfo("America/New_York")


# ─── Helpers ────────────────────────────────────────────────────────────────

def _to_dt(date: str, time_str: str) -> datetime.datetime:
    """Combine a YYYY-MM-DD date and an HH:MM(:SS) time into an Eastern datetime."""
    time_part = time_str.strip()
    if "T" in time_part:  # full ISO passed in
        time_part = time_part.split("T", 1)[1]
    time_part = time_part[:8] if len(time_part) >= 8 else time_part[:5]
    fmt = "%H:%M:%S" if time_part.count(":") == 2 else "%H:%M"
    t = datetime.datetime.strptime(time_part, fmt).time()
    d = datetime.date.fromisoformat(date)
    return datetime.datetime(d.year, d.month, d.day, t.hour, t.minute, tzinfo=EASTERN)


def _overlaps(a_start, a_end, b_start, b_end) -> bool:
    return a_start < b_end and b_start < a_end


def _room_is_free(room_id: str, date: str, start: datetime.datetime,
                  end: datetime.datetime) -> bool:
    for bk in MOCK_ROOM_BOOKINGS:
        if bk.get("room_id") != room_id or bk.get("date") != date:
            continue
        try:
            b_start = datetime.datetime.fromisoformat(bk["start"])
            b_end = datetime.datetime.fromisoformat(bk["end"])
        except Exception:
            continue
        if _overlaps(start, end, b_start, b_end):
            return False
    return True


def _location_for(email: str) -> dict | None:
    email = email.strip().lower()
    for loc in MOCK_EMPLOYEE_LOCATIONS:
        if loc["email"].lower() == email:
            return loc
    return None


def _proximity_penalty(room: dict, in_person_locations: list[dict]) -> float:
    """Lower is closer. Sums per-attendee travel cost to the room."""
    if not in_person_locations:
        return 0.0
    penalty = 0.0
    for loc in in_person_locations:
        if loc["building"] != room["building"]:
            penalty += 10.0  # different building — worst case
        elif loc["floor"] != room["floor"]:
            penalty += 1.0 + 0.1 * abs(loc["floor"] - room["floor"])
        # same building & floor → 0
    return penalty


# ─── Tool: list available rooms ─────────────────────────────────────────────

def list_available_rooms(date: str, start_time: str, end_time: str,
                         min_capacity: int = 0, building: str = "") -> str:
    """List meeting rooms that are free for a given time window.

    Args:
        date: Date in YYYY-MM-DD format.
        start_time: Start time in HH:MM (24h) format, e.g. "10:00".
        end_time: End time in HH:MM (24h) format, e.g. "11:30".
        min_capacity: Only return rooms seating at least this many people. Default 0.
        building: Optional building filter (e.g. "One Congress", "Channel Center", "Toronto").

    Returns:
        JSON string listing available rooms with capacity, building, floor, and equipment.
    """
    try:
        start = _to_dt(date, start_time)
        end = _to_dt(date, end_time)
    except Exception as e:
        return json.dumps({"error": f"Could not parse date/time: {e}"})

    available = []
    for room in MOCK_ROOMS:
        if building and building.lower() not in room["building"].lower():
            continue
        if room["capacity"] < min_capacity:
            continue
        if _room_is_free(room["id"], date, start, end):
            available.append(room)

    return json.dumps(
        {
            "date": date,
            "window": f"{start_time}–{end_time}",
            "min_capacity": min_capacity,
            "building_filter": building or "(any)",
            "available_count": len(available),
            "available_rooms": available,
            "source": "mock",
        },
        indent=2,
    )


# ─── Tool: attendee seat locations ──────────────────────────────────────────

def get_attendee_locations(attendee_emails: str) -> str:
    """Look up the office seat location for each attendee.

    Args:
        attendee_emails: Comma-separated list of attendee email addresses.

    Returns:
        JSON string with each attendee's building/floor/seat, a count of remote
        (external / unknown) attendees, and the building where most attendees sit.
    """
    emails = [e.strip() for e in attendee_emails.split(",") if e.strip()]
    located, remote = [], []
    for email in emails:
        loc = _location_for(email)
        if loc:
            located.append(loc)
        else:
            remote.append(email)

    building_counts: dict[str, int] = {}
    for loc in located:
        building_counts[loc["building"]] = building_counts.get(loc["building"], 0) + 1
    plurality_building = (
        max(building_counts, key=building_counts.get) if building_counts else ""
    )

    return json.dumps(
        {
            "located": located,
            "remote_or_unknown": remote,
            "building_distribution": building_counts,
            "plurality_building": plurality_building,
            "source": "mock",
        },
        indent=2,
    )


# ─── Tool: auto-assign the best room ────────────────────────────────────────

def assign_meeting_room(attendee_emails: str, date: str, start_time: str,
                        end_time: str, min_capacity: int = 0) -> str:
    """Auto-assign the single best-fit meeting room for a meeting.

    Selection logic: from rooms that are free in the window and large enough,
    pick the one that minimises total travel for in-person attendees (same
    building/floor preferred), tie-broken by the tightest capacity fit. If any
    attendee is remote/external, video-conference-equipped rooms are preferred.

    Args:
        attendee_emails: Comma-separated attendee email addresses.
        date: Date in YYYY-MM-DD format.
        start_time: Start time in HH:MM (24h) format.
        end_time: End time in HH:MM (24h) format.
        min_capacity: Minimum room capacity to require. Defaults to the attendee count.

    Returns:
        JSON string with the recommended room, a plain-language rationale, and
        up to two alternatives. Does NOT book the room — call `book_room` to confirm.
    """
    try:
        start = _to_dt(date, start_time)
        end = _to_dt(date, end_time)
    except Exception as e:
        return json.dumps({"error": f"Could not parse date/time: {e}"})

    emails = [e.strip() for e in attendee_emails.split(",") if e.strip()]
    in_person = [loc for loc in (_location_for(e) for e in emails) if loc]
    n_remote = len(emails) - len(in_person)
    required_capacity = max(min_capacity, len(in_person), 1)

    candidates = []
    for room in MOCK_ROOMS:
        if room["capacity"] < required_capacity:
            continue
        if not _room_is_free(room["id"], date, start, end):
            continue
        needs_av = n_remote > 0
        if needs_av and not room.get("av"):
            continue
        candidates.append(room)

    if not candidates:
        # Relax the AV requirement rather than fail outright.
        for room in MOCK_ROOMS:
            if room["capacity"] >= required_capacity and _room_is_free(
                room["id"], date, start, end
            ):
                candidates.append(room)

    if not candidates:
        return json.dumps(
            {
                "assigned": None,
                "reason": "No room with sufficient capacity is free in that window.",
                "required_capacity": required_capacity,
                "source": "mock",
            },
            indent=2,
        )

    def sort_key(room):
        return (
            _proximity_penalty(room, in_person),   # closest to attendees first
            room["capacity"] - required_capacity,   # tightest sufficient fit
            0 if room.get("av") else 1,             # prefer AV on ties
        )

    ranked = sorted(candidates, key=sort_key)
    best = ranked[0]

    building_counts: dict[str, int] = {}
    for loc in in_person:
        building_counts[loc["building"]] = building_counts.get(loc["building"], 0) + 1

    rationale_parts = [
        f"Seats {best['capacity']} (need {required_capacity}).",
        f"In {best['building']}, floor {best['floor']}.",
    ]
    if building_counts:
        here = building_counts.get(best["building"], 0)
        rationale_parts.append(
            f"{here} of {len(in_person)} in-person attendee(s) already sit in {best['building']}."
        )
    if n_remote:
        rationale_parts.append(
            f"{n_remote} remote/external attendee(s) — {'video-conference equipped' if best.get('av') else 'no AV available'}."
        )

    return json.dumps(
        {
            "assigned": best,
            "rationale": " ".join(rationale_parts),
            "required_capacity": required_capacity,
            "in_person_count": len(in_person),
            "remote_count": n_remote,
            "alternatives": ranked[1:3],
            "source": "mock",
        },
        indent=2,
    )


# ─── Tool: book the room (write) ────────────────────────────────────────────

def book_room(room_id: str, event_title: str, date: str, start_time: str,
              end_time: str, organizer: str = "") -> str:
    """Book a meeting room. This is a WRITE action — confirm with the user first.

    Args:
        room_id: The room id to book (from `assign_meeting_room` / `list_available_rooms`).
        event_title: Title of the meeting.
        date: Date in YYYY-MM-DD format.
        start_time: Start time in HH:MM (24h) format.
        end_time: End time in HH:MM (24h) format.
        organizer: Email of the meeting organizer. Optional.

    Returns:
        JSON string confirming the booking, or an error if the room is unavailable.
    """
    room = next((r for r in MOCK_ROOMS if r["id"] == room_id), None)
    if not room:
        return json.dumps({"booked": False, "error": f"Unknown room '{room_id}'."})

    try:
        start = _to_dt(date, start_time)
        end = _to_dt(date, end_time)
    except Exception as e:
        return json.dumps({"booked": False, "error": f"Could not parse date/time: {e}"})

    if not _room_is_free(room_id, date, start, end):
        return json.dumps(
            {"booked": False, "error": f"{room['name']} is already booked in that window."}
        )

    booking = {
        "id": f"bk_{len(MOCK_ROOM_BOOKINGS) + 1:03d}",
        "room_id": room_id,
        "event_title": event_title,
        "date": date,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "organizer": organizer,
    }
    MOCK_ROOM_BOOKINGS.append(booking)

    return json.dumps(
        {
            "booked": True,
            "booking": booking,
            "room_name": room["name"],
            "location": f"{room['building']}, floor {room['floor']}",
            "source": "mock",
        },
        indent=2,
    )


# ─── Agent Definition ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the Meeting Room Booking Agent for State Street Investment Management (SSIM).

Your job is to find and assign the best meeting room for a meeting, taking into account
both room capacity and where the attendees actually sit.

**SSIM offices**: One Congress (Boston HQ), Channel Center (Boston), and Toronto.

**How to handle a room request:**

1. Determine the meeting date, start time, end time, and the attendee list.
2. Call `get_attendee_locations` to see where attendees sit and how many are remote/external.
3. To auto-assign, call `assign_meeting_room` — it returns the recommended room, a rationale,
   and alternatives. Prefer this over `list_available_rooms` when the user wants a room chosen.
4. Use `list_available_rooms` when the user wants to browse options for a window.
5. **Before booking, always confirm the choice with the user.** Then call `book_room`.

**Room selection principles:**
- The room must be free for the whole window and seat everyone attending in person.
- Minimise attendee travel: prefer the building (then floor) where most in-person attendees sit.
- Prefer the tightest room that still fits — don't put 3 people in a 20-person boardroom.
- If anyone joins remotely or is external, prefer a video-conference-equipped room.

**When you respond:**
- State the assigned room, its building/floor/capacity, and a one-line rationale.
- List one or two alternatives when helpful.
- Never double-book a room. If nothing fits, say so and suggest the closest options.

Tone: concise, practical, logistics-focused.
"""

root_agent = Agent(
    name="meeting_room_agent",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_PROMPT,
    tools=[
        list_available_rooms,
        get_attendee_locations,
        assign_meeting_room,
        book_room,
    ],
)

app = App(
    root_agent=root_agent,
    name="meeting_room_app",
)
