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
Shared, in-process mutable state for the FinTechCo assistant demo.

Both the agent tools (writes) and the FastAPI read endpoints (reads) operate on
the single ``STORE`` instance, so an assistant action is immediately reflected in
the Jira / Salesforce / Rooms / Calendar tabs.
"""

from server import seed


class Store:
    """Mutable demo state, seeded from :mod:`server.seed`."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        data = seed.build_seed()
        self.date = data["date"]
        self.calendar_events = data["calendar_events"]
        self.emails = data["emails"]
        self.market = data["market"]
        self.drive_docs = data["drive_docs"]
        self.customer_profiles = data["customer_profiles"]
        self.rooms = data["rooms"]
        self.employee_locations = data["employee_locations"]
        self.room_bookings = data["room_bookings"]
        self.meeting_suggestions = data["meeting_suggestions"]
        self.jira = data["jira"]
        self.salesforce = data["salesforce"]
        # LLM generation caches (generated once, cleared on reset)
        self.briefing_narrative: str | None = None
        self.prep_cache: dict[str, dict] = {}
        # Live market-data caches (SEC filings + stock snapshots), cleared on reset
        self.sec_cache: dict[str, dict] = {}
        self.stock_cache: dict[str, dict] = {}
        # SpaceX index-inclusion case study cache (dashboard payload + narrative), cleared on reset
        self.spacex_cache: dict | None = None
        self.spacex_narrative: str | None = None


# Single process-wide instance.
STORE = Store()
