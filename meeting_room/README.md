# meeting-room

Meeting Room Booking agent for State Street Investment Management.

Looks at the room inventory and each attendee's seat location, then auto-assigns the
best-fit room (capacity + proximity) and books it. Agent generated with `agents-cli`.

## Project Structure

```
meeting-room/
├── app/         # Core agent code
│   ├── agent.py               # Room booking tools + agent definition
│   ├── mock_data.py           # Rooms, employee seat locations, booking ledger
│   ├── agent_engine_app.py    # Agent Engine application logic
│   └── app_utils/             # App utilities and helpers
├── tests/                     # Unit, integration, and eval tests
├── GEMINI.md                  # AI-assisted development guide
└── pyproject.toml             # Project dependencies
```

## Tools

| Tool | Purpose |
| ---- | ------- |
| `list_available_rooms` | Rooms free for a time window (capacity/building filters) |
| `get_attendee_locations` | Each attendee's building/floor/seat + remote count |
| `assign_meeting_room` | Auto-pick the best room (capacity + attendee proximity) |
| `book_room` | Book a room (write action — confirm first) |

## Quick Start

```bash
agents-cli install && agents-cli dev
```

Try: *"Assign a room for a 10:00–11:00 meeting today with sarah.chen@statestreet.com,
james.okonkwo@statestreet.com and one external client."*

## Deployment

```bash
gcloud config set project <your-project-id>
agents-cli deploy
```

In this dev environment the room inventory, seat directory, and booking ledger are served
from `app/mock_data.py`. A production build would replace these with Google Workspace
Calendar *resource* calendars and free/busy queries.
