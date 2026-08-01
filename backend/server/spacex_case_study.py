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
SpaceX (NASDAQ: SPCX) index-inclusion market-intelligence dashboard — a
self-contained case study independent of the FinTechCo customer domain
(``mock_data.py``/``seed.py``). See PRD §6.8 / spec.md for the product and
technical spec.

Combines three live-with-mock-fallback sources — SEC EDGAR filings, Yahoo
Finance price history (via :mod:`server.market_data`), and FRED macro data
(:mod:`server.fred_data`) — with the verified reference facts in
:mod:`server.spacex_reference_data`, then layers on deterministic event-study
math and a categorized "impact on bank operations" analysis.
"""

import json
import os
import urllib.error
import urllib.request

from server import fred_data, market_data
from server import spacex_reference_data as ref

_SEC_UA = "FinTechCo Employee Digital Assistant demo (contact: dev@chenkeamonwang.altostrat.com)"
_TIMEOUT = 6
_FILING_FORMS = {"S-1", "S-1/A", "8-A12B", "424B4", "S-8", "8-K"}
_CURATED_DESCRIPTIONS = {f["accession"]: f["description"] for f in ref.FILINGS}


def _live_disabled() -> bool:
    return os.getenv("DEMO_DISABLE_LIVE_MARKET", "").strip().lower() in ("1", "true", "yes")


# ─── Price series (Yahoo Finance, via market_data, with a baked fallback) ────

def get_price_series(ticker: str, mock_prices: list[dict]) -> dict:
    """SPCX/index daily close history, falling back to a baked real snapshot
    (rather than the generic ``mock_data`` fixtures, which don't carry time
    series) on any failure or when live fetches are disabled."""
    if _live_disabled():
        return {"ticker": ticker, "source": "mock", "prices": mock_prices}
    try:
        result = market_data.get_price_history(ticker, range_="3mo", interval="1d")
        if not result.get("prices"):
            raise ValueError("empty price series")
        return result
    except Exception:
        return {"ticker": ticker, "source": "mock", "prices": mock_prices}


# ─── SEC EDGAR filings (broader form set than market_data.get_sec_filings) ──

def _mock_filings(limit: int) -> dict:
    return {
        "company": "SpaceX", "ticker": ref.SPCX_TICKER, "cik": ref.SPCX_CIK,
        "source": "mock", "filings": ref.FILINGS[:limit],
    }


def get_filings(limit: int = 11) -> dict:
    """SpaceX's IPO/listing-story filings: S-1, S-1/A, 8-A12B, 424B4, S-8, 8-K —
    a broader form set than the generic customer-watch SEC helper, since these
    tell the IPO story. Deduped by (form, filed), curated descriptions
    preferred over SEC's own (usually just the form code repeated)."""
    if _live_disabled():
        return _mock_filings(limit)
    try:
        cik_int = int(ref.SPCX_CIK)
        url = f"https://data.sec.gov/submissions/CIK{cik_int:010d}.json"
        req = urllib.request.Request(
            url, headers={"User-Agent": _SEC_UA, "Accept": "application/json", "Host": "data.sec.gov"}
        )
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        recent = data["filings"]["recent"]
        seen = set()
        rows = []
        for form, filed, acc, doc in zip(
            recent["form"], recent["filingDate"], recent["accessionNumber"], recent["primaryDocument"],
        ):
            if form not in _FILING_FORMS:
                continue
            key = (form, filed)
            if key in seen:
                continue
            seen.add(key)
            acc_nodash = acc.replace("-", "")
            doc_url = (f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_nodash}/{doc}"
                       if doc else "")
            rows.append({
                "form": form, "filed": filed,
                "description": _CURATED_DESCRIPTIONS.get(acc, form),
                "accession": acc, "primary_doc": doc, "url": doc_url,
            })
            if len(rows) >= limit:
                break

        if not rows:
            raise ValueError("no matching filings in live response")

        return {
            "company": data.get("name", "SpaceX"), "ticker": ref.SPCX_TICKER,
            "cik": f"{cik_int:010d}", "source": "live", "filings": rows,
        }
    except Exception:
        return _mock_filings(limit)


# ─── Event-study math ────────────────────────────────────────────────────────

def _pct(a, b):
    if a is None or not b:
        return None
    return round((a - b) / b * 100, 2)


def compute_event_study(spcx_prices: list[dict], ndx_prices: list[dict]) -> dict:
    """Offer-price/first-close/peak/latest/inclusion-date prices and their %
    changes, plus the excess return of SPCX net of the index's own move."""
    if not spcx_prices:
        return {}

    by_date_ndx = {p["date"]: p["close"] for p in ndx_prices}
    offer_price = ref.IPO_PRICE
    first = spcx_prices[0]
    peak = max(spcx_prices, key=lambda p: p["close"])
    latest = spcx_prices[-1]
    inclusion_price = next((p["close"] for p in spcx_prices if p["date"] >= ref.INCLUSION_DATE), None)

    ndx_base = by_date_ndx.get(first["date"]) or (ndx_prices[0]["close"] if ndx_prices else None)
    ndx_latest = ndx_prices[-1]["close"] if ndx_prices else None

    spcx_since_ipo_pct = _pct(latest["close"], offer_price)
    ndx_since_ipo_date_pct = _pct(ndx_latest, ndx_base)
    excess = (
        round(spcx_since_ipo_pct - ndx_since_ipo_date_pct, 2)
        if spcx_since_ipo_pct is not None and ndx_since_ipo_date_pct is not None
        else None
    )

    return {
        "ipo_price": offer_price,
        "first_close_price": round(first["close"], 2),
        "first_close_pop_pct": _pct(first["close"], offer_price),
        "peak_price": round(peak["close"], 2),
        "peak_date": peak["date"],
        "latest_price": round(latest["close"], 2),
        "latest_date": latest["date"],
        "inclusion_date_price": round(inclusion_price, 2) if inclusion_price is not None else None,
        "since_inclusion_pct": _pct(latest["close"], inclusion_price),
        "since_peak_pct": _pct(latest["close"], peak["close"]),
        "spcx_since_ipo_pct": spcx_since_ipo_pct,
        "ndx_since_ipo_date_pct": ndx_since_ipo_date_pct,
        "excess_return_since_ipo_pct": excess,
    }


# ─── Insights (deterministic; also the LLM narrative's fallback) ────────────

def compose_insights(metrics: dict) -> list[str]:
    if not metrics:
        return []
    insights = [
        f"SPCX priced at ${metrics['ipo_price']:.0f} on {ref.IPO_DATE} and closed its first session at "
        f"${metrics['first_close_price']:.2f} ({metrics['first_close_pop_pct']:+.1f}%), then touched a "
        f"post-IPO peak of ${metrics['peak_price']:.2f} on {metrics['peak_date']} amid speculation about "
        "forced buying ahead of a Nasdaq-100 decision."
    ]

    if metrics.get("since_inclusion_pct") is not None:
        direction = "fallen" if metrics["since_inclusion_pct"] < 0 else "risen"
        insights.append(
            f"Since being fast-tracked into the {ref.INDEX_NAME} on {ref.INCLUSION_DATE}, SPCX has "
            f"{direction} {abs(metrics['since_inclusion_pct']):.1f}% to ${metrics['latest_price']:.2f} "
            f"as of {metrics['latest_date']} — the anticipated index-inclusion demand did not sustain "
            "the stock above its post-IPO peak."
        )

    if metrics.get("excess_return_since_ipo_pct") is not None:
        rel = "outperforming" if metrics["excess_return_since_ipo_pct"] >= 0 else "underperforming"
        insights.append(
            f"SPCX is {metrics['spcx_since_ipo_pct']:+.1f}% versus its IPO offer price, against "
            f"{metrics['ndx_since_ipo_date_pct']:+.1f}% for the {ref.INDEX_NAME} over the same window — "
            f"{rel} the index by {abs(metrics['excess_return_since_ipo_pct']):.1f}pp even after "
            "mandated index-fund buying on inclusion."
        )

    insights.append(
        "SpaceX is too large for the Russell 2000 and is expected to join the Russell 1000 at the "
        "September or December 2026 reconstitution; S&P 500 eligibility requires four consecutive "
        "profitable quarters, which S&P Dow Jones Indices does not fast-track — not realistic before "
        "mid-2027 given a $4.9B trailing net loss."
    )
    return insights


# ─── Impact on bank operations ───────────────────────────────────────────────

def bank_impact_sections(metrics: dict) -> list[dict]:
    m = metrics or {}
    since_ipo = m.get("spcx_since_ipo_pct")
    excess = m.get("excess_return_since_ipo_pct")
    since_incl = m.get("since_inclusion_pct")
    peak = m.get("peak_price")
    latest = m.get("latest_price")

    since_ipo_line = (
        f"The stock is {since_ipo:+.1f}% versus its ${m.get('ipo_price', 0):.0f} offer price as of "
        f"{m.get('latest_date', 'today')} — aftermarket performance banks should weigh when pricing the "
        "underwriting discount on the next mega-IPO."
        if since_ipo is not None else
        "Aftermarket performance versus the offer price is a key input for pricing the next mega-IPO."
    )
    excess_line = (
        f"Excess return over the {ref.INDEX_NAME} since IPO is {excess:+.1f}pp — the cleanest read on "
        "how much of the move was mechanical index-fund flow versus fundamentals."
        if excess is not None else
        f"Excess return over the {ref.INDEX_NAME} is the cleanest read on flow-driven vs. fundamental moves."
    )
    sbl_line = (
        f"With the stock {abs(since_incl):.1f}% {'below' if since_incl < 0 else 'above'} its "
        f"{ref.INCLUSION_DATE} index-inclusion-date price, margin/haircut schedules on SPCX-collateralized "
        "loans should reflect the realized post-inclusion volatility, not the IPO-week levels."
        if since_incl is not None else
        "Margin/haircut schedules on SPCX-collateralized loans should reflect realized post-listing volatility."
    )
    risk_line = (
        f"SPCX's swing from a ${peak:.2f} post-IPO peak to ${latest:.2f} in a matter of weeks is a live "
        "stress-test case for single-name concentration limits across trading, lending, and wealth books."
        if peak is not None and latest is not None else
        "SPCX's post-IPO price swing is a live stress-test case for single-name concentration limits."
    )

    return [
        {
            "title": "Equity capital markets & underwriting",
            "points": [
                "A ~$75B IPO is a marquee league-table event; ECM should mine the syndicate relationships "
                "built here for the follow-on debt deal and future secondary offerings.",
                since_ipo_line,
            ],
        },
        {
            "title": "Index-fund & ETF flows",
            "points": [
                "The 2026 Nasdaq fast-track rule forced every Nasdaq-100-tracking fund to buy SPCX inside a "
                "compressed 15-trading-day window — a one-time, mechanical demand shock our index & "
                "passive-fund trading desks should model ahead of the next fast-tracked mega-IPO.",
                excess_line,
            ],
        },
        {
            "title": "Prime brokerage & securities-based lending",
            "points": [
                "Elevated realized volatility since listing argues for tighter margin/haircut schedules on "
                "SPCX-collateralized loans and SBL facilities in the near term.",
                sbl_line,
            ],
        },
        {
            "title": "Wealth & private banking",
            "points": [
                "Concentrated-stock clients who received or purchased SPCX pre-IPO likely carry single-name "
                "concentration risk; proactively offer hedging/diversification conversations ahead of any "
                "lock-up expiration.",
                "Retail/HNW demand for SPCX exposure (direct or via index funds tracking the Nasdaq-100) is "
                "a natural entry point for a structured-note or collar-overlay conversation.",
            ],
        },
        {
            "title": "Corporate banking",
            "points": [
                "The concurrent senior notes offering (priced 2026-06-23, closed 2026-06-26) signals SpaceX "
                "is diversifying into fixed-income markets alongside the equity raise — an opening for a "
                "broader corporate banking relationship (cash management, revolving credit) beyond the IPO "
                "underwriting mandate.",
            ],
        },
        {
            "title": "Risk management",
            "points": [
                risk_line,
                "Treat the fast-track index-inclusion mechanism itself as a recurring event-risk factor for "
                "any future mega-IPO the bank underwrites or extends credit against.",
            ],
        },
    ]


# ─── Dashboard payload ────────────────────────────────────────────────────────

def get_dashboard_payload() -> dict:
    """Assembles everything the API/UI/PDF need: timeline, prices, metrics,
    insights, filings, macro snapshot, and bank-impact analysis."""
    spcx = get_price_series(ref.SPCX_TICKER, ref.SPCX_PRICES)
    index = get_price_series(ref.INDEX_TICKER, ref.NDX_PRICES)
    metrics = compute_event_study(spcx["prices"], index["prices"])
    return {
        "company": "SpaceX",
        "ticker": ref.SPCX_TICKER,
        "index_name": ref.INDEX_NAME,
        "index_ticker": ref.INDEX_TICKER,
        "ipo_date": ref.IPO_DATE,
        "inclusion_date": ref.INCLUSION_DATE,
        "timeline": ref.TIMELINE,
        "prices": {"spcx": spcx, "index": index},
        "metrics": metrics,
        "insights": compose_insights(metrics),
        "filings": get_filings(),
        "fred": fred_data.get_economic_snapshot(),
        "bank_impact": bank_impact_sections(metrics),
    }
