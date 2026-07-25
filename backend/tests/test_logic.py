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

"""Tests for the pure logic layer — company resolution, market intelligence,
briefing/prep assembly, and demo write actions."""

import pytest

from server import logic


# ─── Company resolution ─────────────────────────────────────────────────────

@pytest.mark.parametrize("query,expected_ticker", [
    ("WSM", "WSM"),
    ("wsm", "WSM"),
    ("Williams-Sonoma", "WSM"),
    ("etsy", "ETSY"),
    ("Dave", "DAVE"),
])
def test_resolve_company_public(store, query, expected_ticker):
    p = logic._resolve_company(store, query)
    assert p is not None
    assert p["ticker"] == expected_ticker


def test_resolve_company_private(store):
    p = logic._resolve_company(store, "Glenbrook")
    assert p is not None
    assert p.get("public") is False
    assert not p.get("ticker")


def test_resolve_company_unknown(store):
    assert logic._resolve_company(store, "Nonexistent Corp") is None


# ─── SEC filings ────────────────────────────────────────────────────────────

def test_sec_filings_public(store):
    res = logic.sec_filings(store, "Williams-Sonoma")
    assert res["source"] == "mock"  # offline in tests
    assert res["ticker"] == "WSM"
    assert res["filings"]


def test_sec_filings_private_company(store):
    res = logic.sec_filings(store, "Glenbrook")
    assert res["public"] is False
    assert "no SEC filings" in res["message"]


def test_sec_filings_unknown(store):
    res = logic.sec_filings(store, "Nonexistent Corp")
    assert "error" in res


def test_sec_filings_cached(store):
    logic.sec_filings(store, "ETSY")
    assert "ETSY:" in store.sec_cache


# ─── Stock snapshot ─────────────────────────────────────────────────────────

def test_stock_snapshot_public(store):
    snap = logic.stock_snapshot(store, "DAVE")
    assert snap["ticker"] == "DAVE"
    assert snap["source"] == "mock"
    assert snap["quote"]["price"]
    assert "DAVE" in store.stock_cache


def test_stock_snapshot_private(store):
    snap = logic.stock_snapshot(store, "Glenbrook")
    assert snap["public"] is False


# ─── Public-company watch + briefing ────────────────────────────────────────

def test_public_company_watch(store):
    rows = logic.public_company_watch(store)
    assert len(rows) == 3  # WSM, ETSY, DAVE (Glenbrook excluded — private)
    tickers = {r["ticker"] for r in rows}
    assert tickers == {"WSM", "ETSY", "DAVE"}
    for r in rows:
        assert r["price"]
        assert r["next_earnings_date"]
        assert r["latest_filing"]["form"] in {"10-K", "10-Q", "8-K"}


def test_briefing_summary_includes_watch(store):
    b = logic.briefing_summary(store)
    assert "public_company_watch" in b
    assert len(b["public_company_watch"]) == 3


# ─── Meeting prep enrichment ────────────────────────────────────────────────

def test_meeting_prep_customer_enriched(store):
    prep = logic.meeting_prep(store, event_id="cal_002")  # Williams-Sonoma
    assert prep["is_customer_meeting"] is True
    assert prep["customer_profile"]["ticker"] == "WSM"
    assert prep["stock_snapshot"] is not None
    assert prep["stock_snapshot"]["ticker"] == "WSM"
    assert prep["latest_filing"]["form"] in {"10-K", "10-Q", "8-K"}


def test_meeting_prep_internal_not_enriched(store):
    prep = logic.meeting_prep(store, event_id="cal_003")  # internal working group
    assert prep["is_customer_meeting"] is False
    assert prep["stock_snapshot"] is None
    assert prep["latest_filing"] is None


# ─── Demo write actions ─────────────────────────────────────────────────────

def test_log_salesforce_activity_prepends(store):
    before = len(store.salesforce["activities"])
    out = logic.log_salesforce_activity(store, "Williams-Sonoma, Inc.", "Call", "Q3 review call")
    assert out["logged"] is True
    assert len(store.salesforce["activities"]) == before + 1
    assert store.salesforce["activities"][0]["account"] == "Williams-Sonoma, Inc."


def test_create_jira_tasks(store):
    before = len(store.jira["issues"])
    out = logic.create_jira_tasks(store, "SSIM", "Task one\nTask two", "Dev", "High")
    assert len(store.jira["issues"]) == before + 2
    assert out["created_count"] == 2
