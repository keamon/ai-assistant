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
Meeting Prep Agent — State Street Investment Management
Pulls Google Calendar, Gmail, and Drive to generate meeting plans,
talking tracks, and background context (especially for customer meetings).
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
    MOCK_CALENDAR_EVENTS,
    MOCK_EMAILS,
    MOCK_DRIVE_DOCS,
    MOCK_CUSTOMER_PROFILES,
)

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

EASTERN = ZoneInfo("America/New_York")


def search_calendar_events(query: str, days_ahead: int = 7) -> str:
    """Search upcoming calendar events by keyword (title, attendee, or topic).

    Args:
        query: Search term — meeting title, attendee name, or topic keyword.
        days_ahead: How many days ahead to search. Default 7.

    Returns:
        JSON string with matching calendar events including attendees and details.
    """
    try:
        from googleapiclient.discovery import build

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/calendar.readonly"]
        )
        service = build("calendar", "v3", credentials=creds)
        now = datetime.datetime.now(EASTERN)
        time_max = now + datetime.timedelta(days=days_ahead)
        result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now.isoformat(),
                timeMax=time_max.isoformat(),
                singleEvents=True,
                orderBy="startTime",
                q=query,
            )
            .execute()
        )
        events = []
        for e in result.get("items", []):
            attendees = [a.get("email", "") for a in e.get("attendees", [])]
            domain_set = {a.split("@")[-1] for a in attendees if "@" in a}
            is_customer = any(
                d not in ("chenkeamonwang.altostrat.com", "statestreet.com")
                for d in domain_set
            )
            events.append({
                "id": e.get("id"),
                "title": e.get("summary", "(No title)"),
                "start": e["start"].get("dateTime", e["start"].get("date")),
                "end": e["end"].get("dateTime", e["end"].get("date")),
                "location": e.get("location", ""),
                "description": e.get("description", "")[:500],
                "attendees": attendees,
                "is_customer_meeting": is_customer,
                "video_link": e.get("hangoutLink", ""),
                "organizer": e.get("organizer", {}).get("email", ""),
            })
        return json.dumps({"query": query, "events": events}, indent=2)

    except Exception:
        q_lower = query.lower()
        matched = [
            e for e in MOCK_CALENDAR_EVENTS
            if q_lower in e.get("title", "").lower()
            or any(q_lower in a.lower() for a in e.get("attendees", []))
        ]
        if not matched:
            matched = MOCK_CALENDAR_EVENTS[:3]
        return json.dumps({"query": query, "events": matched, "source": "mock"}, indent=2)


def get_meeting_by_id(event_id: str) -> str:
    """Fetch full details for a specific calendar event by ID.

    Args:
        event_id: The Google Calendar event ID.

    Returns:
        JSON string with full event details.
    """
    try:
        from googleapiclient.discovery import build

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/calendar.readonly"]
        )
        service = build("calendar", "v3", credentials=creds)
        e = service.events().get(calendarId="primary", eventId=event_id).execute()
        return json.dumps(e, indent=2)
    except Exception:
        for e in MOCK_CALENDAR_EVENTS:
            if e.get("id") == event_id:
                return json.dumps(e, indent=2)
        return json.dumps({"error": f"Event {event_id} not found"})


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
    """Search Google Drive for documents relevant to the meeting topic.

    Args:
        query: Keywords to search for (e.g. "Global Equity Fund Q1 2026").
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


SYSTEM_PROMPT = """You are the Meeting Prep Agent for State Street Investment Management (SSIM).

Your role is to prepare comprehensive meeting briefs for SSIM professionals before
client meetings, internal strategy sessions, and partner calls.

SSIM manages ~$4.1 trillion AUM across index, active quantitative, ESG, and multi-asset
strategies. The team serves institutional clients: pension funds, sovereign wealth funds,
insurance companies, foundations, and wealth platforms.

**How to respond to a meeting prep request:**

1. Call `search_calendar_events` to find the specific meeting. If the user provides an
   event ID, use `get_meeting_by_id`.
2. Extract attendee emails and call `search_emails_by_attendees` for recent context.
3. Call `search_drive_documents` with keywords from the meeting title and org names.
4. If it's a customer meeting, call `get_customer_profile` with the client name.
5. Synthesise everything into the meeting brief below.

**Meeting Brief Format** (Markdown):

# Meeting Brief: [Meeting Title]
**Date/Time**: [Date], [Time] ET | **Duration**: [Duration]
**Location/Link**: [Location or video link]
**Attendees**: {List with names, titles, organisations}
**Meeting Type**: Internal | Customer | External Partner

## Objective
One sentence on the meeting goal.

## Agenda (Suggested)
Numbered items with time allocation.

## Talking Track
Per agenda item: key message, data points, anticipated questions.

## Background
- Client/stakeholder profile (AUM, mandate, relationship history)
- Recent communications summary
- Applicable SSIM products or strategies

## Key Documents
List relevant Drive docs with links.

## Pre-Meeting Action Items
What must be done before the meeting.

## Open Items / Follow-up Tracker
Outstanding items from prior meetings.

**For customer meetings**, always include:
- Client's investment mandate and risk profile
- Current SSIM strategies invested in
- Any RFP, mandate review, or re-allocation risk
- Competitive context if known
- Suggested next steps and commitment asks

Tone: Executive-ready, specific, data-driven. No filler.
"""

root_agent = Agent(
    name="meeting_prep_agent",
    model=Gemini(
        model="gemini-2.0-flash-001",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_PROMPT,
    tools=[
        search_calendar_events,
        get_meeting_by_id,
        search_emails_by_attendees,
        search_drive_documents,
        get_drive_document_content,
        get_customer_profile,
    ],
)

app = App(
    root_agent=root_agent,
    name="meeting_prep_app",
)
