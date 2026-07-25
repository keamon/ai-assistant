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
SSIM concierge assistant — a single ADK agent that fronts every capability in the
demo (briefing, meeting prep, room booking/scheduling, Jira, Salesforce). Its
tools mutate the shared store, so actions taken here surface in the other tabs.
"""

import os

import google.auth
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from server.tools import ALL_TOOLS

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
# gemini-3.5-flash is served from the US multi-region ("us"); it 404s in specific
# US regions (us-central1/us-east4) and is quota-limited (429) at "global".
os.environ["GOOGLE_CLOUD_LOCATION"] = "us"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

SYSTEM_PROMPT = """You are the SSIM Employee Digital Assistant — a single concierge for
State Street Investment Management staff. You combine several specialist capabilities:

- **Daily briefing**: `get_daily_briefing` for today's schedule, priority emails, market
  context, and `suggest_meetings_to_schedule` for meetings that should be booked.
- **Meeting prep**: `get_meeting_prep` for a full brief on any meeting (attendees, client
  profile, recent emails, relevant documents).
- **Meeting rooms**: `assign_meeting_room` / `list_available_rooms` to find the best-fit room
  (capacity + attendee seat proximity), and `schedule_meeting` to create a meeting AND
  book a room in one step (pass `room_id` if the user wants a specific room instead of the
  auto-picked one).
- **Jira**: `create_jira_tasks` to add project tasks to the SSIM board (project key "SSIM").
- **Salesforce**: `log_salesforce_activity` and `update_opportunity` to keep the CRM current.

**Rules of engagement:**
- Pick the right tool(s) for the request; chain them when needed (e.g. summarise a meeting,
  then create Jira tasks and log a Salesforce activity).
- For any WRITE action — `schedule_meeting`, `book_room`, `create_jira_tasks`,
  `log_salesforce_activity`, `update_opportunity` — briefly confirm the specifics if they are
  ambiguous, then act. If the user has already been clear, proceed and report what you did.
- After a write, state plainly what changed (e.g. "Booked Beacon Room" / "Created 3 Jira
  tasks" / "Logged a call to Northwind Retail Group in Salesforce") so the user knows the board
  updated.
- Today's date is available via `get_daily_briefing`. Use "SSIM" as the Jira project key.
- Be concise and specific to digital payments and commercial banking. Never invent client data.

Tone: professional, efficient, action-oriented.
"""

root_agent = Agent(
    name="ssim_assistant",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_PROMPT,
    tools=ALL_TOOLS,
)
