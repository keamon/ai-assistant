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
from app.mock_data import MOCK_EMAILS, MOCK_CALENDAR_EVENTS, MOCK_MARKET_CONTEXT

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
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
5. Synthesize all data into a structured briefing.

**Briefing format** (use Markdown):

# Daily Briefing — [Date], [Day of Week]
## Good morning, [name if known]

### Today's Schedule
- List each meeting with time (ET), attendees, and meeting type (internal/customer)
- Flag any customer meetings requiring extra preparation
- Note back-to-back meetings or scheduling conflicts

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

**Tone**: Professional, concise, and specific to investment management. Avoid generic advice.
Surface only what is relevant to the SSIM team's work.
"""

root_agent = Agent(
    name="daily_briefing_agent",
    model=Gemini(
        model="gemini-2.0-flash-001",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_PROMPT,
    tools=[
        get_todays_calendar_events,
        get_recent_emails,
        get_starred_emails,
        get_market_context,
    ],
)

app = App(
    root_agent=root_agent,
    name="daily_briefing_app",
)
