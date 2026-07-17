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
Daily Briefing Agent — State Street Investment Management
Pulls Gmail and Google Calendar data to prepare a morning briefing
with focus items, meeting summaries, and action items for the day.
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

# Mock data for demonstration — replace with real API calls via credentials
from app.mock_data import (
    MOCK_EMAILS,
    MOCK_CALENDAR_EVENTS,
    MOCK_MARKET_CONTEXT,
    MOCK_DRIVE_DOCS,
    MOCK_CUSTOMER_PROFILES,
    MOCK_ROOMS,
    MOCK_EMPLOYEE_LOCATIONS,
    MOCK_ROOM_BOOKINGS,
    MOCK_MEETING_SUGGESTIONS,
)

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "us"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

EASTERN = ZoneInfo("America/New_York")


# ─── Tool: Calendar ───────────────────────────────────────────────────────────

def get_todays_calendar_events(date: str = "") -> str:
    """Retrieve all calendar events scheduled for today (or a specified date).

    Connects to Google Calendar for dev@chenkeamonwang.altostrat.com.
    Falls back to mock data in development mode.

    Args:
        date: Optional date string in YYYY-MM-DD format. Defaults to today.

    Returns:
        JSON string listing today's calendar events with time, title,
        attendees, location, and meeting type (internal / customer / external).
    """
    try:
        from googleapiclient.discovery import build
        from google.oauth2 import credentials as oauth2_credentials

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/calendar.readonly"]
        )
        service = build("calendar", "v3", credentials=creds)

        target_date = (
            datetime.date.fromisoformat(date) if date else datetime.date.today()
        )
        start = datetime.datetime(
            target_date.year, target_date.month, target_date.day,
            tzinfo=EASTERN
        ).isoformat()
        end = (
            datetime.datetime(
                target_date.year, target_date.month, target_date.day,
                tzinfo=EASTERN
            ) + datetime.timedelta(days=1)
        ).isoformat()

        result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start,
                timeMax=end,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = []
        for e in result.get("items", []):
            attendees = [
                a.get("email", "") for a in e.get("attendees", [])
            ]
            domain_set = {a.split("@")[-1] for a in attendees if "@" in a}
            meeting_type = (
                "customer"
                if any(
                    d not in ("chenkeamonwang.altostrat.com", "statestreet.com")
                    for d in domain_set
                )
                else "internal"
            )
            events.append(
                {
                    "id": e.get("id"),
                    "title": e.get("summary", "(No title)"),
                    "start": e["start"].get("dateTime", e["start"].get("date")),
                    "end": e["end"].get("dateTime", e["end"].get("date")),
                    "location": e.get("location", ""),
                    "description": e.get("description", "")[:300],
                    "attendees": attendees,
                    "meeting_type": meeting_type,
                    "video_link": e.get("hangoutLink", ""),
                }
            )
        return json.dumps({"date": str(target_date), "events": events}, indent=2)

    except Exception:
        # Fall back to mock data
        target = date or str(datetime.date.today())
        events = [e for e in MOCK_CALENDAR_EVENTS if e.get("date") == target]
        if not events:
            events = MOCK_CALENDAR_EVENTS  # return all mock if date not matched
        return json.dumps({"date": target, "events": events, "source": "mock"}, indent=2)


# ─── Tool: Gmail ──────────────────────────────────────────────────────────────

def get_recent_emails(hours_back: int = 24, max_results: int = 20) -> str:
    """Retrieve recent emails from Gmail for the past N hours.

    Prioritises unread, flagged, and emails with action-required subjects.
    Connects to Gmail API for dev@chenkeamonwang.altostrat.com.

    Args:
        hours_back: How many hours back to search. Default 24.
        max_results: Maximum number of emails to return. Default 20.

    Returns:
        JSON string with a list of emails including sender, subject,
        snippet, date, labels, and whether action is likely required.
    """
    try:
        from googleapiclient.discovery import build

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/gmail.readonly"]
        )
        service = build("gmail", "v1", credentials=creds)

        after_ts = int(
            (
                datetime.datetime.now(EASTERN)
                - datetime.timedelta(hours=hours_back)
            ).timestamp()
        )
        query = f"after:{after_ts}"

        results = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
        )

        emails = []
        for msg_ref in results.get("messages", []):
            msg = (
                service.users()
                .messages()
                .get(userId="me", id=msg_ref["id"], format="metadata",
                     metadataHeaders=["From", "To", "Subject", "Date"])
                .execute()
            )
            headers = {
                h["name"]: h["value"]
                for h in msg.get("payload", {}).get("headers", [])
            }
            labels = msg.get("labelIds", [])
            action_keywords = ["action required", "urgent", "deadline", "approve",
                                "review", "response needed", "eod", "asap"]
            subj = headers.get("Subject", "").lower()
            needs_action = (
                "UNREAD" in labels
                or any(kw in subj for kw in action_keywords)
                or "STARRED" in labels
            )
            emails.append(
                {
                    "id": msg_ref["id"],
                    "from": headers.get("From", ""),
                    "subject": headers.get("Subject", ""),
                    "date": headers.get("Date", ""),
                    "snippet": msg.get("snippet", "")[:200],
                    "labels": labels,
                    "needs_action": needs_action,
                }
            )
        return json.dumps(
            {"hours_back": hours_back, "email_count": len(emails), "emails": emails},
            indent=2,
        )

    except Exception:
        filtered = MOCK_EMAILS[:max_results]
        return json.dumps(
            {
                "hours_back": hours_back,
                "email_count": len(filtered),
                "emails": filtered,
                "source": "mock",
            },
            indent=2,
        )


def get_starred_emails(max_results: int = 10) -> str:
    """Retrieve starred/flagged emails — items previously marked for follow-up.

    Args:
        max_results: Maximum number of starred emails to return. Default 10.

    Returns:
        JSON string with starred emails requiring attention.
    """
    try:
        from googleapiclient.discovery import build

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/gmail.readonly"]
        )
        service = build("gmail", "v1", credentials=creds)
        results = (
            service.users()
            .messages()
            .list(userId="me", q="is:starred", maxResults=max_results)
            .execute()
        )
        emails = []
        for msg_ref in results.get("messages", []):
            msg = (
                service.users()
                .messages()
                .get(userId="me", id=msg_ref["id"], format="metadata",
                     metadataHeaders=["From", "Subject", "Date"])
                .execute()
            )
            headers = {h["name"]: h["value"]
                       for h in msg.get("payload", {}).get("headers", [])}
            emails.append(
                {
                    "id": msg_ref["id"],
                    "from": headers.get("From", ""),
                    "subject": headers.get("Subject", ""),
                    "date": headers.get("Date", ""),
                    "snippet": msg.get("snippet", "")[:200],
                }
            )
        return json.dumps({"starred_emails": emails}, indent=2)

    except Exception:
        starred = [e for e in MOCK_EMAILS if e.get("starred")]
        return json.dumps({"starred_emails": starred[:max_results], "source": "mock"}, indent=2)


# ─── Tool: Market Context ─────────────────────────────────────────────────────

def get_market_context() -> str:
    """Return relevant market and portfolio context for State Street IM.

    Provides AUM updates, key market moves, fund performance highlights,
    and regulatory/compliance reminders relevant for the day.

    Returns:
        JSON string with market context relevant to the investment team.
    """
    return json.dumps(MOCK_MARKET_CONTEXT, indent=2)


# ─── Tools: Meeting Prep (folded in from the meeting_prep agent) ───────────────

def search_emails_by_attendees(attendee_emails: str, days_back: int = 30) -> str:
    """Search Gmail for recent email threads with specific attendees.

    Args:
        attendee_emails: Comma-separated list of email addresses to search for.
        days_back: How many days back to search. Default 30.

    Returns:
        JSON string with relevant email threads from those contacts.
    """
    try:
        from googleapiclient.discovery import build

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/gmail.readonly"]
        )
        service = build("gmail", "v1", credentials=creds)
        emails_list = [e.strip() for e in attendee_emails.split(",")]
        from_query = " OR ".join(f"from:{e}" for e in emails_list)
        after_date = (
            datetime.date.today() - datetime.timedelta(days=days_back)
        ).strftime("%Y/%m/%d")
        query = f"({from_query}) after:{after_date}"
        results = service.users().messages().list(
            userId="me", q=query, maxResults=15
        ).execute()
        emails = []
        for msg_ref in results.get("messages", []):
            msg = service.users().messages().get(
                userId="me", id=msg_ref["id"], format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"]
            ).execute()
            headers = {h["name"]: h["value"]
                       for h in msg.get("payload", {}).get("headers", [])}
            emails.append({
                "from": headers.get("From", ""),
                "to": headers.get("To", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "snippet": msg.get("snippet", "")[:300],
            })
        return json.dumps({"attendees_searched": emails_list, "emails": emails}, indent=2)
    except Exception:
        emails_list = [e.strip() for e in attendee_emails.split(",")]
        matched = [
            e for e in MOCK_EMAILS
            if any(addr in e.get("from", "") or addr in e.get("to", "")
                   for addr in emails_list)
        ]
        if not matched:
            matched = MOCK_EMAILS[:5]
        return json.dumps(
            {"attendees_searched": emails_list, "emails": matched, "source": "mock"}, indent=2
        )


def search_drive_documents(query: str, max_results: int = 5) -> str:
    """Search Google Drive for documents relevant to a meeting topic.

    Args:
        query: Keywords to search for (e.g. "Global Equity Fund Q2 2026").
        max_results: Maximum number of documents to return. Default 5.

    Returns:
        JSON string with matching documents including name, link, and summary.
    """
    try:
        from googleapiclient.discovery import build

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        service = build("drive", "v3", credentials=creds)
        results = (
            service.files()
            .list(
                q=f"fullText contains '{query}' and trashed=false",
                pageSize=max_results,
                fields="files(id, name, mimeType, webViewLink, modifiedTime, description)",
                orderBy="modifiedTime desc",
            )
            .execute()
        )
        docs = results.get("files", [])
        return json.dumps({"query": query, "documents": docs}, indent=2)
    except Exception:
        q_lower = query.lower()
        matched = [
            d for d in MOCK_DRIVE_DOCS
            if q_lower in d.get("name", "").lower()
            or any(q_lower in tag for tag in d.get("tags", []))
        ]
        if not matched:
            matched = MOCK_DRIVE_DOCS[:3]
        return json.dumps(
            {"query": query, "documents": matched[:max_results], "source": "mock"}, indent=2
        )


def get_drive_document_content(file_id: str) -> str:
    """Retrieve the text content of a Google Drive document by file ID.

    Args:
        file_id: The Google Drive file ID.

    Returns:
        The document text content (first 3000 characters).
    """
    try:
        from googleapiclient.discovery import build

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        service = build("drive", "v3", credentials=creds)
        content = service.files().export(fileId=file_id, mimeType="text/plain").execute()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        return content[:3000]
    except Exception:
        for doc in MOCK_DRIVE_DOCS:
            if doc.get("id") == file_id:
                return doc.get("content", "Content not available.")
        return "Document content not available in mock data."


def get_customer_profile(customer_name: str) -> str:
    """Retrieve background information on a customer or prospect.

    Args:
        customer_name: Name of the customer organisation or contact.

    Returns:
        JSON string with customer profile and relationship context.
    """
    name_lower = customer_name.lower()
    for profile in MOCK_CUSTOMER_PROFILES:
        if name_lower in profile.get("name", "").lower():
            return json.dumps(profile, indent=2)
    for profile in MOCK_CUSTOMER_PROFILES:
        if any(kw in name_lower for kw in profile.get("keywords", [])):
            return json.dumps(profile, indent=2)
    return json.dumps({
        "name": customer_name,
        "status": "Not found in CRM",
        "note": "This may be a new prospect. Check Salesforce or recent emails.",
    })


def _find_event(event_id: str = "", meeting_title: str = "") -> dict | None:
    """Locate a calendar event in the mock calendar by id or title substring."""
    if event_id:
        for e in MOCK_CALENDAR_EVENTS:
            if e.get("id") == event_id:
                return e
    if meeting_title:
        t = meeting_title.lower()
        for e in MOCK_CALENDAR_EVENTS:
            if t in e.get("title", "").lower():
                return e
    return None


def get_meeting_prep(event_id: str = "", meeting_title: str = "") -> str:
    """Assemble a full prep brief for one meeting (the expandable per-meeting view).

    Pulls the meeting's details, recent emails from its attendees, related Drive
    documents, and — for customer meetings — the client CRM profile.

    Args:
        event_id: Calendar event id (preferred). Optional.
        meeting_title: Meeting title or a substring of it, if the id is unknown.

    Returns:
        JSON string with the meeting, customer_profile, recent_emails, and
        related_documents needed to prepare for the meeting.
    """
    event = _find_event(event_id, meeting_title)
    if not event:
        return json.dumps(
            {"error": "Meeting not found", "event_id": event_id, "meeting_title": meeting_title}
        )

    attendees = event.get("attendees", [])
    external = [
        a for a in attendees
        if "@" in a
        and a.split("@")[-1] not in ("chenkeamonwang.altostrat.com", "statestreet.com")
    ]
    is_customer = bool(external) or event.get("meeting_type") == "customer"

    # Recent emails from the *other* attendees (exclude the owner, whose address
    # is on every thread and would otherwise match everything).
    contacts = [a for a in attendees if a != "dev@chenkeamonwang.altostrat.com"] or attendees
    recent_emails = [
        e for e in MOCK_EMAILS
        if any(addr in e.get("from", "") for addr in contacts)
    ]

    # Related Drive docs — match on words from the meeting title
    title_words = [w.lower() for w in event.get("title", "").replace("—", " ").split() if len(w) > 3]
    related_docs = []
    for d in MOCK_DRIVE_DOCS:
        hay = (d.get("name", "").lower() + " " + " ".join(d.get("tags", [])))
        if any(w in hay for w in title_words):
            related_docs.append({k: d[k] for k in ("id", "name", "webViewLink", "category") if k in d})

    # Customer profile for customer meetings
    profile = None
    if is_customer:
        for p in MOCK_CUSTOMER_PROFILES:
            hay = event.get("title", "").lower() + " " + " ".join(external).lower()
            if any(kw in hay for kw in p.get("keywords", [])):
                profile = p
                break

    return json.dumps(
        {
            "meeting": {
                "id": event.get("id"),
                "title": event.get("title"),
                "start": event.get("start"),
                "end": event.get("end"),
                "location": event.get("location", ""),
                "attendees": attendees,
                "meeting_type": event.get("meeting_type", "internal"),
                "video_link": event.get("video_link", ""),
                "description": event.get("description", ""),
            },
            "is_customer_meeting": is_customer,
            "customer_profile": profile,
            "recent_emails": recent_emails,
            "related_documents": related_docs,
            "source": "mock",
        },
        indent=2,
    )


# ─── Tool: Suggested meetings to schedule ──────────────────────────────────────

def suggest_meetings_to_schedule() -> str:
    """Suggest meetings that likely need to be scheduled but aren't on the calendar.

    Scans today's signals (emails, action items, portfolio events) for situations
    that imply a meeting is needed, and returns them as structured suggestions the
    UI can render with a "Schedule" action.

    Returns:
        JSON string: a list of suggestions, each with title, rationale, suggested
        attendees, duration, priority, and a suggested date.
    """
    existing_titles = " ".join(e.get("title", "").lower() for e in MOCK_CALENDAR_EVENTS)
    suggestions = [
        s for s in MOCK_MEETING_SUGGESTIONS
        # Drop a suggestion if a very similar meeting is already scheduled.
        if s["title"].split("—")[0].strip().lower() not in existing_titles
    ]
    return json.dumps(
        {"suggestion_count": len(suggestions), "suggestions": suggestions, "source": "mock"},
        indent=2,
    )


# ─── Tool: Schedule a meeting (creates event + auto-books a room) ───────────────

def _sched_dt(date: str, time_str: str) -> datetime.datetime:
    time_part = time_str.strip()
    if "T" in time_part:
        time_part = time_part.split("T", 1)[1]
    time_part = time_part[:8] if len(time_part) >= 8 else time_part[:5]
    fmt = "%H:%M:%S" if time_part.count(":") == 2 else "%H:%M"
    t = datetime.datetime.strptime(time_part, fmt).time()
    d = datetime.date.fromisoformat(date)
    return datetime.datetime(d.year, d.month, d.day, t.hour, t.minute, tzinfo=EASTERN)


def _room_free(room_id: str, date: str, start: datetime.datetime, end: datetime.datetime) -> bool:
    for bk in MOCK_ROOM_BOOKINGS:
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


def _seat_for(email: str) -> dict | None:
    email = email.strip().lower()
    for loc in MOCK_EMPLOYEE_LOCATIONS:
        if loc["email"].lower() == email:
            return loc
    return None


def _room_penalty(room: dict, seats: list[dict]) -> float:
    if not seats:
        return 0.0
    penalty = 0.0
    for loc in seats:
        if loc["building"] != room["building"]:
            penalty += 10.0
        elif loc["floor"] != room["floor"]:
            penalty += 1.0 + 0.1 * abs(loc["floor"] - room["floor"])
    return penalty


def _assign_room(attendee_emails: list[str], date: str, start: datetime.datetime,
                 end: datetime.datetime) -> dict | None:
    """Pick the best-fit free room (capacity + proximity). Mirrors the meeting_room agent."""
    seats = [s for s in (_seat_for(e) for e in attendee_emails) if s]
    n_remote = len(attendee_emails) - len(seats)
    required = max(len(seats), 1)
    candidates = [
        r for r in MOCK_ROOMS
        if r["capacity"] >= required and _room_free(r["id"], date, start, end)
        and (r.get("av") or n_remote == 0)
    ]
    if not candidates:
        candidates = [
            r for r in MOCK_ROOMS
            if r["capacity"] >= required and _room_free(r["id"], date, start, end)
        ]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda r: (_room_penalty(r, seats), r["capacity"] - required, 0 if r.get("av") else 1),
    )[0]


def schedule_meeting(title: str, attendee_emails: str, date: str,
                     start_time: str, end_time: str) -> str:
    """Schedule a new meeting: create the calendar event AND auto-book a room.

    This is a WRITE action — confirm the details with the user before calling it.

    Args:
        title: Meeting title.
        attendee_emails: Comma-separated attendee email addresses.
        date: Date in YYYY-MM-DD format.
        start_time: Start time in HH:MM (24h) format.
        end_time: End time in HH:MM (24h) format.

    Returns:
        JSON string confirming the created event and the assigned room.
    """
    try:
        start = _sched_dt(date, start_time)
        end = _sched_dt(date, end_time)
    except Exception as e:
        return json.dumps({"scheduled": False, "error": f"Could not parse date/time: {e}"})

    attendees = [e.strip() for e in attendee_emails.split(",") if e.strip()]
    room = _assign_room(attendees, date, start, end)

    domains = {a.split("@")[-1] for a in attendees if "@" in a}
    is_customer = any(
        d not in ("chenkeamonwang.altostrat.com", "statestreet.com") for d in domains
    )

    event = {
        "id": f"cal_{len(MOCK_CALENDAR_EVENTS) + 1:03d}",
        "date": date,
        "title": title,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "location": f"{room['name']} ({room['building']}, fl {room['floor']})" if room else "TBD",
        "description": "Scheduled via Daily Briefing assistant.",
        "attendees": attendees,
        "meeting_type": "customer" if is_customer else "internal",
        "video_link": "",
    }
    MOCK_CALENDAR_EVENTS.append(event)

    booking = None
    if room:
        booking = {
            "id": f"bk_{len(MOCK_ROOM_BOOKINGS) + 1:03d}",
            "room_id": room["id"],
            "event_title": title,
            "date": date,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "organizer": "dev@chenkeamonwang.altostrat.com",
        }
        MOCK_ROOM_BOOKINGS.append(booking)

    return json.dumps(
        {
            "scheduled": True,
            "event": event,
            "room": room,
            "booking": booking,
            "note": None if room else "No room could be auto-assigned; please book manually.",
            "source": "mock",
        },
        indent=2,
    )


# ─── Agent Definition ─────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the Daily Briefing Agent for State Street Investment Management (SSIM).

Your role is to prepare a concise, actionable morning briefing for investment professionals
at State Street Investment Management. SSIM manages approximately $4.1 trillion in AUM
across index, active, and ESG strategies globally.

**Your audience**: Portfolio managers, relationship managers, investment strategists,
and senior leaders on the SSIM team.

When asked for the daily briefing, you must:
1. Call `get_todays_calendar_events` to retrieve today's schedule.
2. Call `get_recent_emails` (last 24 hours) to check important communications.
3. Call `get_starred_emails` to surface any flagged follow-up items.
4. Call `get_market_context` for portfolio and market context.
5. Call `suggest_meetings_to_schedule` to surface meetings that should be booked.
6. Synthesize all data into a structured briefing.

**Briefing format** (use Markdown):

# Daily Briefing — [Date], [Day of Week]
## Good morning, [name if known]

### Today's Schedule
- List each meeting with time (ET), attendees, and meeting type (internal/customer)
- Flag any customer meetings requiring extra preparation
- Note back-to-back meetings or scheduling conflicts
- Mention that a full prep brief is available for any meeting on request

### Suggested Meetings to Schedule
- List the suggestions from `suggest_meetings_to_schedule` with a one-line rationale
- For each, note the suggested attendees, date, and priority

### Priority Emails & Action Items
- List emails needing a response or action today
- Include sender, subject, and the specific action required
- Prioritise by urgency

### Starred Follow-ups
- Items previously flagged that still need attention

### Market & Portfolio Context
- Key market developments relevant to SSIM strategies
- Any portfolio or AUM highlights
- Regulatory or compliance reminders

### Focus for Today
- Synthesise the top 3–5 priorities the person should focus on
- Consider both meetings and outstanding tasks

**Per-meeting prep (expandable view):**
When the user asks to prepare for / expand / open a specific meeting, call
`get_meeting_prep` with the event id or meeting title and produce a concise brief:
objective, attendees & client profile, recent communications, relevant documents,
and suggested talking points. For customer meetings, always include the client's
mandate, current SSIM strategies, and any renewal or mandate risk.

**Scheduling meetings:**
When the user wants to schedule one of the suggested meetings (or any new meeting),
gather the title, attendees, date, and time, then **confirm the details before
writing**. Call `schedule_meeting` — it creates the calendar event and auto-assigns
the best-fit meeting room (by capacity and attendee seat proximity). Report the
scheduled time and the assigned room with a one-line rationale.

**Tone**: Professional, concise, and specific to investment management. Avoid generic advice.
Surface only what is relevant to the SSIM team's work.
"""

root_agent = Agent(
    name="daily_briefing_agent",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_PROMPT,
    tools=[
        get_todays_calendar_events,
        get_recent_emails,
        get_starred_emails,
        get_market_context,
        suggest_meetings_to_schedule,
        get_meeting_prep,
        schedule_meeting,
        search_emails_by_attendees,
        search_drive_documents,
        get_drive_document_content,
        get_customer_profile,
    ],
)

app = App(
    root_agent=root_agent,
    name="daily_briefing_app",
)
