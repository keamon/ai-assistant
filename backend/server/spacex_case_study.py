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
SpaceX (NASDAQ: SPCX) index-inclusion market-intelligence case study — event-study
metrics, deterministic insights, and "impact on bank operations" analysis for a
FinTechCo audience.

Standalone from the FinTechCo demo-customer domain (no :class:`server.store.Store`
dependency, no :mod:`server.mock_data`): combines a **live-with-mock-fallback**
price series (:mod:`server.market_data`), a **live-with-mock-fallback** SEC EDGAR
filings fetch (broader form set than the generic customer-watch fetch, curated
descriptions backfilled from :mod:`server.spacex_reference_data`), and
:mod:`server.fred_data`'s macro snapshot. Each live-fetched piece is tagged
``"source": "live"`` or ``"source": "mock"``, matching the rest of the codebase's
market-data convention.
"""

import json
import os
import urllib.request

from server import fred_data, market_data
from server import spacex_reference_data as ref

_TIMEOUT = 6
_SEC_UA = "FinTechCo Employee Digital Assistant demo (contact: dev@chenkeamonwang.altostrat.com)"
COMPANY_NAME = "Space Exploration Technologies Corp."


def _live_disabled() -> bool:
    return os.getenv("DEMO_DISABLE_LIVE_MARKET", "").strip().lower() in ("1", "true", "yes")


# ─── Price series ────────────────────────────────────────────────────────────

def get_price_series(ticker: str, fallback: list[dict]) -> dict:
    """Live Yahoo daily close history for ``ticker``, falling back to the baked
    reference series in :mod:`server.spacex_reference_data` on any failure.

    Returns ``{ticker, source: "live"|"mock", prices: [{date, close}]}``.
    """
    if not _live_disabled():
        try:
            hist = market_data.get_price_history(ticker, range_="3mo")
            if hist.get("prices"):
                return {"ticker": ticker, "source": "live", "prices": hist["prices"]}
        except Exception:
            pass
    return {"ticker": ticker, "source": "mock", "prices": fallback}


# ─── SEC EDGAR filings ───────────────────────────────────────────────────────

def _curated_description(form: str, filed: str) -> str:
    """Backfill a curated description from the baked reference filings, by
    (form, filed date) — used for both the live and mock paths since SEC's own
    ``primaryDocDescription`` is usually just the form code repeated."""
    for f in ref.FILINGS:
        if f["form"] == form and f["filed"] == filed:
            return f["description"]
    return f"{form} filing"


def get_filings(limit: int = 12) -> dict:
    """Recent SpaceX SEC filings across the full form set relevant to an IPO
    (S-1, S-1/A, 8-A12B, 424B4, S-8, 8-K) — broader than the generic
    customer-watch fetch in :mod:`server.market_data`, which only pulls
    10-K/10-Q/8-K. Falls back to :data:`server.spacex_reference_data.FILINGS`.
    """
    if not _live_disabled():
        try:
            cik_int = int(ref.SPCX_CIK)
            url = f"https://data.sec.gov/submissions/CIK{cik_int:010d}.json"
            req = urllib.request.Request(
                url, headers={"User-Agent": _SEC_UA, "Accept": "application/json",
                              "Host": "data.sec.gov"}
            )
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            recent = data["filings"]["recent"]
            rows = []
            for form, filed, acc, doc in zip(
                recent["form"], recent["filingDate"],
                recent["accessionNumber"], recent["primaryDocument"],
            ):
                rows.append({
                    "form": form, "filed": filed,
                    "description": _curated_description(form, filed),
                    "accession": acc, "primary_doc": doc,
                })
                if len(rows) >= limit:
                    break
            return {
                "company": data.get("name", COMPANY_NAME), "ticker": ref.SPCX_TICKER,
                "cik": ref.SPCX_CIK, "source": "live", "filings": rows,
            }
        except Exception:
            pass
    return {
        "company": COMPANY_NAME, "ticker": ref.SPCX_TICKER, "cik": ref.SPCX_CIK,
        "source": "mock", "filings": ref.FILINGS[:limit],
    }


# ─── Event-study metrics ─────────────────────────────────────────────────────

def compute_event_study(spcx_prices: list[dict], index_prices: list[dict]) -> dict:
    """IPO-anchored + index-inclusion-anchored return metrics for SPCX vs. the
    Nasdaq-100, both indexed to SPCX's first trading day."""
    if not spcx_prices:
        return {}

    first_date = spcx_prices[0]["date"]
    latest = spcx_prices[-1]
    peak = max(spcx_prices, key=lambda p: p["close"])

    index_by_date = {p["date"]: p["close"] for p in index_prices}
    index_base = index_by_date.get(first_date) or (index_prices[0]["close"] if index_prices else None)
    index_latest = index_prices[-1]["close"] if index_prices else None

    spcx_since_ipo_pct = (latest["close"] / ref.IPO_PRICE - 1) * 100
    ndx_since_ipo_date_pct = (
        (index_latest / index_base - 1) * 100 if index_base and index_latest is not None else None
    )
    excess_return_since_ipo_pct = (
        spcx_since_ipo_pct - ndx_since_ipo_date_pct if ndx_since_ipo_date_pct is not None else None
    )

    price_at_inclusion = next((p["close"] for p in spcx_prices if p["date"] == ref.INCLUSION_DATE), None)
    since_inclusion_pct = (
        (latest["close"] / price_at_inclusion - 1) * 100 if price_at_inclusion else None
    )

    return {
        "ipo_price": ref.IPO_PRICE,
        "ipo_date": first_date,
        "latest_price": round(latest["close"], 2),
        "latest_date": latest["date"],
        "peak_price": round(peak["close"], 2),
        "peak_date": peak["date"],
        "spcx_since_ipo_pct": round(spcx_since_ipo_pct, 1),
        "ndx_since_ipo_date_pct": round(ndx_since_ipo_date_pct, 1) if ndx_since_ipo_date_pct is not None else None,
        "excess_return_since_ipo_pct": round(excess_return_since_ipo_pct, 1) if excess_return_since_ipo_pct is not None else None,
        "inclusion_date": ref.INCLUSION_DATE,
        "price_at_inclusion": round(price_at_inclusion, 2) if price_at_inclusion else None,
        "since_inclusion_pct": round(since_inclusion_pct, 1) if since_inclusion_pct is not None else None,
        "drawdown_from_peak_pct": round((latest["close"] / peak["close"] - 1) * 100, 1),
    }


# ─── Insights + bank-impact analysis (deterministic; doubles as the LLM fallback) ──

def compose_insights(metrics: dict) -> list[str]:
    if not metrics:
        return []
    out = [
        f"SPCX priced at ${metrics['ipo_price']:.0f} on {metrics['ipo_date']} and closed at "
        f"${metrics['latest_price']:.2f} on {metrics['latest_date']} ({metrics['spcx_since_ipo_pct']:+.1f}% "
        "since the IPO offer price).",
        f"Shares peaked at ${metrics['peak_price']:.2f} on {metrics['peak_date']} — "
        f"{metrics['drawdown_from_peak_pct']:+.1f}% off that high at the latest close, so most of the "
        "post-IPO pop has already unwound.",
    ]
    if metrics.get("ndx_since_ipo_date_pct") is not None:
        out.append(
            f"Over the same window the {ref.INDEX_NAME} moved {metrics['ndx_since_ipo_date_pct']:+.1f}%, "
            f"putting SPCX's excess return at {metrics['excess_return_since_ipo_pct']:+.1f}pp vs. the index."
        )
    if metrics.get("since_inclusion_pct") is not None:
        out.append(
            f"Since the fast-tracked {ref.INDEX_NAME} inclusion on {metrics['inclusion_date']}, SPCX is "
            f"{metrics['since_inclusion_pct']:+.1f}% — the forced index-fund buying did not durably support "
            "the stock."
        )
    out.append(
        f"SPCX's {ref.INDEX_NAME} entry came just 15 trading days after its IPO under a 2026 Nasdaq rule "
        "change that waives the usual seasoning/free-float wait for top-40-by-market-cap listings — a much "
        "faster path than the S&P 500, which requires four consecutive quarters of GAAP profitability and "
        "makes SpaceX (a $4.9B net loss most recently) ineligible before mid-2027 at the earliest."
    )
    return out


def bank_impact_sections(metrics: dict) -> list[dict]:
    since_ipo = metrics.get("spcx_since_ipo_pct") if metrics else None
    drawdown = metrics.get("drawdown_from_peak_pct") if metrics else None
    since_incl = metrics.get("since_inclusion_pct") if metrics else None
    return [
        {"title": "Equity capital markets", "points": [
            "The largest IPO on record (~$75B raised) plus a same-month senior notes offering generated a "
            "sizable underwriting/advisory fee pool across the syndicate — a reference deal for sizing and "
            "structuring other pre-IPO mega-cap listings.",
            "The fast-tracked Nasdaq-100 inclusion (15 trading days post-IPO) is a new precedent ECM desks "
            "should factor into listing-timeline and index-eligibility advice for other large private "
            "companies weighing an IPO.",
        ]},
        {"title": "Index-fund / ETF flows", "points": [
            "Passive Nasdaq-100 trackers had to buy SPCX within days of the inclusion announcement, "
            "concentrated forced buying that landed right as the stock was already giving back its post-IPO "
            "peak.",
            f"FinTechCo's index-fund and ETF clients absorbed that buy-in near a local top — SPCX is "
            f"{since_incl:+.1f}% since inclusion" if since_incl is not None else
            "FinTechCo's index-fund and ETF clients absorbed that buy-in near a local top.",
        ]},
        {"title": "Prime brokerage & securities-based lending", "points": [
            f"A {drawdown:+.1f}% drawdown from peak raises margin-call risk on concentrated SPCX positions "
            "carried on securities-based lines — lending desks should tighten haircuts/LTV on SPCX collateral "
            "until the stock's realized volatility settles." if drawdown is not None else
            "Elevated realized volatility since the IPO raises margin-call risk on concentrated SPCX "
            "positions carried on securities-based lines.",
            "Stock-loan desks should expect elevated borrow demand/fee income given short interest typical of "
            "a richly-valued, newly-indexed mega-cap.",
        ]},
        {"title": "Wealth / private banking", "points": [
            "Clients holding pre-IPO SpaceX equity or who chased the post-listing pop are sitting on paper "
            f"losses from the ${metrics.get('peak_price', 0):.0f} peak" if metrics else
            "Clients holding pre-IPO SpaceX equity or who chased the post-listing pop are sitting on paper "
            "losses from the post-IPO peak.",
            "Relationship managers should proactively raise concentration risk and diversification/hedging "
            "(collars, exchange funds) for clients with outsized single-stock SPCX exposure.",
        ]},
        {"title": "Corporate banking", "points": [
            "SpaceX is a newly public issuer with fresh treasury, cash-management, and debt-market needs "
            "(the senior notes offering) — a competitive opportunity to pitch corporate/commercial banking "
            "services now that it carries public-company disclosure and governance obligations.",
            "The IPO and notes proceeds materially expand SpaceX's balance-sheet capacity, relevant to any "
            "existing or prospective credit facilities.",
        ]},
        {"title": "Risk management", "points": [
            "The IPO-to-peak-to-unwind path (a swing of over 90 percentage points in six weeks) is a useful "
            "stress-test case for concentrated single-name exposure across the bank's book.",
            "Because SPCX now sits inside the Nasdaq-100, its volatility has a direct, mechanical read-through "
            "to index-tracking books and correlation assumptions used in broader risk models.",
        ]},
    ]


# ─── Assembled dashboard payload ─────────────────────────────────────────────

def get_dashboard_payload() -> dict:
    """Everything the ``/api/spacex-analytics`` endpoint and the client-side PDF
    report need, except the LLM narrative (generated + cached separately)."""
    spcx = get_price_series(ref.SPCX_TICKER, ref.SPCX_PRICES)
    index = get_price_series(ref.INDEX_TICKER, ref.NDX_PRICES)
    filings = get_filings()
    fred = fred_data.get_economic_snapshot()
    metrics = compute_event_study(spcx["prices"], index["prices"])

    return {
        "company": COMPANY_NAME,
        "ticker": ref.SPCX_TICKER,
        "index_name": ref.INDEX_NAME,
        "index_ticker": ref.INDEX_TICKER,
        "timeline": ref.TIMELINE,
        "prices": {"spcx": spcx, "index": index},
        "metrics": metrics,
        "insights": compose_insights(metrics),
        "filings": filings,
        "fred": fred,
        "bank_impact": bank_impact_sections(metrics),
    }
