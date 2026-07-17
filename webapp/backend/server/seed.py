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
Seed data for the SSIM assistant demo store.

The SSIM domain data (calendar, emails, market, Drive docs, customer profiles,
rooms, seat locations, meeting suggestions) is the single source of truth living
in ``daily_briefing/app/mock_data.py`` — we load that module directly so the demo
never drifts from the agent. Jira and Salesforce state are demo-only and defined
here.
"""

import copy
import datetime
import importlib.util
import os

_DB_MOCK_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "daily_briefing", "app", "mock_data.py"
    )
)


def _load_db_mock():
    """Load daily_briefing/app/mock_data.py by path (it only imports datetime)."""
    spec = importlib.util.spec_from_file_location("ssim_db_mock", _DB_MOCK_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seed_jira(today: str) -> dict:
    return {
        "project": "SSIM",
        "columns": ["To Do", "In Progress", "Done"],
        "issues": [
            {"id": "SSIM-101", "key": "SSIM-101", "project": "SSIM",
             "title": "Prepare Q2 attribution pack for CalPERS review",
             "description": "Finalise Q2 attribution (+12 bps) and fee schedule for the 10am review.",
             "assignee": "James Okonkwo", "status": "In Progress", "priority": "High",
             "created": today},
            {"id": "SSIM-102", "key": "SSIM-102", "project": "SSIM",
             "title": "MSCI World rebalance — execution schedule",
             "description": "Coordinate ~$2.1B flow with trading desk before June 2 effective date.",
             "assignee": "James Okonkwo", "status": "To Do", "priority": "High",
             "created": today},
            {"id": "SSIM-103", "key": "SSIM-103", "project": "SSIM",
             "title": "Update composite performance presentations (SEC Marketing Rule)",
             "description": "Compliance review due Friday COB before external distribution.",
             "assignee": "Sarah Chen", "status": "To Do", "priority": "Medium",
             "created": today},
            {"id": "SSIM-104", "key": "SSIM-104", "project": "SSIM",
             "title": "OTPP final pitch deck — risk management lead",
             "description": "Reorder deck to lead with risk framework for CIO Priya Mehta.",
             "assignee": "Peter Walsh", "status": "In Progress", "priority": "High",
             "created": today},
            {"id": "SSIM-105", "key": "SSIM-105", "project": "SSIM",
             "title": "GIC pre-read pack (ESG policy, proxy record, Article 8/9 list)",
             "description": "Send before tomorrow's scoping call.",
             "assignee": "Dev", "status": "Done", "priority": "Medium",
             "created": today},
        ],
    }


def _seed_salesforce(today: str) -> dict:
    plus_30 = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    return {
        "accounts": [
            {"id": "acc_calpers", "name": "CalPERS", "type": "Public Pension Fund",
             "aum": "$490B", "owner": "Sarah Chen", "status": "Active Client"},
            {"id": "acc_otpp", "name": "Ontario Teachers' Pension Plan", "type": "Public Pension Fund",
             "aum": "$255B CAD", "owner": "Peter Walsh", "status": "Prospect — RFP Finalist"},
            {"id": "acc_gic", "name": "GIC", "type": "Sovereign Wealth Fund",
             "aum": "$770B+", "owner": "Dev", "status": "Prospect — Scoping"},
            {"id": "acc_mercer", "name": "Mercer", "type": "Investment Consultant",
             "aum": "—", "owner": "Peter Walsh", "status": "Consultant"},
        ],
        "opportunities": [
            {"id": "opp_calpers", "account": "CalPERS",
             "name": "Global Equity Passive — Mandate Renewal", "stage": "Negotiation",
             "amount": "$8.2B", "close_date": "2026-12-31"},
            {"id": "opp_calpers_em", "account": "CalPERS",
             "name": "Emerging Markets Allocation", "stage": "Qualification",
             "amount": "$0.5B", "close_date": ""},
            {"id": "opp_otpp", "account": "Ontario Teachers' Pension Plan",
             "name": "Active Quantitative Equity Mandate", "stage": "Proposal",
             "amount": "$2.0B", "close_date": plus_30},
            {"id": "opp_gic", "account": "GIC",
             "name": "ESG Global Equity Mandate", "stage": "Qualification",
             "amount": "$5.0B", "close_date": ""},
        ],
        "activities": [
            {"id": "act_001", "account": "CalPERS", "type": "Email",
             "summary": "Michael Torres requested Q2 attribution + fee schedule before the review.",
             "date": today},
            {"id": "act_002", "account": "Ontario Teachers' Pension Plan", "type": "Note",
             "summary": "CIO Priya Mehta joining final pitch — lead with risk management.",
             "date": today},
            {"id": "act_003", "account": "GIC", "type": "Email",
             "summary": "Pre-call questions received: ESG policy, proxy record, carbon footprint.",
             "date": today},
        ],
    }


def build_seed() -> dict:
    """Return a fresh, fully-independent copy of the demo state."""
    m = _load_db_mock()
    today = datetime.date.today().isoformat()
    return {
        "date": today,
        "calendar_events": copy.deepcopy(m.MOCK_CALENDAR_EVENTS),
        "emails": copy.deepcopy(m.MOCK_EMAILS),
        "market": copy.deepcopy(m.MOCK_MARKET_CONTEXT),
        "drive_docs": copy.deepcopy(m.MOCK_DRIVE_DOCS),
        "customer_profiles": copy.deepcopy(m.MOCK_CUSTOMER_PROFILES),
        "rooms": copy.deepcopy(m.MOCK_ROOMS),
        "employee_locations": copy.deepcopy(m.MOCK_EMPLOYEE_LOCATIONS),
        "room_bookings": copy.deepcopy(m.MOCK_ROOM_BOOKINGS),
        "meeting_suggestions": copy.deepcopy(m.MOCK_MEETING_SUGGESTIONS),
        "jira": _seed_jira(today),
        "salesforce": _seed_salesforce(today),
    }
