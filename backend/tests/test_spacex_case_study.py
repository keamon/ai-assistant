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

"""Tests for the SpaceX index-inclusion case study (offline/mock-fallback
behaviour, matching the market-data layer's convention — see conftest.py)."""

from server import fred_data, spacex_case_study as sc


def test_get_price_series_mock():
    spcx = sc.get_price_series(sc.SPCX_TICKER)
    assert spcx["source"] == "mock"
    assert spcx["ticker"] == sc.SPCX_TICKER
    assert len(spcx["prices"]) > 0
    assert spcx["prices"][0]["date"] == "2026-06-12"

    ndx = sc.get_price_series(sc.INDEX_TICKER)
    assert ndx["source"] == "mock"
    assert len(ndx["prices"]) > 0


def test_get_filings_mock():
    res = sc.get_filings()
    assert res["source"] == "mock"
    assert res["ticker"] == sc.SPCX_TICKER
    assert len(res["filings"]) >= 1
    for f in res["filings"]:
        assert f["description"]
        assert f["form"]


def test_compute_event_study():
    spcx = sc._mock_prices(sc.SPCX_TICKER)["prices"]
    ndx = sc._mock_prices(sc.INDEX_TICKER)["prices"]
    m = sc.compute_event_study(spcx, ndx)

    assert m["ipo_price"] == sc.IPO_PRICE
    assert m["first_close"] == spcx[0]["close"]
    assert m["latest_price"] == spcx[-1]["close"]
    assert m["peak_price"] == max(p["close"] for p in spcx)
    # Peak is a maximum, so every other close is <= peak; from-peak % <= 0.
    assert m["spcx_from_peak_pct"] <= 0
    assert m["excess_return_since_ipo_pct"] == round(
        m["spcx_since_ipo_pct"] - m["ndx_since_ipo_date_pct"], 2
    )


def test_compute_event_study_empty_prices():
    assert sc.compute_event_study([], []) == {}


def test_compose_insights_nonempty_for_real_metrics():
    spcx = sc._mock_prices(sc.SPCX_TICKER)["prices"]
    ndx = sc._mock_prices(sc.INDEX_TICKER)["prices"]
    metrics = sc.compute_event_study(spcx, ndx)
    insights = sc.compose_insights(metrics)
    assert len(insights) >= 3
    assert all(isinstance(i, str) and i for i in insights)


def test_compose_insights_handles_missing_metrics():
    assert sc.compose_insights({}) == ["Price data unavailable."]


def test_bank_impact_sections_structure():
    sections = sc.bank_impact_sections({})
    assert len(sections) >= 4
    for s in sections:
        assert s["title"]
        assert len(s["points"]) >= 1


def test_get_dashboard_payload_mock():
    payload = sc.get_dashboard_payload()
    assert payload["ticker"] == sc.SPCX_TICKER
    assert payload["prices"]["spcx"]["source"] == "mock"
    assert payload["prices"]["index"]["source"] == "mock"
    assert payload["filings"]["source"] == "mock"
    assert payload["fred"]["source"] == "mock"
    assert payload["metrics"]
    assert payload["insights"]
    assert payload["bank_impact"]
    assert payload["timeline"]


def test_fred_get_economic_snapshot_mock():
    snap = fred_data.get_economic_snapshot()
    assert snap["source"] == "mock"
    assert "DFF" in snap["series"]
    assert "CPIAUCSL" in snap["series"]
    assert isinstance(snap["yield_curve_10y2y"], (int, float))


def test_spacex_analytics_endpoint(client, monkeypatch):
    from server import llm

    monkeypatch.setattr(llm, "generate_spacex_narrative", lambda payload: "TEST SPACEX NARRATIVE")
    res = client.get("/api/spacex-analytics")
    assert res.status_code == 200
    data = res.json()
    assert data["ticker"] == "SPCX"
    assert data["narrative"] == "TEST SPACEX NARRATIVE"
    assert data["prices"]["spcx"]["source"] == "mock"

    # Cached: a second call returns the same payload without recomputing.
    res2 = client.get("/api/spacex-analytics")
    assert res2.json() == data
