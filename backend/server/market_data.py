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
Live public-company market intelligence for the SSIM assistant — **SEC EDGAR**
(recent 10-K / 10-Q / 8-K filings) and **Yahoo Finance** (quote, price move,
next earnings, headlines).

Design:
- **Stdlib only** (``urllib`` + ``http.cookiejar``) — no ``yfinance``/``pandas``
  dependency, so the container stays slim. The Yahoo path performs the required
  cookie + crumb handshake itself.
- **Live with graceful mock fallback**: every function calls the real API and,
  on any error/timeout, returns the baked-in fixtures from
  :mod:`server.mock_data`. Each response is tagged ``"source": "live"`` or
  ``"source": "mock"`` so callers/UI can show provenance.
- **Stock quotes get a second live tier**: if Yahoo's cookie/crumb handshake
  fails, :func:`get_stock_snapshot` scrapes Google's search results page for
  its inline stock answer box (price + move) before giving up to mock. This is
  a best-effort convenience, not a supported API — Google's markup is
  undocumented and can change or serve a cookie-consent page without notice,
  so failures here are expected and silently degrade to mock.
- **Deterministic offline mode**: set ``SSIM_DISABLE_LIVE_MARKET=1`` to skip the
  network entirely and always return the mock fixtures. Used by the test suite
  and CI so runs are fast and hermetic.

No :class:`server.store.Store` dependency — these are pure network helpers over
module-level constants. Store-aware caching lives in :mod:`server.logic`.
"""

import datetime
import http.cookiejar
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

from server import mock_data

# SEC requires a descriptive User-Agent identifying the requester.
_SEC_UA = "SSIM Employee Digital Assistant demo (contact: dev@chenkeamonwang.altostrat.com)"
# Yahoo's public endpoints want a browser-like UA + a cookie/crumb pair.
_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120 Safari/537.36"
)
_TIMEOUT = 6  # seconds — keep the request budget tight so the UI stays snappy
_SEC_FORMS = ("10-K", "10-Q", "8-K")


def _live_disabled() -> bool:
    """True when live fetches are switched off (offline/CI/testing)."""
    return os.getenv("SSIM_DISABLE_LIVE_MARKET", "").strip().lower() in ("1", "true", "yes")


def _r(x, n=2):
    """Round floats for display; pass through anything non-numeric untouched."""
    return round(x, n) if isinstance(x, (int, float)) else x


# ─── SEC EDGAR ───────────────────────────────────────────────────────────────

def get_sec_filings(ticker: str, cik: str, form_type: str = "", limit: int = 6) -> dict:
    """Recent SEC filings for a public company.

    Returns ``{company, ticker, cik, source, filings:[{form, filed, period,
    accession, primary_doc, url}]}``. Falls back to
    :data:`server.mock_data.MOCK_SEC_FILINGS` on any failure.
    """
    ticker = (ticker or "").upper()
    forms = (form_type.upper(),) if form_type else _SEC_FORMS

    if _live_disabled():
        return _mock_sec(ticker, forms, limit)

    try:
        cik_int = int(cik)
        url = f"https://data.sec.gov/submissions/CIK{cik_int:010d}.json"
        req = urllib.request.Request(
            url, headers={"User-Agent": _SEC_UA, "Accept": "application/json",
                          "Host": "data.sec.gov"}
        )
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        recent = data["filings"]["recent"]
        rows = []
        for form, filed, period, acc, doc in zip(
            recent["form"], recent["filingDate"], recent["reportDate"],
            recent["accessionNumber"], recent["primaryDocument"],
        ):
            if form not in forms:
                continue
            acc_nodash = acc.replace("-", "")
            if doc:
                doc_url = (f"https://www.sec.gov/Archives/edgar/data/"
                           f"{cik_int}/{acc_nodash}/{doc}")
            else:
                doc_url = (f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany"
                           f"&CIK={cik_int:010d}&type={form}")
            rows.append({
                "form": form, "filed": filed, "period": period,
                "accession": acc, "primary_doc": doc, "url": doc_url,
            })
            if len(rows) >= limit:
                break

        return {
            "company": data.get("name", ticker),
            "ticker": ticker,
            "cik": f"{cik_int:010d}",
            "source": "live",
            "filings": rows,
        }
    except Exception:
        return _mock_sec(ticker, forms, limit)


def _mock_sec(ticker: str, forms, limit: int) -> dict:
    base = mock_data.MOCK_SEC_FILINGS.get(ticker)
    if not base:
        return {"company": ticker, "ticker": ticker, "cik": "", "source": "mock", "filings": []}
    filings = [f for f in base["filings"] if f["form"] in forms][:limit]
    return {**base, "filings": filings, "source": "mock"}


# ─── Yahoo Finance (cookie + crumb handshake, stdlib) ────────────────────────

# Cached (opener, crumb) so we handshake once per process; refreshed on 401.
_yahoo_session = None


def _new_yahoo_opener():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [("User-Agent", _BROWSER_UA), ("Accept", "*/*")]
    # Seed the A3 consent cookie by loading a quote page first.
    try:
        opener.open("https://finance.yahoo.com/quote/AAPL", timeout=_TIMEOUT).read()
    except Exception:
        pass
    return opener


def _yahoo_session_pair(refresh: bool = False):
    global _yahoo_session
    if _yahoo_session and not refresh:
        return _yahoo_session
    opener = _new_yahoo_opener()
    req = urllib.request.Request("https://query1.finance.yahoo.com/v1/test/getcrumb")
    with opener.open(req, timeout=_TIMEOUT) as resp:
        crumb = resp.read().decode("utf-8").strip()
    _yahoo_session = (opener, crumb)
    return _yahoo_session


def _yahoo_get_json(base_url: str, params: dict, needs_crumb: bool = True):
    """GET a Yahoo endpoint as JSON, refreshing the crumb once on HTTP 401."""
    for attempt in (0, 1):
        opener, crumb = _yahoo_session_pair(refresh=(attempt == 1))
        q = dict(params)
        if needs_crumb:
            q["crumb"] = crumb
        url = f"{base_url}?{urllib.parse.urlencode(q)}"
        try:
            with opener.open(url, timeout=_TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 401 and attempt == 0:
                continue  # stale crumb — refresh and retry once
            raise
    raise RuntimeError("Yahoo request failed after crumb refresh")


_EXCHANGE_MAP = {
    "NasdaqGS": "Nasdaq", "NasdaqGM": "Nasdaq", "NasdaqCM": "Nasdaq",
    "NMS": "Nasdaq", "NGM": "Nasdaq",
    "NYQ": "NYSE", "New York Stock Exchange": "NYSE", "NYSE": "NYSE",
}


def _norm_exchange(name: str) -> str:
    return _EXCHANGE_MAP.get(name, name or "")


def _yahoo_next_earnings(ticker: str) -> str:
    """Next earnings date as ``YYYY-MM-DD`` (best effort; "" if unavailable)."""
    try:
        data = _yahoo_get_json(
            f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}",
            {"modules": "calendarEvents"},
        )
        events = data["quoteSummary"]["result"][0]["calendarEvents"]["earnings"]["earningsDate"]
        if not events:
            return ""
        first = events[0]
        if isinstance(first, dict):
            if first.get("fmt"):
                return first["fmt"]
            raw = first.get("raw")
            if raw:
                return datetime.datetime.utcfromtimestamp(raw).date().isoformat()
        return ""
    except Exception:
        return ""


def _yahoo_news(ticker: str, count: int = 3) -> list:
    """Recent headlines for a ticker (best effort; [] if unavailable)."""
    try:
        data = _yahoo_get_json(
            "https://query1.finance.yahoo.com/v1/finance/search",
            {"q": ticker, "newsCount": count, "quotesCount": 0},
            needs_crumb=False,
        )
        out = []
        for item in (data.get("news") or [])[:count]:
            ts = item.get("providerPublishTime")
            date = ""
            if ts:
                date = datetime.datetime.utcfromtimestamp(ts).date().isoformat()
            out.append({
                "headline": item.get("title", ""),
                "source": item.get("publisher", ""),
                "date": date,
                "url": item.get("link", ""),
            })
        return out
    except Exception:
        return []


def get_stock_snapshot(ticker: str) -> dict:
    """Live quote + next earnings + headlines for a public company.

    Returns ``{ticker, company, exchange, currency, source, quote{...},
    next_earnings_date, news[...]}``. Tries Yahoo Finance first; if that fails,
    tries scraping a live price/move off Google Search (see module docstring);
    falls back to :data:`server.mock_data.MOCK_YAHOO_FINANCE` if both fail.
    """
    ticker = (ticker or "").upper()

    if _live_disabled():
        return _mock_stock(ticker)

    try:
        data = _yahoo_get_json(
            "https://query1.finance.yahoo.com/v7/finance/quote",
            {"symbols": ticker},
        )
        result = data["quoteResponse"]["result"]
        if not result:
            raise ValueError(f"no Yahoo quote result for {ticker}")
        q = result[0]
        snap = {
            "ticker": ticker,
            "company": q.get("longName") or q.get("shortName") or ticker,
            "exchange": _norm_exchange(q.get("fullExchangeName", "")),
            "currency": q.get("currency", "USD"),
            "source": "live",
            "quote": {
                "price": _r(q.get("regularMarketPrice")),
                "change": _r(q.get("regularMarketChange")),
                "change_pct": _r(q.get("regularMarketChangePercent")),
                "prev_close": _r(q.get("regularMarketPreviousClose")),
                "day_low": _r(q.get("regularMarketDayLow")),
                "day_high": _r(q.get("regularMarketDayHigh")),
                "week52_low": _r(q.get("fiftyTwoWeekLow")),
                "week52_high": _r(q.get("fiftyTwoWeekHigh")),
                "volume": q.get("regularMarketVolume"),
                "market_cap": q.get("marketCap"),
                "pe_ratio": _r(q.get("trailingPE")),
            },
            "next_earnings_date": _yahoo_next_earnings(ticker),
            "news": _yahoo_news(ticker),
        }
        return snap
    except Exception:
        google_quote = _fetch_google_quote(ticker)
        if google_quote:
            return _stock_with_google_quote(ticker, google_quote)
        return _mock_stock(ticker)


# ─── Google Search (second live tier — best effort, no API) ─────────────────

# Matches Google's mobile-layout answer-box price span, e.g.
# `<div class="BNeawe iBp4i AP7Wnd">$226.74</div>`. Undocumented and can
# change without notice — see the module docstring.
_GOOGLE_PRICE_RE = re.compile(r'BNeawe iBp4i AP7Wnd">\$?([\d,]+\.\d+)<')
_GOOGLE_MOVE_RE = re.compile(
    r'BNeawe[\w ]*AP7Wnd">\s*([+\-][\d,]+\.\d+)\s*\(?([+\-]?[\d.]+)%\)?'
)


def _parse_google_quote(html: str) -> dict | None:
    """Best-effort extraction of ``{price, change, change_pct}`` from a Google
    search results page for a stock ticker query. Returns ``None`` if the
    expected answer-box markup isn't present (layout change, consent
    interstitial, no results, etc.) — the caller falls back to mock."""
    price_match = _GOOGLE_PRICE_RE.search(html)
    if not price_match:
        return None
    quote = {"price": _r(float(price_match.group(1).replace(",", ""))), "change": None, "change_pct": None}
    move_match = _GOOGLE_MOVE_RE.search(html)
    if move_match:
        quote["change"] = _r(float(move_match.group(1).replace(",", "")))
        quote["change_pct"] = _r(float(move_match.group(2)))
    return quote


def _fetch_google_quote(ticker: str) -> dict | None:
    """Scrape a live price/move for ``ticker`` off Google Search. Returns
    ``None`` on any failure (network, blocked, unparseable) — never raises."""
    try:
        query = urllib.parse.quote_plus(f"{ticker} stock price")
        url = f"https://www.google.com/search?q={query}&hl=en&gl=us"
        req = urllib.request.Request(
            url, headers={"User-Agent": _BROWSER_UA, "Accept-Language": "en-US,en;q=0.9"}
        )
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        return _parse_google_quote(html)
    except Exception:
        return None


def _stock_with_google_quote(ticker: str, google_quote: dict) -> dict:
    """Mock company/exchange/earnings/news metadata with a live price/move
    scraped from Google layered on top — used when Yahoo is unreachable."""
    snap = _mock_stock(ticker)
    snap["source"] = "live"
    snap["quote"] = {
        **snap.get("quote", {}),
        **{k: v for k, v in google_quote.items() if v is not None},
    }
    return snap


def _mock_stock(ticker: str) -> dict:
    base = mock_data.MOCK_YAHOO_FINANCE.get(ticker)
    if not base:
        return {"ticker": ticker, "company": ticker, "exchange": "", "currency": "USD",
                "source": "mock", "quote": {}, "next_earnings_date": "", "news": []}
    return {"ticker": ticker, "source": "mock", **base}
