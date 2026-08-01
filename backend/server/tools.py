# ruff: noqa
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

"""
ADK function tools for the FinTechCo assistant. Each is a thin wrapper that calls
:mod:`server.logic` against the shared :data:`server.store.STORE` and returns a
JSON string. Writes here are what make the Jira / Salesforce / Rooms tabs update.
"""

import json

from server import logic
from server.store import STORE


# ─── Daily briefing / meeting prep ──────────────────────────────────────────

def get_daily_briefing() -> str:
    """Get today's schedule, priority emails, market context, and meeting suggestions."""
    return json.dumps(logic.briefing_summary(STORE), indent=2, default=str)


def suggest_meetings_to_schedule() -> str:
    """Suggest meetings that should be scheduled but are not yet on the calendar."""
    s = logic.suggest_meetings(STORE)
    return json.dumps({"suggestion_count": len(s), "suggestions": s}, indent=2, default=str)


def get_meeting_prep(event_id: str = "", meeting_title: str = "") -> str:
    """Assemble a full prep brief for one meeting (attendees, client profile, emails, docs).

    Args:
        event_id: Calendar event id (preferred). Optional.
        meeting_title: Meeting title or substring, if the id is unknown.
    """
    return json.dumps(logic.meeting_prep(STORE, event_id, meeting_title), indent=2, default=str)


# ─── Market intelligence (public-company customers) ─────────────────────────

def get_sec_filings(company_or_ticker: str, form_type: str = "") -> str:
    """Recent SEC EDGAR filings (10-K / 10-Q / 8-K) for a public customer.

    Use this for a client's latest earnings report or annual/quarterly filing when
    prepping for a meeting or renewal. Live from SEC EDGAR with a mock fallback
    (each response carries a "source" of "live" or "mock").

    Args:
        company_or_ticker: Customer name or ticker (e.g. "Williams-Sonoma", "WSM", "Etsy").
        form_type: Optional filter — "10-K", "10-Q", or "8-K". Omit for the latest of each.
    """
    return json.dumps(logic.sec_filings(STORE, company_or_ticker, form_type), indent=2, default=str)


def get_stock_snapshot(company_or_ticker: str) -> str:
    """Live stock quote, price move, next earnings date, and headlines for a public customer.

    Use this for market context on a client (share price, upcoming earnings, recent news)
    ahead of a meeting. Live from Yahoo Finance with a mock fallback (each response carries
    a "source" of "live" or "mock").

    Args:
        company_or_ticker: Customer name or ticker (e.g. "Dave", "DAVE", "Etsy").
    """
    return json.dumps(logic.stock_snapshot(STORE, company_or_ticker), indent=2, default=str)


# ─── Rooms ──────────────────────────────────────────────────────────────────

def list_available_rooms(date: str, start_time: str, end_time: str,
                         min_capacity: int = 0, building: str = "") -> str:
    """List meeting rooms free for a window.

    Args:
        date: YYYY-MM-DD.
        start_time: HH:MM (24h).
        end_time: HH:MM (24h).
        min_capacity: Minimum seats required. Default 0.
        building: Optional building filter.
    """
    rooms = logic.list_available_rooms(STORE, date, start_time, end_time, min_capacity, building)
    return json.dumps({"available_count": len(rooms), "available_rooms": rooms}, indent=2)


def assign_meeting_room(attendee_emails: str, date: str, start_time: str,
                        end_time: str, min_capacity: int = 0) -> str:
    """Auto-pick the best-fit free room by capacity and attendee seat proximity.

    Args:
        attendee_emails: Comma-separated attendee emails.
        date: YYYY-MM-DD.
        start_time: HH:MM (24h).
        end_time: HH:MM (24h).
        min_capacity: Minimum seats required. Defaults to attendee count.
    """
    attendees = [e.strip() for e in attendee_emails.split(",") if e.strip()]
    return json.dumps(
        logic.assign_room(STORE, attendees, date, start_time, end_time, min_capacity),
        indent=2,
    )


def book_room(room_id: str, event_title: str, date: str, start_time: str,
              end_time: str, organizer: str = "") -> str:
    """Book a room (WRITE — confirm with the user first).

    Args:
        room_id: Room id from assign/list.
        event_title: Meeting title.
        date: YYYY-MM-DD.
        start_time: HH:MM (24h).
        end_time: HH:MM (24h).
        organizer: Organizer email. Optional.
    """
    return json.dumps(
        logic.book_room(STORE, room_id, event_title, date, start_time, end_time, organizer),
        indent=2,
    )


def schedule_meeting(title: str, attendee_emails: str, date: str,
                     start_time: str, end_time: str, room_id: str = "") -> str:
    """Schedule a meeting: create the calendar event AND book a room (WRITE — confirm first).

    Args:
        title: Meeting title.
        attendee_emails: Comma-separated attendee emails.
        date: YYYY-MM-DD.
        start_time: HH:MM (24h).
        end_time: HH:MM (24h).
        room_id: Specific room id to book (from list_available_rooms/assign_meeting_room).
            Optional — omit to auto-pick the best-fit room.
    """
    attendees = [e.strip() for e in attendee_emails.split(",") if e.strip()]
    return json.dumps(
        logic.schedule_meeting(STORE, title, attendees, date, start_time, end_time, room_id or None),
        indent=2, default=str,
    )


# ─── Jira (write) ───────────────────────────────────────────────────────────

def create_jira_tasks(project: str, task_titles: str, assignee: str = "",
                      priority: str = "Medium") -> str:
    """Create Jira issues in the To Do column (WRITE — confirm first). Updates the Jira board.

    Args:
        project: Jira project key (use "FTC").
        task_titles: Task titles, one per line or separated by ';'.
        assignee: Assignee name. Optional.
        priority: High / Medium / Low. Default Medium.
    """
    return json.dumps(
        logic.create_jira_tasks(STORE, project, task_titles, assignee, priority), indent=2
    )


# ─── Salesforce (write) ─────────────────────────────────────────────────────

def log_salesforce_activity(account: str, activity_type: str, summary: str) -> str:
    """Log a Salesforce activity against an account (WRITE — confirm first). Updates the CRM.

    Args:
        account: Account name (e.g. "Williams-Sonoma, Inc.").
        activity_type: Call / Email / Meeting / Note.
        summary: One-line summary of the interaction.
    """
    return json.dumps(logic.log_salesforce_activity(STORE, account, activity_type, summary), indent=2)


def update_opportunity(opportunity_id: str, stage: str = "", amount: str = "") -> str:
    """Update a Salesforce opportunity's stage and/or amount (WRITE — confirm first).

    Args:
        opportunity_id: Opportunity id or name.
        stage: New stage (e.g. Qualification / Proposal / Negotiation / Closed Won). Optional.
        amount: New amount string. Optional.
    """
    return json.dumps(logic.update_opportunity(STORE, opportunity_id, stage, amount), indent=2)


ALL_TOOLS = [
    get_daily_briefing,
    suggest_meetings_to_schedule,
    get_meeting_prep,
    get_sec_filings,
    get_stock_snapshot,
    list_available_rooms,
    assign_meeting_room,
    book_room,
    schedule_meeting,
    create_jira_tasks,
    log_salesforce_activity,
    update_opportunity,
]
