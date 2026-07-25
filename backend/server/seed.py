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
in :mod:`server.mock_data`. Jira and Salesforce state are demo-only and defined
here.
"""

import copy
import datetime

from server import mock_data


def _seed_jira(today: str) -> dict:
    return {
        "project": "SSIM",
        "columns": ["To Do", "In Progress", "Done"],
        "issues": [
            {"id": "SSIM-101", "key": "SSIM-101", "project": "SSIM",
             "title": "Prepare Q2 payments performance pack for Williams-Sonoma review",
             "description": "Finalise Q2 authorization/chargeback metrics and fee schedule for the 10am review.",
             "assignee": "James Okonkwo", "status": "In Progress", "priority": "High",
             "created": today},
            {"id": "SSIM-102", "key": "SSIM-102", "project": "SSIM",
             "title": "Card network rule change — rollout schedule",
             "description": "Coordinate ~$2.1B in affected TPV with the platform team before the June 2 effective date.",
             "assignee": "James Okonkwo", "status": "To Do", "priority": "High",
             "created": today},
            {"id": "SSIM-103", "key": "SSIM-103", "project": "SSIM",
             "title": "Update uptime/SLA performance decks (SOC 2 review)",
             "description": "Compliance review due Friday COB before external distribution.",
             "assignee": "Sarah Chen", "status": "To Do", "priority": "Medium",
             "created": today},
            {"id": "SSIM-104", "key": "SSIM-104", "project": "SSIM",
             "title": "Etsy final pitch deck — risk & fraud lead",
             "description": "Reorder deck to lead with fraud/risk management for VP of Payments Divya Nair.",
             "assignee": "Peter Walsh", "status": "In Progress", "priority": "High",
             "created": today},
            {"id": "SSIM-105", "key": "SSIM-105", "project": "SSIM",
             "title": "Dave pre-read pack (BSA/AML program, KYC flow, compliance DDQ)",
             "description": "Send before tomorrow's scoping call.",
             "assignee": "Dev", "status": "Done", "priority": "Medium",
             "created": today},
        ],
    }


def _seed_salesforce(today: str) -> dict:
    plus_30 = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    return {
        "accounts": [
            {"id": "acc_wsm", "name": "Williams-Sonoma, Inc.", "type": "Enterprise Merchant",
             "scale": "$8B TPV", "owner": "Sarah Chen", "status": "Active Client"},
            {"id": "acc_etsy", "name": "Etsy, Inc.", "type": "Enterprise Merchant",
             "scale": "$13B projected TPV", "owner": "Peter Walsh", "status": "Prospect — RFP Finalist"},
            {"id": "acc_dave", "name": "Dave Inc.", "type": "BaaS Partner",
             "scale": "$500M program deposits", "owner": "Dev", "status": "Prospect — Scoping"},
            {"id": "acc_glenbrook", "name": "Glenbrook Partners", "type": "Payments Advisory Firm",
             "scale": "—", "owner": "Peter Walsh", "status": "Consultant"},
        ],
        "opportunities": [
            {"id": "opp_wsm", "account": "Williams-Sonoma, Inc.",
             "name": "Payment Gateway — Processing Agreement Renewal", "stage": "Negotiation",
             "amount": "$8B TPV", "close_date": "2026-12-31"},
            {"id": "opp_wsm_rtp", "account": "Williams-Sonoma, Inc.",
             "name": "Real-Time Payments Add-on", "stage": "Qualification",
             "amount": "$0.5B TPV", "close_date": ""},
            {"id": "opp_etsy", "account": "Etsy, Inc.",
             "name": "Payments + Embedded Lending (BaaS)", "stage": "Proposal",
             "amount": "$13B TPV", "close_date": plus_30},
            {"id": "opp_dave", "account": "Dave Inc.",
             "name": "Banking-as-a-Service Program", "stage": "Qualification",
             "amount": "$500M deposits", "close_date": ""},
        ],
        "activities": [
            {"id": "act_001", "account": "Williams-Sonoma, Inc.", "type": "Email",
             "summary": "Requested Q2 authorization/chargeback metrics + fee schedule before the review.",
             "date": today},
            {"id": "act_002", "account": "Etsy, Inc.", "type": "Note",
             "summary": "VP of Payments Divya Nair joining final pitch — lead with fraud/risk management.",
             "date": today},
            {"id": "act_003", "account": "Dave Inc.", "type": "Email",
             "summary": "Pre-call questions received: BSA/AML program, KYC flow, compliance DDQ.",
             "date": today},
        ],
    }


def build_seed() -> dict:
    """Return a fresh, fully-independent copy of the demo state."""
    m = mock_data
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
