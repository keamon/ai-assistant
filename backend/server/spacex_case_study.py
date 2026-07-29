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
SpaceX (NASDAQ: SPCX) index-inclusion case study — an analytics dashboard
feature, independent of the FinTechCo demo-customer domain data in
:mod:`server.mock_data`. Combines three live data sources with the same
live-with-mock-fallback pattern as :mod:`server.market_data` /
:mod:`server.fred_data`:

- **SEC EDGAR** — SpaceX's IPO/listing filings (S-1, 424B4, 8-A12B, 8-Ks).
- **Yahoo Finance** — SPCX and Nasdaq-100 (^NDX) daily price history.
- **FRED** — macro backdrop (rates, CPI, unemployment) via :mod:`server.fred_data`.

Pre-researched reference facts (timeline, price history, curated filings) live
in :mod:`server.spacex_reference_data` — this module is the business-logic
layer on top: live fetch + fallback, event-study metrics, insights, and the
bank-operations-impact analysis.
"""

import datetime
import json
import os
import urllib.request

from server import fred_data, market_data
from server.spacex_reference_data import (
    FILINGS,
    INCLUSION_DATE,
    INDEX_NAME,
    INDEX_TICKER,
    IPO_PRICE,
    SPCX_CIK,
    SPCX_TICKER,
    TIMELINE,
)
from server.spacex_reference_data import NDX_PRICES as _MOCK_NDX_PRICES
from server.spacex_reference_data import SPCX_PRICES as _MOCK_SPCX_PRICES

_SEC_UA = "FinTechCo Employee Digital Assistant demo (contact: dev@chenkeamonwang.altostrat.com)"
_TIMEOUT = 6
_MOCK_FILINGS = FILINGS


def _live_disabled() -> bool:
    return os.getenv("SSIM_DISABLE_LIVE_MARKET", "").strip().lower() in ("1", "true", "yes")


def _mock_prices(ticker: str) -> dict:
    prices = _MOCK_SPCX_PRICES if ticker == SPCX_TICKER else _MOCK_NDX_PRICES
    return {"ticker": ticker, "source": "mock", "currency": "USD", "prices": prices}


def get_price_series(ticker: str) -> dict:
    """SPCX or ^NDX daily price history since just before the IPO, live with mock fallback."""
    if _live_disabled():
        return _mock_prices(ticker)
    try:
        return market_data.get_price_history(ticker, range_="6mo", interval="1d")
    except Exception:
        return _mock_prices(ticker)


def _mock_filings() -> dict:
    return {"company": "Space Exploration Technologies Corp.", "ticker": SPCX_TICKER,
            "cik": SPCX_CIK, "source": "mock", "filings": list(_MOCK_FILINGS)}


# SEC EDGAR's own "primaryDocDescription" field is usually just the form code
# repeated (e.g. "8-K"), not a useful summary — so the live path prefers these
# hand-curated descriptions (keyed by accession number) and only falls back to
# whatever SEC returned for filings outside the curated set.
_CURATED_DESCRIPTIONS = {f["accession"]: f["description"] for f in _MOCK_FILINGS}


def get_filings(limit: int = 11) -> dict:
    """SpaceX's IPO/listing-era SEC filings, live with a curated mock fallback.

    Unlike :func:`server.market_data.get_sec_filings` (10-K/10-Q/8-K only, and
    only knows the FinTechCo demo customers' tickers), this pulls the broader
    set of forms that tell an IPO story — S-1, 424B4, 8-A12B, S-8, 8-K — and
    falls back to a curated real-filing list specific to SpaceX.
    """
    if _live_disabled():
        return _mock_filings()
    try:
        cik_int = int(SPCX_CIK)
        url = f"https://data.sec.gov/submissions/CIK{cik_int:010d}.json"
        req = urllib.request.Request(
            url, headers={"User-Agent": _SEC_UA, "Accept": "application/json", "Host": "data.sec.gov"}
        )
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        recent = data["filings"]["recent"]
        forms_of_interest = {"S-1", "S-1/A", "8-A12B", "424B4", "S-8", "8-K"}
        rows = []
        seen_form_date = set()
        for form, filed, acc, doc, desc in zip(
            recent["form"], recent["filingDate"], recent["accessionNumber"],
            recent["primaryDocument"], recent["primaryDocDescription"],
        ):
            if form not in forms_of_interest:
                continue
            # SEC occasionally lists the same same-day filing twice (e.g. a
            # duplicate 8-A12B submission) — keep only the first.
            if (form, filed) in seen_form_date:
                continue
            seen_form_date.add((form, filed))
            acc_nodash = acc.replace("-", "")
            doc_url = (f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_nodash}/{doc}"
                       if doc else "")
            description = _CURATED_DESCRIPTIONS.get(acc) or desc or form
            rows.append({"form": form, "filed": filed, "description": description,
                         "accession": acc, "primary_doc": doc, "url": doc_url})
            if len(rows) >= limit:
                break

        return {"company": data.get("name", "Space Exploration Technologies Corp."),
                "ticker": SPCX_TICKER, "cik": f"{cik_int:010d}", "source": "live", "filings": rows}
    except Exception:
        return _mock_filings()


# ─── Event-study metrics ─────────────────────────────────────────────────────

def _lookup(prices: list[dict], date: str):
    for p in prices:
        if p["date"] == date:
            return p["close"]
    return None


def _pct(a: float, b: float) -> float | None:
    """Percent change from a to b."""
    if a in (None, 0) or b is None:
        return None
    return round((b - a) / a * 100, 2)


def compute_event_study(spcx_prices: list[dict], ndx_prices: list[dict]) -> dict:
    """Key stats comparing SPCX's price path to the Nasdaq-100 since the IPO."""
    if not spcx_prices:
        return {}
    first = spcx_prices[0]
    last = spcx_prices[-1]
    peak = max(spcx_prices, key=lambda p: p["close"])
    inclusion_price = _lookup(spcx_prices, INCLUSION_DATE)
    ndx_first = _lookup(ndx_prices, first["date"]) or (ndx_prices[0]["close"] if ndx_prices else None)
    ndx_last = ndx_prices[-1]["close"] if ndx_prices else None
    ndx_inclusion = _lookup(ndx_prices, INCLUSION_DATE)

    spcx_since_ipo = _pct(IPO_PRICE, last["close"])
    spcx_since_first_close = _pct(first["close"], last["close"])
    ndx_since_ipo_date = _pct(ndx_first, ndx_last) if ndx_first and ndx_last else None
    spcx_from_peak = _pct(peak["close"], last["close"])
    spcx_ipo_to_inclusion = _pct(IPO_PRICE, inclusion_price) if inclusion_price else None
    ndx_ipo_to_inclusion = _pct(ndx_first, ndx_inclusion) if ndx_first and ndx_inclusion else None
    spcx_inclusion_to_now = _pct(inclusion_price, last["close"]) if inclusion_price else None
    ndx_inclusion_to_now = _pct(ndx_inclusion, ndx_last) if ndx_inclusion and ndx_last else None

    excess_since_ipo = (
        round(spcx_since_ipo - ndx_since_ipo_date, 2)
        if spcx_since_ipo is not None and ndx_since_ipo_date is not None else None
    )

    return {
        "ipo_price": IPO_PRICE,
        "first_close": first["close"],
        "first_close_date": first["date"],
        "latest_price": last["close"],
        "latest_date": last["date"],
        "peak_price": peak["close"],
        "peak_date": peak["date"],
        "inclusion_price": inclusion_price,
        "spcx_since_ipo_pct": spcx_since_ipo,
        "spcx_since_first_close_pct": spcx_since_first_close,
        "spcx_from_peak_pct": spcx_from_peak,
        "ndx_since_ipo_date_pct": ndx_since_ipo_date,
        "excess_return_since_ipo_pct": excess_since_ipo,
        "spcx_ipo_to_inclusion_pct": spcx_ipo_to_inclusion,
        "ndx_ipo_to_inclusion_pct": ndx_ipo_to_inclusion,
        "spcx_inclusion_to_now_pct": spcx_inclusion_to_now,
        "ndx_inclusion_to_now_pct": ndx_inclusion_to_now,
    }


def compose_insights(metrics: dict) -> list[str]:
    """Deterministic, data-driven bullet insights (used as the LLM's fallback too)."""
    if not metrics:
        return ["Price data unavailable."]
    m = metrics
    out = []
    if m.get("spcx_since_ipo_pct") is not None:
        direction = "above" if m["spcx_since_ipo_pct"] >= 0 else "below"
        out.append(
            f"SPCX trades **{abs(m['spcx_since_ipo_pct']):.1f}% {direction}** its ${m['ipo_price']:.0f} "
            f"IPO offer price as of {m['latest_date']} (${m['latest_price']:.2f})."
        )
    if m.get("peak_price") and m.get("spcx_from_peak_pct") is not None:
        out.append(
            f"Shares peaked at **${m['peak_price']:.2f}** on {m['peak_date']} "
            f"(+{_pct(m['ipo_price'], m['peak_price']):.1f}% vs. the offer price) and have since fallen "
            f"**{abs(m['spcx_from_peak_pct']):.1f}%** from that high."
        )
    if m.get("spcx_ipo_to_inclusion_pct") is not None and m.get("ndx_ipo_to_inclusion_pct") is not None:
        out.append(
            f"Between the IPO and the {INDEX_NAME} inclusion date ({INCLUSION_DATE}), SPCX moved "
            f"{m['spcx_ipo_to_inclusion_pct']:+.1f}% while the index itself moved "
            f"{m['ndx_ipo_to_inclusion_pct']:+.1f}% — most of SPCX's index-inclusion-speculation rally had "
            "already happened before the effective date."
        )
    if m.get("spcx_inclusion_to_now_pct") is not None and m.get("ndx_inclusion_to_now_pct") is not None:
        out.append(
            f"Since the actual inclusion date, SPCX is {m['spcx_inclusion_to_now_pct']:+.1f}% versus "
            f"{m['ndx_inclusion_to_now_pct']:+.1f}% for the {INDEX_NAME} — a **'buy the rumor, sell the "
            "news'** pattern, with no sustained inclusion-day pop for the stock itself."
        )
    if m.get("excess_return_since_ipo_pct") is not None:
        out.append(
            f"Net of the index's own move, SPCX has underperformed the {INDEX_NAME} by "
            f"**{abs(m['excess_return_since_ipo_pct']):.1f} points** since its first trading day — being "
            "added to a passive index guaranteed a wave of forced buying, but did not guarantee durable "
            "outperformance."
        )
    return out


# ─── Bank-operations impact ──────────────────────────────────────────────────

def bank_impact_sections(metrics: dict) -> list[dict]:
    """Static, categorized analysis of how an event like this touches a bank's
    business lines — grounded in the computed metrics where useful."""
    m = metrics or {}
    vol_note = ""
    if m.get("peak_price") and m.get("latest_price"):
        swing = abs(_pct(m["peak_price"], m["latest_price"]) or 0)
        vol_note = f" SPCX's {swing:.0f}% round-trip from its post-IPO peak illustrates the scale of that risk."

    return [
        {
            "title": "Equity Capital Markets & Underwriting",
            "points": [
                "A ~$75B IPO plus a follow-on senior notes offering within two weeks generates substantial "
                "underwriting, advisory, and debt-placement fee revenue for the bank(s) in the syndicate.",
                "Mega-IPO allocation and stabilization (over-allotment/greenshoe) activity concentrates "
                "short-term inventory and price risk on the underwriting desk's balance sheet.",
            ],
        },
        {
            "title": "Index Funds, ETF Authorized Participants & Trading Desks",
            "points": [
                "Fast-tracked index inclusion forces passive funds tracking the Nasdaq-100 to buy SPCX "
                "immediately, and any bank running index-fund/ETF authorized-participant or basket-trading "
                "desks sees a spike in creation/redemption and rebalancing flow around the inclusion date.",
                "Program and block-trading desks should expect elevated volume and wider spreads in the "
                "name for days around each index event (Nasdaq-100, then Russell, then any future S&P 500 "
                "decision).",
            ],
        },
        {
            "title": "Prime Brokerage, Margin & Securities-Based Lending",
            "points": [
                "Concentrated, newly-liquid single-name positions (employee/early-investor shares coming "
                "out of lockup, or clients using SPCX as loan collateral) carry outsized volatility risk." + vol_note,
                "Risk teams should apply conservative haircuts and stress the loan-to-value on any "
                "securities-based lending book with SPCX collateral given the realized volatility since "
                "listing — the stock has traded across more than a 2x high-low range in its first seven "
                "weeks.",
            ],
        },
        {
            "title": "Wealth & Private Banking",
            "points": [
                "Employees and early investors emerging from lockup create demand for liquidity solutions "
                "(structured sales, collar/hedging strategies, pre-planned diversification programs).",
                "Relationship managers should expect concentrated-position conversations from any client "
                "holding SPCX equity compensation or pre-IPO shares.",
            ],
        },
        {
            "title": "Corporate & Commercial Banking",
            "points": [
                "A newly-public, capital-intensive issuer with fresh IPO and debt proceeds is a candidate "
                "for expanded treasury management, cash-sweep, and corporate banking relationships.",
                "The debt offering launched within two weeks of the IPO signals an issuer that will likely "
                "return to capital markets again as it scales — an origination opportunity for relationship "
                "banks.",
            ],
        },
        {
            "title": "Risk Management & Macro Backdrop",
            "points": [
                "Elevated 10-year Treasury yields raise the discount rate applied to a long-duration, "
                "pre-profitability growth story like SpaceX, amplifying the sensitivity of its valuation "
                "(and any bank exposure to it) to rate moves.",
                "A single-name concentration this large moving in and out of core index products is itself "
                "a market-structure risk worth monitoring for any bank running index-linked structured "
                "products or overlay strategies.",
            ],
        },
    ]


# ─── Assembled dashboard payload ─────────────────────────────────────────────

def get_dashboard_payload() -> dict:
    spcx = get_price_series(SPCX_TICKER)
    ndx = get_price_series(INDEX_TICKER)
    metrics = compute_event_study(spcx.get("prices", []), ndx.get("prices", []))
    filings = get_filings()
    fred_snapshot = fred_data.get_economic_snapshot()

    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "company": "Space Exploration Technologies Corp. (SpaceX)",
        "ticker": SPCX_TICKER,
        "index_name": INDEX_NAME,
        "index_ticker": INDEX_TICKER,
        "timeline": TIMELINE,
        "prices": {"spcx": spcx, "index": ndx},
        "metrics": metrics,
        "insights": compose_insights(metrics),
        "filings": filings,
        "fred": fred_snapshot,
        "bank_impact": bank_impact_sections(metrics),
    }
