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
Shared pytest fixtures for the FinTechCo backend suite.

Tests are hermetic: **no network, no live model calls**. We force the
market-data layer into offline/mock mode (``DEMO_DISABLE_LIVE_MARKET=1``)
*before* importing any server module, and monkeypatch the LLM helpers so the
briefing/prep endpoints never call the model. This keeps CI fast and
deterministic.
"""

import os

# Must be set before server.market_data is imported anywhere.
os.environ["DEMO_DISABLE_LIVE_MARKET"] = "1"

import pytest  # noqa: E402

from server import llm  # noqa: E402
from server.store import Store  # noqa: E402


@pytest.fixture
def store():
    """A fresh, isolated demo store per test."""
    return Store()


@pytest.fixture
def client(monkeypatch):
    """FastAPI TestClient with the store reset and the LLM helpers stubbed.

    Stubbing the LLM keeps the ``/api/briefing`` and ``/api/prep`` endpoints
    offline (they otherwise call the model for narrative/talking points).
    """
    from fastapi.testclient import TestClient

    from server import main
    from server.store import STORE

    monkeypatch.setattr(llm, "generate_briefing_narrative", lambda summary: "TEST NARRATIVE")
    monkeypatch.setattr(
        llm,
        "generate_meeting_prep",
        lambda prep: {
            "objective": "TEST OBJECTIVE",
            "agenda": ["a"],
            "talking_points": ["tp"],
            "anticipated_questions": [{"question": "q", "answer": "a"}],
        },
    )
    monkeypatch.setattr(llm, "generate_spacex_narrative", lambda payload: "TEST SPACEX NARRATIVE")

    STORE.reset()
    main._SESSIONS.clear()
    return TestClient(main.app)
