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
Live macroeconomic context from the **FRED API** (Federal Reserve Bank of St.
Louis) for the SpaceX index-inclusion case study.

Design mirrors :mod:`server.market_data`: live with graceful mock fallback,
each response tagged ``"source": "live"`` or ``"source": "mock"``, and
``DEMO_DISABLE_LIVE_MARKET=1`` forces the offline path (used by tests/CI).
Stdlib-only (``urllib``) plus ``python-dotenv`` to read ``FRED_API_KEY`` from
``backend/.env`` — no ``pandas`` or FRED SDK dependency.
"""

import datetime
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

_TIMEOUT = 6
_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Load backend/.env once at import time so FRED_API_KEY is available even when
# the process wasn't started with the env var already exported.
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass

# series_id -> (label, units label, decimals). CPI is handled separately
# below because it needs a year-over-year calculation, not a raw reading.
_RATE_SERIES = {
    "DFF": ("Effective Federal Funds Rate", "%", 2),
    "DGS10": ("10-Year Treasury Yield", "%", 2),
    "DGS2": ("2-Year Treasury Yield", "%", 2),
    "UNRATE": ("Unemployment Rate", "%", 1),
}
_CPI_SERIES = "CPIAUCSL"

# Baked-in offline fallback, sourced from a live FRED pull on 2026-07-28 so the
# mock path reflects a real, recent macro snapshot rather than placeholder
# numbers. See implementation.md for how this was captured.
_MOCK_SNAPSHOT = {
    "as_of": "2026-07-27",
    "source": "mock",
    "series": {
        "DFF": {"label": "Effective Federal Funds Rate", "units": "%", "value": 3.63, "prior": 3.63, "date": "2026-07-27"},
        "DGS10": {"label": "10-Year Treasury Yield", "units": "%", "value": 4.65, "prior": 4.69, "date": "2026-07-27"},
        "DGS2": {"label": "2-Year Treasury Yield", "units": "%", "value": 4.31, "prior": 4.33, "date": "2026-07-27"},
        "UNRATE": {"label": "Unemployment Rate", "units": "%", "value": 4.2, "prior": 4.3, "date": "2026-06-01"},
        "CPIAUCSL": {"label": "CPI (Year-over-Year)", "units": "%", "value": 3.46, "prior": 3.39, "date": "2026-06-01"},
    },
    "yield_curve_10y2y": 0.34,
}


def _live_disabled() -> bool:
    return os.getenv("DEMO_DISABLE_LIVE_MARKET", "").strip().lower() in ("1", "true", "yes")


def _r(x, n=2):
    return round(x, n) if isinstance(x, (int, float)) else x


def _fetch_observations(series_id: str, limit: int = 14) -> list[dict]:
    api_key = os.getenv("FRED_API_KEY", "")
    if not api_key:
        raise RuntimeError("FRED_API_KEY not set")
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit,
    }
    url = f"{_BASE_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [o for o in data.get("observations", []) if o.get("value") not in (None, ".")]


def _latest_rate(series_id: str) -> tuple[float, float, str]:
    """Return (latest_value, prior_value, latest_date) for a daily/monthly rate series."""
    obs = _fetch_observations(series_id, limit=14)
    if not obs:
        raise RuntimeError(f"no observations for {series_id}")
    latest = float(obs[0]["value"])
    prior = float(obs[1]["value"]) if len(obs) > 1 else latest
    return latest, prior, obs[0]["date"]


def _cpi_yoy() -> tuple[float, float, str]:
    """Year-over-year CPI inflation for the latest month and the month before."""
    obs = _fetch_observations(_CPI_SERIES, limit=14)
    if len(obs) < 13:
        raise RuntimeError("not enough CPI history for a YoY calc")
    by_date = {o["date"]: float(o["value"]) for o in obs}
    dates = sorted(by_date, reverse=True)
    latest_date = dates[0]
    prior_date = dates[1]

    def _yoy_at(date_str: str) -> float:
        d = datetime.date.fromisoformat(date_str)
        year_ago = d.replace(year=d.year - 1).isoformat()
        if date_str not in by_date or year_ago not in by_date:
            raise RuntimeError("missing year-ago CPI observation")
        return (by_date[date_str] - by_date[year_ago]) / by_date[year_ago] * 100

    return _yoy_at(latest_date), _yoy_at(prior_date), latest_date


def get_economic_snapshot() -> dict:
    """Latest macro snapshot: fed funds, 10Y/2Y treasury, CPI YoY, unemployment.

    Returns ``{as_of, source, series:{id:{label, units, value, prior, date}},
    yield_curve_10y2y}``. Falls back to :data:`_MOCK_SNAPSHOT` (a real FRED
    pull captured 2026-07-28) on any failure or when live fetches are off.
    """
    if _live_disabled():
        return json.loads(json.dumps(_MOCK_SNAPSHOT))

    try:
        series = {}
        for sid, (label, units, decimals) in _RATE_SERIES.items():
            value, prior, date = _latest_rate(sid)
            series[sid] = {"label": label, "units": units, "value": _r(value, decimals),
                           "prior": _r(prior, decimals), "date": date}

        cpi_value, cpi_prior, cpi_date = _cpi_yoy()
        series["CPIAUCSL"] = {
            "label": "CPI (Year-over-Year)", "units": "%",
            "value": _r(cpi_value), "prior": _r(cpi_prior), "date": cpi_date,
        }

        latest_date = max(s["date"] for s in series.values())
        yield_curve = _r(series["DGS10"]["value"] - series["DGS2"]["value"])

        return {
            "as_of": latest_date,
            "source": "live",
            "series": series,
            "yield_curve_10y2y": yield_curve,
        }
    except Exception:
        return json.loads(json.dumps(_MOCK_SNAPSHOT))
