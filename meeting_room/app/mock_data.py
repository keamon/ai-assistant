"""
Mock data for Meeting Room Booking Agent — State Street Investment Management.
Simulates the corporate room inventory, employee seat locations, and the
existing booking ledger. Buildings/floors are consistent with the seat
locations of people referenced by the other SSIM agents.
"""

import datetime

_TODAY = datetime.date.today().isoformat()
_TOMORROW = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

# ─── Room inventory ────────────────────────────────────────────────────────────
# Buildings: "One Congress" (Boston HQ), "Channel Center" (Boston), "Toronto"
MOCK_ROOMS = [
    {
        "id": "room_bos1_4a",
        "name": "Conference Room 4A",
        "building": "One Congress",
        "floor": 4,
        "capacity": 8,
        "equipment": ["display", "video_conf", "whiteboard"],
        "av": True,
    },
    {
        "id": "room_bos1_4b",
        "name": "Huddle 4B",
        "building": "One Congress",
        "floor": 4,
        "capacity": 4,
        "equipment": ["display"],
        "av": False,
    },
    {
        "id": "room_bos1_12",
        "name": "Fenway Boardroom",
        "building": "One Congress",
        "floor": 12,
        "capacity": 20,
        "equipment": ["display", "video_conf", "whiteboard", "speakerphone"],
        "av": True,
    },
    {
        "id": "room_bos1_7",
        "name": "Beacon Room",
        "building": "One Congress",
        "floor": 7,
        "capacity": 12,
        "equipment": ["display", "video_conf", "whiteboard"],
        "av": True,
    },
    {
        "id": "room_bos2_3",
        "name": "Harbor View",
        "building": "Channel Center",
        "floor": 3,
        "capacity": 10,
        "equipment": ["display", "video_conf"],
        "av": True,
    },
    {
        "id": "room_bos2_6",
        "name": "Seaport Suite",
        "building": "Channel Center",
        "floor": 6,
        "capacity": 6,
        "equipment": ["display", "video_conf", "whiteboard"],
        "av": True,
    },
    {
        "id": "room_tor_18",
        "name": "CN Tower Room",
        "building": "Toronto",
        "floor": 18,
        "capacity": 14,
        "equipment": ["display", "video_conf", "whiteboard"],
        "av": True,
    },
    {
        "id": "room_tor_18b",
        "name": "Lakeshore Huddle",
        "building": "Toronto",
        "floor": 18,
        "capacity": 4,
        "equipment": ["display"],
        "av": False,
    },
]

# ─── Employee seat locations ───────────────────────────────────────────────────
# Keyed by email. Covers the SSIM colleagues referenced across the other agents.
MOCK_EMPLOYEE_LOCATIONS = [
    {"email": "dev@chenkeamonwang.altostrat.com", "name": "Dev (You)", "building": "One Congress", "floor": 7, "seat": "7-114"},
    {"email": "sarah.chen@statestreet.com", "name": "Sarah Chen", "building": "One Congress", "floor": 7, "seat": "7-102"},
    {"email": "james.okonkwo@statestreet.com", "name": "James Okonkwo", "building": "One Congress", "floor": 4, "seat": "4-210"},
    {"email": "anna.petrov@statestreet.com", "name": "Anna Petrov", "building": "One Congress", "floor": 12, "seat": "12-045"},
    {"email": "mark.johnson@statestreet.com", "name": "Mark Johnson", "building": "Channel Center", "floor": 3, "seat": "3-330"},
    {"email": "lisa.huang@statestreet.com", "name": "Lisa Huang", "building": "Channel Center", "floor": 6, "seat": "6-118"},
    {"email": "robert.kim@statestreet.com", "name": "Robert Kim", "building": "One Congress", "floor": 7, "seat": "7-131"},
    {"email": "peter.walsh@statestreet.com", "name": "Peter Walsh", "building": "Toronto", "floor": 18, "seat": "18-204"},
]

# ─── Existing bookings (so availability is non-trivial) ─────────────────────────
MOCK_ROOM_BOOKINGS = [
    {
        "id": "bk_001",
        "room_id": "room_bos1_4a",
        "event_title": "Morning Portfolio Review — Global Equity Index Team",
        "date": _TODAY,
        "start": f"{_TODAY}T08:30:00-04:00",
        "end": f"{_TODAY}T09:00:00-04:00",
        "organizer": "james.okonkwo@statestreet.com",
    },
    {
        "id": "bk_002",
        "room_id": "room_bos1_12",
        "event_title": "Fenway Boardroom — Client Off-site",
        "date": _TODAY,
        "start": f"{_TODAY}T10:00:00-04:00",
        "end": f"{_TODAY}T12:00:00-04:00",
        "organizer": "peter.walsh@statestreet.com",
    },
    {
        "id": "bk_003",
        "room_id": "room_bos1_7",
        "event_title": "Risk Committee — Weekly Standup",
        "date": _TODAY,
        "start": f"{_TODAY}T16:30:00-04:00",
        "end": f"{_TODAY}T17:00:00-04:00",
        "organizer": "james.okonkwo@statestreet.com",
    },
    {
        "id": "bk_004",
        "room_id": "room_bos2_3",
        "event_title": "ESG Data Vendor Demo",
        "date": _TOMORROW,
        "start": f"{_TOMORROW}T09:00:00-04:00",
        "end": f"{_TOMORROW}T10:00:00-04:00",
        "organizer": "anna.petrov@statestreet.com",
    },
]
