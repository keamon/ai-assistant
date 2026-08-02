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

"""Unit tests for the SpaceX index-inclusion case study logic (offline: market
data forced into mock mode by conftest's DEMO_DISABLE_LIVE_MARKET=1)."""

from server import spacex_case_study as spx
from server import spacex_reference_data as ref


def test_get_price_series_falls_back_to_mock_when_live_disabled():
    result = spx.get_price_series(ref.SPCX_TICKER, ref.SPCX_PRICES)
    assert result["source"] == "mock"
    assert result["prices"] == ref.SPCX_PRICES


def test_get_filings_falls_back_to_mock_when_live_disabled():
    result = spx.get_filings()
    assert result["source"] == "mock"
    assert result["ticker"] == ref.SPCX_TICKER
    assert result["filings"] == ref.FILINGS[:12]


def test_compute_event_study_metrics():
    metrics = spx.compute_event_study(ref.SPCX_PRICES, ref.NDX_PRICES)
    assert metrics["ipo_price"] == ref.IPO_PRICE
    assert metrics["ipo_date"] == ref.SPCX_PRICES[0]["date"]
    assert metrics["latest_price"] == ref.SPCX_PRICES[-1]["close"]
    assert metrics["peak_price"] == max(p["close"] for p in ref.SPCX_PRICES)
    assert metrics["drawdown_from_peak_pct"] <= 0
    assert metrics["ndx_since_ipo_date_pct"] is not None
    assert metrics["since_inclusion_pct"] is not None


def test_compute_event_study_empty_input():
    assert spx.compute_event_study([], []) == {}


def test_compose_insights_nonempty_and_data_driven():
    metrics = spx.compute_event_study(ref.SPCX_PRICES, ref.NDX_PRICES)
    insights = spx.compose_insights(metrics)
    assert len(insights) >= 3
    assert any(ref.INDEX_NAME in i for i in insights)


def test_compose_insights_empty_metrics():
    assert spx.compose_insights({}) == []


def test_bank_impact_sections_categories():
    metrics = spx.compute_event_study(ref.SPCX_PRICES, ref.NDX_PRICES)
    sections = spx.bank_impact_sections(metrics)
    titles = {s["title"] for s in sections}
    assert titles == {
        "Equity capital markets",
        "Index-fund / ETF flows",
        "Prime brokerage & securities-based lending",
        "Wealth / private banking",
        "Corporate banking",
        "Risk management",
    }
    for section in sections:
        assert section["points"]


def test_get_dashboard_payload_shape():
    payload = spx.get_dashboard_payload()
    assert payload["ticker"] == ref.SPCX_TICKER
    assert payload["index_ticker"] == ref.INDEX_TICKER
    assert payload["timeline"] == ref.TIMELINE
    assert set(payload["prices"].keys()) == {"spcx", "index"}
    assert payload["metrics"]["ipo_price"] == ref.IPO_PRICE
    assert payload["insights"]
    assert payload["filings"]["filings"]
    assert payload["fred"]["source"] in ("live", "mock")
    assert len(payload["bank_impact"]) == 6
