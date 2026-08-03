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
Pre-researched, verified real-world facts for the SpaceX (NASDAQ: SPCX)
index-inclusion case study — **pure constants, no fetch/business logic**.

This is the single source of truth :mod:`server.spacex_case_study` builds on
top of. Splitting it out means a rebuild of the case study's business logic
(event-study math, insights, bank-impact analysis) or its API/UI layer never
needs to re-derive or re-fetch these facts — see implementation.md for how
they were captured (web search for the IPO/index-inclusion timeline; live
pulls from SEC EDGAR CIK 0001181412 and the Yahoo Finance chart API on
2026-07-28).

Macro/FRED data is intentionally NOT duplicated here — :mod:`server.fred_data`
is already a self-contained, reusable live-with-mock-fallback module with its
own real baked snapshot; call ``fred_data.get_economic_snapshot()`` directly.
"""

SPCX_CIK = "0001181412"
SPCX_TICKER = "SPCX"
INDEX_TICKER = "^NDX"
INDEX_NAME = "Nasdaq-100"
IPO_DATE = "2026-06-12"
IPO_PRICE = 135.0
IPO_VALUATION = "~$1.75T"
IPO_RAISE = "~$75B"
INCLUSION_DATE = "2026-07-06"

TIMELINE = [
    {"date": "2026-05-20", "label": "S-1 registration filed", "kind": "filing",
     "detail": "SpaceX files its IPO registration statement with the SEC, opening the roadshow."},
    {"date": "2026-06-10", "label": "Nasdaq listing registered (Form 8-A12B)", "kind": "filing",
     "detail": "Class A common stock registered for listing on the Nasdaq Global Select Market."},
    {"date": "2026-06-12", "label": "IPO — SPCX begins trading", "kind": "market",
     "detail": f"Priced at ${IPO_PRICE:.0f}/share (~$1.75T valuation, ~$75B raised) — the largest IPO on record. "
                "Final terms filed same-day on Form 424B4."},
    {"date": "2026-06-16", "label": "Post-IPO peak (~$211)", "kind": "market",
     "detail": "Shares peak within days of the listing, ~56% above the offer price, amid speculation about "
                "forced buying from index funds ahead of a Nasdaq-100 decision."},
    {"date": "2026-06-22", "label": "Senior notes offering launched (8-K)", "kind": "filing",
     "detail": "SpaceX launches a debt offering alongside the equity raise — priced 06-23, closed 06-26 — "
                "adding fixed-income capacity on top of the IPO proceeds."},
    {"date": INCLUSION_DATE, "label": f"Fast-tracked into the {INDEX_NAME}", "kind": "index",
     "detail": "A 2026 Nasdaq rule change lets any new listing ranked in the top 40 by market cap enter after "
                "just 15 trading days, waiving the usual seasoning/free-float wait — SpaceX enters ~3.5 weeks "
                "after its IPO, well before a typical newly-public company would qualify."},
    {"date": "2026-09-30", "label": "Russell 1000 reconstitution (expected)", "kind": "index",
     "detail": "Already added to FTSE Russell and MSCI benchmark indexes; too large for the Russell 2000 "
                "small-cap index, expected to join the Russell 1000 at the September or December 2026 "
                "reconstitution."},
    {"date": "2027-06-30", "label": "Earliest realistic S&P 500 eligibility", "kind": "index",
     "detail": "S&P Dow Jones Indices declined to fast-track mega-IPOs and requires a full year of trading "
                "plus four consecutive quarters of GAAP profitability. SpaceX reported a $4.9B net loss in "
                "its most recent fiscal year, so S&P 500 inclusion is not realistic before mid-2027."},
]

# Daily close prices, captured from a live Yahoo Finance chart-API pull on
# 2026-07-28. SPCX_PRICES starts on the IPO date; NDX_PRICES starts a bit
# earlier for pre-IPO context.
SPCX_PRICES = [{"date": "2026-06-12", "close": 160.95}, {"date": "2026-06-15", "close": 192.5}, {"date": "2026-06-16", "close": 211.39}, {"date": "2026-06-17", "close": 191.82}, {"date": "2026-06-18", "close": 185.0}, {"date": "2026-06-22", "close": 154.6}, {"date": "2026-06-23", "close": 156.11}, {"date": "2026-06-24", "close": 154.54}, {"date": "2026-06-25", "close": 153.0}, {"date": "2026-06-26", "close": 153.23}, {"date": "2026-06-29", "close": 164.19}, {"date": "2026-06-30", "close": 170.86}, {"date": "2026-07-01", "close": 157.54}, {"date": "2026-07-02", "close": 162.0}, {"date": "2026-07-06", "close": 160.42}, {"date": "2026-07-07", "close": 149.47}, {"date": "2026-07-08", "close": 148.3}, {"date": "2026-07-09", "close": 152.16}, {"date": "2026-07-10", "close": 145.3}, {"date": "2026-07-13", "close": 139.14}, {"date": "2026-07-14", "close": 136.08}, {"date": "2026-07-15", "close": 135.27}, {"date": "2026-07-16", "close": 131.11}, {"date": "2026-07-17", "close": 123.99}, {"date": "2026-07-20", "close": 119.85}, {"date": "2026-07-21", "close": 123.54}, {"date": "2026-07-22", "close": 115.26}, {"date": "2026-07-23", "close": 118.24}, {"date": "2026-07-24", "close": 115.07}, {"date": "2026-07-27", "close": 113.5}, {"date": "2026-07-28", "close": 116.41}]

NDX_PRICES = [{"date": "2026-06-01", "close": 30513.86}, {"date": "2026-06-02", "close": 30660.6}, {"date": "2026-06-03", "close": 30571.24}, {"date": "2026-06-04", "close": 30407.81}, {"date": "2026-06-05", "close": 28957.6}, {"date": "2026-06-08", "close": 29414.26}, {"date": "2026-06-09", "close": 29084.5}, {"date": "2026-06-10", "close": 28508.03}, {"date": "2026-06-11", "close": 29446.18}, {"date": "2026-06-12", "close": 29635.95}, {"date": "2026-06-15", "close": 30543.92}, {"date": "2026-06-16", "close": 29968.13}, {"date": "2026-06-17", "close": 29670.95}, {"date": "2026-06-18", "close": 30406.19}, {"date": "2026-06-22", "close": 30347.08}, {"date": "2026-06-23", "close": 29347.27}, {"date": "2026-06-24", "close": 29220.06}, {"date": "2026-06-25", "close": 29440.32}, {"date": "2026-06-26", "close": 29118.24}, {"date": "2026-06-29", "close": 29774.75}, {"date": "2026-06-30", "close": 30276.35}, {"date": "2026-07-01", "close": 29809.13}, {"date": "2026-07-02", "close": 29329.21}, {"date": "2026-07-06", "close": 29697.87}, {"date": "2026-07-07", "close": 29173.02}, {"date": "2026-07-08", "close": 29252.56}, {"date": "2026-07-09", "close": 29727.1}, {"date": "2026-07-10", "close": 29825.11}, {"date": "2026-07-13", "close": 29264.1}, {"date": "2026-07-14", "close": 29586.29}, {"date": "2026-07-15", "close": 29502.6}, {"date": "2026-07-16", "close": 29025.77}, {"date": "2026-07-17", "close": 28592.66}, {"date": "2026-07-20", "close": 28604.23}, {"date": "2026-07-21", "close": 29155.18}, {"date": "2026-07-22", "close": 28998.1}, {"date": "2026-07-23", "close": 28454.81}, {"date": "2026-07-24", "close": 28128.34}, {"date": "2026-07-27", "close": 28039.21}, {"date": "2026-07-28", "close": 27763.13}]

# Curated from a live SEC EDGAR submissions pull (CIK 0001181412) on
# 2026-07-28, deduped by (form, filed date), with hand-written descriptions —
# SEC's own "primaryDocDescription" field is usually just the form code
# repeated (e.g. "8-K"), not a useful summary.
FILINGS = [
    {"form": "8-K", "filed": "2026-06-26", "description": "Senior notes offering — closing",
     "accession": "0001628280-26-045763", "primary_doc": "spcx-closing8xkjune2026.htm"},
    {"form": "8-K", "filed": "2026-06-23", "description": "Senior notes offering — pricing",
     "accession": "0001628280-26-044955", "primary_doc": "spcx-pricing8xk.htm"},
    {"form": "8-K", "filed": "2026-06-22", "description": "Senior notes offering — launch",
     "accession": "0001628280-26-044489", "primary_doc": "spcx8-kxlaunchseniornotes.htm"},
    {"form": "8-K", "filed": "2026-06-17", "description": "Officer/director appointment (Item 5.02)",
     "accession": "0001628280-26-043865", "primary_doc": "spaceexplorationtechnologi.htm"},
    {"form": "8-K", "filed": "2026-06-16", "description": "Material agreement / unregistered equity sale (Items 1.01, 3.02)",
     "accession": "0001628280-26-043411", "primary_doc": "spaceexplorationtechnologi.htm"},
    {"form": "8-K", "filed": "2026-06-15", "description": "IPO closing — governance conversion, charter/bylaw amendments (Items 3.02, 3.03, 5.02, 5.03)",
     "accession": "0001628280-26-043288", "primary_doc": "spaceexplorationtechnologi.htm"},
    {"form": "S-8", "filed": "2026-06-12", "description": "Employee stock plan registration",
     "accession": "0001628280-26-042832", "primary_doc": "spaceexplorationtechnologi.htm"},
    {"form": "424B4", "filed": "2026-06-12", "description": "Final IPO prospectus — offer price, share count, use of proceeds",
     "accession": "0001628280-26-042639", "primary_doc": "spaceexplorationtechnologi.htm"},
    {"form": "8-A12B", "filed": "2026-06-10", "description": "Nasdaq Global Select Market listing registration",
     "accession": "0001628280-26-042109", "primary_doc": "spaceexplorationtechnologi.htm"},
    {"form": "S-1/A", "filed": "2026-06-03", "description": "IPO registration amendment — pricing range update",
     "accession": "0001628280-26-040364", "primary_doc": "spaceexplorationtechnologib.htm"},
    {"form": "S-1/A", "filed": "2026-06-01", "description": "IPO registration amendment",
     "accession": "0001628280-26-039276", "primary_doc": "spaceexplorationtechnologi.htm"},
    {"form": "S-1", "filed": "2026-05-20", "description": "Initial IPO registration statement",
     "accession": "0001628280-26-036936", "primary_doc": "spaceexplorationtechnologi.htm"},
]
