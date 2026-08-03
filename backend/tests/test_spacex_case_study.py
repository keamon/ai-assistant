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

"""Tests for the SpaceX index-inclusion case study module.

This module is live-only (SEC EDGAR + Yahoo Finance), with no
DEMO_DISABLE_LIVE_MARKET offline path of its own — per CLAUDE.md's "No mock
data" policy, tests monkeypatch the live-call seams directly
(``market_data.get_price_history``, ``spacex_case_study._fetch_filings_raw``)
instead of relying on a baked fallback.
"""

import pytest

from server import market_data, spacex_case_study as spx
from server import spacex_reference_data as ref

_SPCX_PRICES = [
    {"date": "2026-06-12", "close": 160.95},
    {"date": "2026-06-16", "close": 211.39},
    {"date": "2026-07-06", "close": 160.42},
    {"date": "2026-07-28", "close": 116.41},
]
_NDX_PRICES = [
    {"date": "2026-06-01", "close": 30513.86},
    {"date": "2026-06-12", "close": 29635.95},
    {"date": "2026-07-06", "close": 29697.87},
    {"date": "2026-07-28", "close": 27763.13},
]


def _fake_get_price_history(ticker, range_="1y", interval="1d"):
    if ticker == ref.SPCX_TICKER:
        return {"ticker": ticker, "source": "live", "currency": "USD", "prices": list(_SPCX_PRICES)}
    if ticker == ref.INDEX_TICKER:
        return {"ticker": ticker, "source": "live", "currency": "USD", "prices": list(_NDX_PRICES)}
    raise ValueError(f"unexpected ticker {ticker}")


@pytest.fixture
def patched_prices(monkeypatch):
    monkeypatch.setattr(market_data, "get_price_history", _fake_get_price_history)


# ─── get_price_series ────────────────────────────────────────────────────────

def test_get_price_series_trims_spcx_to_ipo_date(patched_prices):
    prices = spx.get_price_series()
    assert prices["spcx"]["prices"][0]["date"] == ref.IPO_DATE
    assert all(p["date"] >= ref.IPO_DATE for p in prices["spcx"]["prices"])
    assert prices["spcx"]["source"] == "live"


def test_get_price_series_keeps_pre_ipo_index_context(patched_prices):
    prices = spx.get_price_series()
    dates = [p["date"] for p in prices["index"]["prices"]]
    assert "2026-06-01" in dates  # pre-IPO context point, not trimmed


def test_get_price_series_raises_on_failure(monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("network unreachable")

    monkeypatch.setattr(market_data, "get_price_history", boom)
    with pytest.raises(OSError):
        spx.get_price_series()


# ─── compute_event_study ─────────────────────────────────────────────────────

def test_compute_event_study_metrics(patched_prices):
    prices = spx.get_price_series()
    metrics = spx.compute_event_study(prices)

    assert metrics["ipo_price"] == ref.IPO_PRICE
    assert metrics["first_close"] == 160.95
    assert metrics["first_close_date"] == "2026-06-12"
    assert metrics["peak_price"] == 211.39
    assert metrics["peak_date"] == "2026-06-16"
    assert metrics["latest_price"] == 116.41
    assert metrics["latest_date"] == "2026-07-28"
    assert metrics["spcx_since_ipo_pct"] == pytest.approx((116.41 - 135.0) / 135.0 * 100, abs=0.01)
    assert metrics["excess_return_since_ipo_pct"] is not None
    # Inclusion-date fields present since a price on/after INCLUSION_DATE exists
    assert metrics["inclusion_date"] == ref.INCLUSION_DATE
    assert metrics["inclusion_price"] == 160.42


def test_compute_event_study_raises_on_empty_prices():
    with pytest.raises(RuntimeError):
        spx.compute_event_study({"spcx": {"prices": []}, "index": {"prices": []}})


# ─── compose_insights / bank_impact_sections ────────────────────────────────

def test_compose_insights_is_data_driven(patched_prices):
    prices = spx.get_price_series()
    metrics = spx.compute_event_study(prices)
    insights = spx.compose_insights(metrics)

    assert isinstance(insights, list)
    assert len(insights) >= 3
    assert all(isinstance(i, str) and i for i in insights)
    assert "135.00" in insights[0]


def test_bank_impact_sections_six_categories(patched_prices):
    prices = spx.get_price_series()
    metrics = spx.compute_event_study(prices)
    sections = spx.bank_impact_sections(metrics)

    assert len(sections) == 6
    titles = {s["title"] for s in sections}
    assert "Equity capital markets & underwriting" in titles
    assert "Risk management" in titles
    for s in sections:
        assert s["points"]
        assert all(isinstance(p, str) and p for p in s["points"])


# ─── get_filings ─────────────────────────────────────────────────────────────

def _fake_filings_raw():
    known = ref.FILINGS[0]  # has a curated description this module should reuse
    return [
        {"form": known["form"], "filed": known["filed"], "accession": known["accession"],
         "primary_doc": known["primary_doc"], "raw_description": known["form"]},
        # duplicate (form, filed) pair — must be deduped
        {"form": known["form"], "filed": known["filed"], "accession": known["accession"],
         "primary_doc": known["primary_doc"], "raw_description": known["form"]},
        # a filing with no curated match — falls back to SEC's own description
        {"form": "8-K", "filed": "2026-08-01", "accession": "0001628280-26-099999",
         "primary_doc": "spcx8k.htm", "raw_description": "8-K"},
        # a form outside the tracked set must never appear (guards _fetch_filings_raw's own filter)
    ]


def test_get_filings_dedups_and_enriches(monkeypatch):
    monkeypatch.setattr(spx, "_fetch_filings_raw", _fake_filings_raw)
    result = spx.get_filings()

    assert result["source"] == "live"
    assert result["ticker"] == ref.SPCX_TICKER
    known = ref.FILINGS[0]
    matching = [f for f in result["filings"] if f["accession"] == known["accession"]]
    assert len(matching) == 1  # deduped
    assert matching[0]["description"] == known["description"]  # curated, not raw "8-K"/"S-1" etc.

    uncurated = [f for f in result["filings"] if f["accession"] == "0001628280-26-099999"]
    assert uncurated[0]["description"] == "8-K"  # falls back to SEC's own description, not fabricated


def test_get_filings_raises_on_failure(monkeypatch):
    def boom():
        raise OSError("SEC EDGAR unreachable")

    monkeypatch.setattr(spx, "_fetch_filings_raw", boom)
    with pytest.raises(OSError):
        spx.get_filings()


# ─── get_dashboard_payload ───────────────────────────────────────────────────

def test_get_dashboard_payload_assembles_everything(patched_prices, monkeypatch):
    monkeypatch.setattr(spx, "_fetch_filings_raw", _fake_filings_raw)

    payload = spx.get_dashboard_payload()

    for key in ("company", "ticker", "cik", "index_name", "index_ticker", "timeline",
                "prices", "metrics", "insights", "filings", "fred", "bank_impact", "news"):
        assert key in payload

    assert payload["ticker"] == ref.SPCX_TICKER
    assert payload["news"] == []  # DEMO_DISABLE_LIVE_MARKET=1 in conftest — no network attempted
    assert payload["fred"]["source"] == "mock"  # fred_data's own pre-existing offline fallback
    assert len(payload["bank_impact"]) == 6
    assert payload["timeline"] == ref.TIMELINE


def test_get_dashboard_payload_raises_when_prices_unavailable(monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("Yahoo unreachable")

    monkeypatch.setattr(market_data, "get_price_history", boom)
    with pytest.raises(OSError):
        spx.get_dashboard_payload()
