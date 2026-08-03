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
self-contained analytics case study, independent of the FinTechCo
demo-customer domain (``mock_data.py``/``seed.py``).

SpaceX IPO'd 2026-06-12 (ticker ``SPCX``, CIK 0001181412) and was fast-tracked
into the Nasdaq-100 on 2026-07-06 under a 2026 Nasdaq rule change — real,
dated facts captured in :mod:`server.spacex_reference_data`.

🔴 Live-only, no mock/fixture fallback — per CLAUDE.md's "No mock data" policy
for new live-data integrations, this module does NOT fall back to
``spacex_reference_data``'s baked price/filing snapshot at runtime the way
``market_data``/``fred_data`` fall back to their own baked snapshots.
``spacex_reference_data``'s ``SPCX_PRICES``/``NDX_PRICES``/``FILINGS``
constants exist only as fixtures for tests to monkeypatch against. Its
``TIMELINE`` (editorial chronology, not a live feed) is the only data this
module uses directly, alongside a ``_CURATED_DESCRIPTIONS`` lookup built from
``FILINGS`` here to enrich (never invent) live SEC filing descriptions. FRED
macro data is the one exception: ``fred_data.get_economic_snapshot()`` is
reused unchanged, since its live/mock fallback predates this policy.
"""

import datetime
import json
import urllib.error
import urllib.request

from server import fred_data, market_data
from server import spacex_reference_data as ref

_FORMS = ("S-1", "S-1/A", "8-A12B", "424B4", "S-8", "8-K")

# Hand-written descriptions for filings this module actually fetches live,
# keyed by accession number — SEC's own ``primaryDocDescription`` is usually
# just the form code repeated, not a useful summary. Enrichment only: a live
# filing whose accession isn't in this map falls back to SEC's own
# description (or an empty string), never a fabricated one.
_CURATED_DESCRIPTIONS = {f["accession"]: f["description"] for f in ref.FILINGS}


def _pct(new: float, old: float) -> float | None:
    if not old:
        return None
    return round((new - old) / old * 100, 2)


# ─── Live price series ───────────────────────────────────────────────────────

def get_price_series() -> dict:
    """SPCX + Nasdaq-100 daily close history, live via Yahoo Finance.

    Returns ``{spcx: {source, prices:[{date,close}]}, index: {...}}``, SPCX
    trimmed to the IPO date onward. Raises straight through on failure — no
    fallback — so the caller can surface a clear error instead of fabricated
    numbers.
    """
    spcx_raw = market_data.get_price_history(ref.SPCX_TICKER, range_="1y", interval="1d")
    index_raw = market_data.get_price_history(ref.INDEX_TICKER, range_="1y", interval="1d")

    spcx_prices = [p for p in spcx_raw["prices"] if p["date"] >= ref.IPO_DATE]
    if not spcx_prices:
        raise RuntimeError(f"no {ref.SPCX_TICKER} price data on/after IPO date {ref.IPO_DATE}")

    # A couple weeks of pre-IPO index context, same shape as the reference data.
    index_cutoff = (datetime.date.fromisoformat(ref.IPO_DATE) - datetime.timedelta(days=14)).isoformat()
    index_prices = [p for p in index_raw["prices"] if p["date"] >= index_cutoff]

    return {
        "spcx": {"source": spcx_raw["source"], "prices": spcx_prices},
        "index": {"source": index_raw["source"], "prices": index_prices},
    }


# ─── Live SEC EDGAR filings ──────────────────────────────────────────────────

def _fetch_filings_raw() -> list[dict]:
    """Raw SEC EDGAR submissions for SpaceX's CIK, unfiltered by dedup/enrichment.

    Separated from :func:`get_filings` so tests can monkeypatch this one seam
    instead of the network call directly.
    """
    cik_int = int(ref.SPCX_CIK)
    url = f"https://data.sec.gov/submissions/CIK{cik_int:010d}.json"
    req = urllib.request.Request(
        url, headers={"User-Agent": market_data._SEC_UA, "Accept": "application/json",
                      "Host": "data.sec.gov"}
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    recent = data["filings"]["recent"]
    forms = recent.get("form", [])
    filed_dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    docs = recent.get("primaryDocument", [])
    descs = recent.get("primaryDocDescription", [])

    rows = []
    for i, form in enumerate(forms):
        if form not in _FORMS:
            continue
        rows.append({
            "form": form,
            "filed": filed_dates[i] if i < len(filed_dates) else "",
            "accession": accessions[i] if i < len(accessions) else "",
            "primary_doc": docs[i] if i < len(docs) else "",
            "raw_description": descs[i] if i < len(descs) else "",
        })
    return rows


def get_filings(limit: int = 11) -> dict:
    """Recent SpaceX IPO/listing filings (broader form set than the generic
    customer-domain SEC helper, since these tell the IPO story).

    Returns ``{company, ticker, cik, source, filings:[{form, filed,
    description, accession, url}]}``, deduped by ``(form, filed)`` and sorted
    newest-first. Raises on failure — no fallback.
    """
    raw = _fetch_filings_raw()
    cik_int = int(ref.SPCX_CIK)

    seen = set()
    rows = []
    for r in raw:
        key = (r["form"], r["filed"])
        if key in seen:
            continue
        seen.add(key)

        acc = r["accession"]
        doc = r.get("primary_doc") or ""
        if doc and acc:
            url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc.replace('-', '')}/{doc}"
        else:
            url = (f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany"
                   f"&CIK={cik_int:010d}&type={r['form']}")

        rows.append({
            "form": r["form"],
            "filed": r["filed"],
            "accession": acc,
            "description": _CURATED_DESCRIPTIONS.get(acc) or r.get("raw_description") or "",
            "url": url,
        })

    rows.sort(key=lambda r: r["filed"], reverse=True)
    return {
        "company": "SPACE EXPLORATION TECHNOLOGIES CORP",
        "ticker": ref.SPCX_TICKER,
        "cik": f"{cik_int:010d}",
        "source": "live",
        "filings": rows[:limit],
    }


# ─── Event-study metrics + insights ──────────────────────────────────────────

def compute_event_study(prices: dict) -> dict:
    """Offer/first-close/peak/latest/inclusion-date prices and their % moves,
    plus SPCX's excess return net of the index's own move since the IPO."""
    spcx = prices["spcx"]["prices"]
    index = prices["index"]["prices"]
    if not spcx:
        raise RuntimeError("no SPCX price data to compute event study")

    first = spcx[0]
    latest = spcx[-1]
    peak = max(spcx, key=lambda p: p["close"])

    def _index_close_on_or_before(date: str):
        candidates = [p for p in index if p["date"] <= date]
        return candidates[-1] if candidates else (index[0] if index else None)

    ipo_index = _index_close_on_or_before(first["date"])
    latest_index = _index_close_on_or_before(latest["date"])
    ndx_since_ipo_date_pct = (
        _pct(latest_index["close"], ipo_index["close"]) if ipo_index and latest_index else None
    )
    spcx_since_ipo_pct = _pct(latest["close"], ref.IPO_PRICE)
    excess_return_since_ipo_pct = (
        round(spcx_since_ipo_pct - ndx_since_ipo_date_pct, 2)
        if spcx_since_ipo_pct is not None and ndx_since_ipo_date_pct is not None else None
    )

    metrics = {
        "ipo_price": ref.IPO_PRICE,
        "ipo_date": ref.IPO_DATE,
        "first_close": first["close"],
        "first_close_date": first["date"],
        "peak_price": peak["close"],
        "peak_date": peak["date"],
        "latest_price": latest["close"],
        "latest_date": latest["date"],
        "spcx_since_ipo_pct": spcx_since_ipo_pct,
        "ndx_since_ipo_date_pct": ndx_since_ipo_date_pct,
        "excess_return_since_ipo_pct": excess_return_since_ipo_pct,
    }

    inclusion_row = next((p for p in spcx if p["date"] >= ref.INCLUSION_DATE), None)
    if inclusion_row:
        metrics["inclusion_date"] = ref.INCLUSION_DATE
        metrics["inclusion_price"] = inclusion_row["close"]
        metrics["spcx_since_inclusion_pct"] = _pct(latest["close"], inclusion_row["close"])

    return metrics


def compose_insights(metrics: dict) -> list[str]:
    """Deterministic, data-driven bullet insights — also the LLM narrative's
    fallback when the model is unavailable."""
    insights = []

    ipo_move = _pct(metrics["first_close"], metrics["ipo_price"])
    insights.append(
        f"SPCX priced at ${metrics['ipo_price']:.2f} and closed its first trading day "
        f"({metrics['first_close_date']}) at ${metrics['first_close']:.2f}"
        + (f" ({ipo_move:+.1f}%)." if ipo_move is not None else ".")
    )

    peak_move = _pct(metrics["peak_price"], metrics["ipo_price"])
    insights.append(
        f"Shares peaked at ${metrics['peak_price']:.2f} on {metrics['peak_date']}"
        + (f", {peak_move:+.1f}% above the offer price." if peak_move is not None else ".")
    )

    if metrics.get("spcx_since_inclusion_pct") is not None:
        insights.append(
            f"Since {ref.INDEX_NAME} inclusion on {metrics['inclusion_date']}, SPCX is "
            f"{metrics['spcx_since_inclusion_pct']:+.1f}% (inclusion-day price ${metrics['inclusion_price']:.2f})."
        )

    if metrics.get("excess_return_since_ipo_pct") is not None:
        insights.append(
            f"As of {metrics['latest_date']}, SPCX is {metrics['spcx_since_ipo_pct']:+.1f}% since the IPO "
            f"vs. the {ref.INDEX_NAME}'s {metrics['ndx_since_ipo_date_pct']:+.1f}% over the same period — "
            f"an excess return of {metrics['excess_return_since_ipo_pct']:+.1f} percentage points, consistent "
            "with index-fund-driven demand around the fast-tracked inclusion."
        )

    return insights


def bank_impact_sections(metrics: dict) -> list[dict]:
    """Six categorized "impact on bank operations" sections, each with 1-2
    points referencing the computed metrics."""
    excess = metrics.get("excess_return_since_ipo_pct")
    since_ipo = metrics.get("spcx_since_ipo_pct")
    peak_move = _pct(metrics["peak_price"], metrics["ipo_price"])

    return [
        {
            "title": "Equity capital markets & underwriting",
            "points": [
                f"The {ref.IPO_RAISE} raise at a {ref.IPO_VALUATION} valuation is one of the largest ECM "
                "mandates of the year — a template for pricing and syndicating mega-cap IPOs of this size.",
                "A senior notes offering launched days after the IPO shows debt and equity capital markets "
                "teams cross-selling the same issuer within weeks of a listing.",
            ],
        },
        {
            "title": "Index-fund & ETF flows",
            "points": [
                f"Fast-track {ref.INDEX_NAME} inclusion forces passive funds/ETFs tracking the index to buy "
                "SPCX regardless of view, concentrating flow risk around the inclusion date into a "
                "predictable, bank-tradable liquidity event.",
                "Custody, index-fund, and ETF authorized-participant (creation/redemption) desks see a "
                "step-change in SPCX-related flow in the weeks around inclusion.",
            ],
        },
        {
            "title": "Prime brokerage & securities-based lending",
            "points": [
                (f"The {peak_move:+.1f}% run to the post-IPO peak, followed by a pullback, is the kind of "
                 "volatility that drives margin/SBL utilization and stress-testing on concentrated single-stock "
                 "positions." if peak_move is not None else
                 "Sharp post-IPO price swings drive margin/SBL utilization and stress-testing on concentrated "
                 "single-stock positions."),
                "Insiders and early investors holding large unrealized gains become natural "
                "securities-based-lending clients once lockups begin to lift.",
            ],
        },
        {
            "title": "Wealth & private banking",
            "points": [
                "Concentrated single-stock wealth (employees, early investors) needs hedging/diversification "
                "advice — collars, exchange funds, and structured monetization strategies are live conversations "
                "right after a mega-IPO like this.",
                (f"Clients holding SPCX since the IPO are sitting on a {since_ipo:+.1f}% price move as of "
                 f"{metrics['latest_date']}; volatility this large is a natural trigger for a portfolio review."
                 if since_ipo is not None else
                 "Clients holding SPCX since the IPO have seen large price swings — a natural trigger for a "
                 "portfolio review."),
            ],
        },
        {
            "title": "Corporate banking",
            "points": [
                "A newly-public issuer of this scale becomes a target for treasury, cash-management, and "
                "revolving-credit-facility relationships as it stands up public-company treasury operations.",
                "Debt investors from the senior notes offering are a natural entry point for a broader "
                "corporate-banking relationship beyond the IPO itself.",
            ],
        },
        {
            "title": "Risk management",
            "points": [
                (f"An excess return of {excess:+.1f} percentage points vs. the {ref.INDEX_NAME} since the IPO "
                 "shows index-inclusion-driven flow can dominate fundamentals in the near term — a factor risk "
                 "desks need to price into single-name concentration limits." if excess is not None else
                 "Elevated single-name volatility around a mega-IPO and fast-track index inclusion is a factor "
                 "risk desks need to price into concentration limits."),
                "A macro backdrop of shifting rates and yield-curve moves (see the FRED snapshot) compounds "
                "single-stock risk for any desk carrying SPCX exposure on inventory or as collateral.",
            ],
        },
    ]


# ─── Assembled dashboard payload ─────────────────────────────────────────────

def get_dashboard_payload() -> dict:
    """Assemble the full SpaceX analytics dashboard payload for the API/PDF.

    Raises if live SEC/Yahoo data is unavailable — the caller (the
    ``/api/spacex-analytics`` endpoint) surfaces that as a clear error rather
    than a fabricated payload.
    """
    prices = get_price_series()
    metrics = compute_event_study(prices)
    insights = compose_insights(metrics)
    filings = get_filings()
    fred = fred_data.get_economic_snapshot()
    bank_impact = bank_impact_sections(metrics)

    # Best-effort headlines, not a fabricated fallback: [] on failure (or when
    # DEMO_DISABLE_LIVE_MARKET is set, same off-switch market_data.py itself uses)
    # is a legitimate "no headlines" result, same as market_data's own
    # next_earnings_date/news best-effort fields.
    if market_data._live_disabled():
        news = []
    else:
        try:
            news = market_data._yahoo_news(ref.SPCX_TICKER, count=6)
        except Exception:
            news = []

    return {
        "company": "SpaceX",
        "ticker": ref.SPCX_TICKER,
        "cik": ref.SPCX_CIK,
        "index_name": ref.INDEX_NAME,
        "index_ticker": ref.INDEX_TICKER,
        "ipo_date": ref.IPO_DATE,
        "ipo_raise": ref.IPO_RAISE,
        "ipo_valuation": ref.IPO_VALUATION,
        "inclusion_date": ref.INCLUSION_DATE,
        "timeline": ref.TIMELINE,
        "prices": prices,
        "metrics": metrics,
        "insights": insights,
        "filings": filings,
        "fred": fred,
        "bank_impact": bank_impact,
        "news": news,
    }
