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

"""Tests for the market-data layer's offline/mock-fallback behaviour.

With ``DEMO_DISABLE_LIVE_MARKET=1`` (set in conftest) every call must skip the
network and return the baked-in fixtures tagged ``source="mock"``.
"""

import pytest

from server import market_data


def test_live_disabled_in_tests():
    assert market_data._live_disabled() is True


@pytest.mark.parametrize("ticker,cik", [("WSM", "0000719955"), ("ETSY", "0001370637"), ("DAVE", "0001841408")])
def test_get_sec_filings_mock(ticker, cik):
    res = market_data.get_sec_filings(ticker, cik)
    assert res["source"] == "mock"
    assert res["ticker"] == ticker
    assert len(res["filings"]) >= 1
    forms = {f["form"] for f in res["filings"]}
    assert forms <= {"10-K", "10-Q", "8-K"}
    for f in res["filings"]:
        assert f["url"].startswith("https://www.sec.gov/")


def test_get_sec_filings_form_filter():
    res = market_data.get_sec_filings("WSM", "0000719955", form_type="10-Q")
    assert res["source"] == "mock"
    assert res["filings"]
    assert all(f["form"] == "10-Q" for f in res["filings"])


def test_get_sec_filings_unknown_ticker():
    res = market_data.get_sec_filings("ZZZZ", "0000000000")
    assert res["source"] == "mock"
    assert res["filings"] == []


@pytest.mark.parametrize("ticker", ["WSM", "ETSY", "DAVE"])
def test_get_stock_snapshot_mock(ticker):
    snap = market_data.get_stock_snapshot(ticker)
    assert snap["source"] == "mock"
    assert snap["ticker"] == ticker
    assert isinstance(snap["quote"].get("price"), (int, float))
    assert snap["next_earnings_date"]
    assert isinstance(snap["news"], list)


def test_get_stock_snapshot_unknown_ticker():
    snap = market_data.get_stock_snapshot("ZZZZ")
    assert snap["source"] == "mock"
    assert snap["quote"] == {}


def test_get_stock_snapshot_falls_back_to_mock_when_yahoo_fails(monkeypatch):
    monkeypatch.setattr(market_data, "_live_disabled", lambda: False)

    def yahoo_fails(*args, **kwargs):
        raise OSError("crumb handshake refused")

    monkeypatch.setattr(market_data, "_yahoo_get_json", yahoo_fails)
    snap = market_data.get_stock_snapshot("WSM")
    assert snap["source"] == "mock"
