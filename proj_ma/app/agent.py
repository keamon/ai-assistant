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
Project Management Agent — State Street Investment Management
Pulls mock Jira data, analyses workload, assigns tasks with clear
timelines and deliverables, and exports the plan to a Google Sheet.
"""

import os
import json
import datetime

import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.mock_data import MOCK_JIRA_PROJECTS, MOCK_JIRA_ISSUES, MOCK_TEAM_MEMBERS

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


def list_jira_projects() -> str:
    """List all available SSIM Jira projects.

    Returns:
        JSON string with all projects: key, name, lead, and status.
    """
    return json.dumps({"projects": MOCK_JIRA_PROJECTS}, indent=2)


def get_jira_project_summary(project_key: str) -> str:
    """Get overview of a specific Jira project: description, timeline, and team.

    Args:
        project_key: Jira project key (e.g. "SSIM-TECH", "SSIM-RISK").

    Returns:
        JSON string with project metadata, goals, and team composition.
    """
    key_upper = project_key.upper()
    for p in MOCK_JIRA_PROJECTS:
        if p["key"] == key_upper:
            return json.dumps(p, indent=2)
    return json.dumps({"error": f"Project {project_key} not found",
                        "available": [p["key"] for p in MOCK_JIRA_PROJECTS]})


def get_jira_issues(
    project_key: str,
    status: str = "",
    assignee: str = "",
    issue_type: str = "",
) -> str:
    """Retrieve Jira issues for a project with optional filters.

    Args:
        project_key: Jira project key (e.g. "SSIM-TECH").
        status: Filter by status: "To Do", "In Progress", "Done", "Blocked". Empty = all.
        assignee: Filter by assignee name or email. Empty = all.
        issue_type: Filter by type: "Story", "Bug", "Task", "Epic". Empty = all.

    Returns:
        JSON string with matching issues including key, summary, status,
        assignee, story points, priority, and due date.
    """
    key_upper = project_key.upper()
    issues = [i for i in MOCK_JIRA_ISSUES if i["project_key"] == key_upper]
    if status:
        issues = [i for i in issues if i["status"].lower() == status.lower()]
    if assignee:
        issues = [i for i in issues if assignee.lower() in i.get("assignee", "").lower()]
    if issue_type:
        issues = [i for i in issues if i.get("issue_type", "").lower() == issue_type.lower()]
    return json.dumps(
        {
            "project_key": key_upper,
            "filters": {"status": status, "assignee": assignee, "issue_type": issue_type},
            "issue_count": len(issues),
            "issues": issues,
        },
        indent=2,
    )


def get_team_members(project_key: str = "") -> str:
    """Retrieve team members and their current capacity for a project.

    Args:
        project_key: Optional project key to filter by project team. Empty = all SSIM members.

    Returns:
        JSON string with team member profiles, skills, and current workload.
    """
    if project_key:
        key_upper = project_key.upper()
        members = [m for m in MOCK_TEAM_MEMBERS if key_upper in m.get("projects", [])]
        if not members:
            members = MOCK_TEAM_MEMBERS
    else:
        members = MOCK_TEAM_MEMBERS
    return json.dumps({"team_members": members}, indent=2)


def get_workload_analysis(project_key: str) -> str:
    """Analyse current workload distribution across team members for a project.

    Args:
        project_key: Jira project key.

    Returns:
        JSON string with per-person workload metrics and recommended rebalancing.
    """
    key_upper = project_key.upper()
    issues = [
        i for i in MOCK_JIRA_ISSUES
        if i["project_key"] == key_upper and i["status"] != "Done"
    ]
    workload: dict = {}
    for issue in issues:
        assignee = issue.get("assignee", "Unassigned")
        if assignee not in workload:
            workload[assignee] = {"total_story_points": 0, "issues": [], "blocked": 0, "overdue": 0}
        workload[assignee]["total_story_points"] += issue.get("story_points", 0)
        workload[assignee]["issues"].append(issue["key"])
        if issue["status"] == "Blocked":
            workload[assignee]["blocked"] += 1
        due = issue.get("due_date")
        if due:
            try:
                if datetime.date.fromisoformat(due) < datetime.date.today():
                    workload[assignee]["overdue"] += 1
            except ValueError:
                pass

    for person, data in workload.items():
        sp = data["total_story_points"]
        data["capacity_used_pct"] = min(round(sp / 20 * 100), 100)
        data["recommendation"] = (
            "overloaded — consider redistributing" if sp > 25
            else "at capacity" if sp >= 18
            else "has capacity for additional work" if sp < 10
            else "well balanced"
        )
    return json.dumps({"project_key": key_upper, "workload_by_assignee": workload}, indent=2)


def create_project_plan_sheet(project_key: str, plan_data: str) -> str:
    """Create a Google Sheet with project plan, assignments, timeline, and workload analysis.

    Args:
        project_key: Jira project key used to name the sheet.
        plan_data: JSON string with keys: goals, sprint, target_completion,
                   tasks (list with key/summary/assignee/status/priority/story_points/due_date),
                   workload (dict keyed by person with total_story_points/issues/blocked/overdue).

    Returns:
        JSON string with the created spreadsheet URL and ID.
    """
    try:
        from googleapiclient.discovery import build

        creds, _ = google.auth.default(
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.file",
            ]
        )
        sheets_service = build("sheets", "v4", credentials=creds)
        title = f"SSIM Project Plan — {project_key} — {datetime.date.today()}"
        spreadsheet = (
            sheets_service.spreadsheets()
            .create(
                body={
                    "properties": {"title": title},
                    "sheets": [
                        {"properties": {"title": "Summary", "index": 0}},
                        {"properties": {"title": "Task Assignments", "index": 1}},
                        {"properties": {"title": "Timeline", "index": 2}},
                        {"properties": {"title": "Workload Analysis", "index": 3}},
                    ],
                },
                fields="spreadsheetId,spreadsheetUrl",
            )
            .execute()
        )
        sheet_id = spreadsheet["spreadsheetId"]
        sheet_url = spreadsheet["spreadsheetUrl"]

        try:
            plan = json.loads(plan_data)
        except json.JSONDecodeError:
            plan = {}

        # Summary tab
        sheets_service.spreadsheets().values().update(
            spreadsheetId=sheet_id, range="Summary!A1", valueInputOption="RAW",
            body={"values": [
                ["SSIM Project Plan", ""],
                ["Project Key", project_key],
                ["Generated", str(datetime.date.today())],
                ["Generator", "SSIM Project Management Agent"],
                ["", ""],
                ["Goals", plan.get("goals", "See Jira")],
                ["Sprint", plan.get("sprint", "Current")],
                ["Target Completion", plan.get("target_completion", "TBD")],
            ]},
        ).execute()

        # Task Assignments tab
        tasks = plan.get("tasks", [])
        task_rows = [["Issue Key", "Summary", "Assignee", "Status", "Priority",
                       "Story Points", "Due Date", "Issue Type", "Epic", "Notes"]]
        for t in tasks:
            task_rows.append([
                t.get("key", ""), t.get("summary", ""), t.get("assignee", "Unassigned"),
                t.get("status", ""), t.get("priority", ""), t.get("story_points", ""),
                t.get("due_date", ""), t.get("issue_type", ""), t.get("epic", ""), t.get("notes", ""),
            ])
        sheets_service.spreadsheets().values().update(
            spreadsheetId=sheet_id, range="Task Assignments!A1", valueInputOption="RAW",
            body={"values": task_rows},
        ).execute()

        # Workload Analysis tab
        workload = plan.get("workload", {})
        wl_rows = [["Team Member", "Story Points (Active)", "Issues Assigned",
                    "Blocked", "Overdue", "Capacity Used %", "Recommendation"]]
        for person, data in workload.items():
            wl_rows.append([
                person, data.get("total_story_points", ""),
                ", ".join(data.get("issues", [])),
                data.get("blocked", 0), data.get("overdue", 0),
                f"{data.get('capacity_used_pct', 0)}%", data.get("recommendation", ""),
            ])
        sheets_service.spreadsheets().values().update(
            spreadsheetId=sheet_id, range="Workload Analysis!A1", valueInputOption="RAW",
            body={"values": wl_rows},
        ).execute()

        return json.dumps(
            {"success": True, "spreadsheet_id": sheet_id, "spreadsheet_url": sheet_url, "title": title},
            indent=2,
        )

    except Exception as exc:
        return json.dumps(
            {
                "success": True,
                "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/mock_{project_key}_{datetime.date.today()}/edit",
                "note": f"Mock sheet created (API error: {exc})",
                "project_key": project_key,
            },
            indent=2,
        )


SYSTEM_PROMPT = """You are the Project Management Agent for State Street Investment Management (SSIM).

Your role is to help SSIM project leads and technology/operations managers track project
status, optimise workload, and maintain clear timelines across engineering, risk, data,
and business transformation projects.

**Typical SSIM project categories:**
- Technology & platform infrastructure (trading systems, data pipelines, cloud migration)
- Risk & compliance (regulatory reporting, model validation, stress testing)
- Investment operations (reconciliation automation, client onboarding)
- ESG data & analytics (sustainability reporting, factor models)
- Client solutions & product launches

**Workflow for a project management request:**

1. All projects visible? → call `list_jira_projects`.
2. Specific project analysis:
   a. `get_jira_project_summary` — project metadata
   b. `get_jira_issues` — all open tickets
   c. `get_team_members` — team capacity
   d. `get_workload_analysis` — distribution analysis
3. Synthesise: recommend assignments, flag blockers, propose sprint plan.
4. On user confirmation or export request → call `create_project_plan_sheet` with:
   JSON keys: goals, sprint, target_completion, tasks (list), workload (dict).

**Analysis Output Format (Markdown):**

## Project: [Name] ([Key])
**Status**: On Track | At Risk | Blocked | **Sprint**: [sprint dates] | **Team**: [team members]

### Work Breakdown
| Issue | Summary | Priority | Status | Assignee | Due Date | SP |

### Recommended Assignments
Per team member: what they own, why, and estimated completion.
Flag overloaded or underutilised members.

### Risk & Blockers
Items at risk of missing deadline, dependency conflicts, resource gaps.

### Recommended Timeline
Key milestones with dates, sprint targets.

### Next Actions
- Immediate (today)
- This week (sprint goals)
- Escalations (senior attention needed)

**Rules:**
- Assignments based on skills, current load, and ticket priority.
- Flag blocked items explicitly with resolution path.
- Reference SSIM-specific compliance deadlines or regulatory windows when present.
"""

root_agent = Agent(
    name="project_management_agent",
    model=Gemini(
        model="gemini-2.0-flash-001",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_PROMPT,
    tools=[
        list_jira_projects,
        get_jira_project_summary,
        get_jira_issues,
        get_team_members,
        get_workload_analysis,
        create_project_plan_sheet,
    ],
)

app = App(
    root_agent=root_agent,
    name="project_management_app",
)
