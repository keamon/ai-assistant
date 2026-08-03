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

"""FastAPI endpoint tests via TestClient (offline: market data mocked, LLM stubbed)."""


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_reset(client):
    r = client.post("/api/reset")
    assert r.status_code == 200
    assert r.json()["reset"] is True


def test_briefing_has_public_company_watch(client):
    r = client.get("/api/briefing")
    assert r.status_code == 200
    body = r.json()
    assert body["narrative"] == "TEST NARRATIVE"
    watch = body["public_company_watch"]
    assert len(watch) == 3
    assert {w["ticker"] for w in watch} == {"WSM", "ETSY", "DAVE"}


def test_stock_endpoint(client):
    r = client.get("/api/stock/WSM")
    assert r.status_code == 200
    body = r.json()
    assert body["ticker"] == "WSM"
    assert body["source"] == "mock"
    assert body["quote"]["price"]


def test_sec_endpoint_public(client):
    r = client.get("/api/sec/etsy")
    assert r.status_code == 200
    body = r.json()
    assert body["ticker"] == "ETSY"
    assert body["filings"]


def test_sec_endpoint_form_filter(client):
    r = client.get("/api/sec/WSM", params={"form_type": "10-K"})
    assert r.status_code == 200
    body = r.json()
    assert all(f["form"] == "10-K" for f in body["filings"])


def test_sec_endpoint_private(client):
    r = client.get("/api/sec/glenbrook")
    assert r.status_code == 200
    body = r.json()
    assert body["public"] is False
    assert "no SEC filings" in body["message"]


def test_prep_endpoint_customer_enriched(client):
    r = client.get("/api/prep/cal_002")  # Williams-Sonoma
    assert r.status_code == 200
    body = r.json()
    assert body["is_customer_meeting"] is True
    assert body["stock_snapshot"]["ticker"] == "WSM"
    assert body["latest_filing"]["form"] in {"10-K", "10-Q", "8-K"}
    assert body["objective"] == "TEST OBJECTIVE"


def test_salesforce_renamed(client):
    r = client.get("/api/salesforce")
    assert r.status_code == 200
    names = {a["name"] for a in r.json()["accounts"]}
    assert names == {"Williams-Sonoma, Inc.", "Etsy, Inc.", "Dave Inc.", "Glenbrook Partners"}


def test_spacex_analytics_endpoint(client, monkeypatch):
    from server import main

    fake_payload = {
        "company": "SpaceX", "ticker": "SPCX", "cik": "0001181412",
        "index_name": "Nasdaq-100", "index_ticker": "^NDX",
        "ipo_date": "2026-06-12", "ipo_raise": "~$75B", "ipo_valuation": "~$1.75T",
        "inclusion_date": "2026-07-06", "timeline": [],
        "prices": {"spcx": {"source": "live", "prices": []}, "index": {"source": "live", "prices": []}},
        "metrics": {}, "insights": [], "filings": {"filings": []},
        "fred": {"series": {}, "yield_curve_10y2y": 0.0}, "bank_impact": [], "news": [],
    }
    monkeypatch.setattr(main.spacex_case_study, "get_dashboard_payload", lambda: fake_payload)
    monkeypatch.setattr(main.llm, "generate_spacex_narrative", lambda payload: "TEST SPACEX NARRATIVE")

    r = client.get("/api/spacex-analytics")
    assert r.status_code == 200
    body = r.json()
    assert body["ticker"] == "SPCX"
    assert body["narrative"] == "TEST SPACEX NARRATIVE"

    # Cached — a second call must not re-invoke the (expensive) payload builder.
    monkeypatch.setattr(
        main.spacex_case_study, "get_dashboard_payload",
        lambda: (_ for _ in ()).throw(AssertionError("should be cached")),
    )
    r2 = client.get("/api/spacex-analytics")
    assert r2.status_code == 200
    assert r2.json()["narrative"] == "TEST SPACEX NARRATIVE"


def test_spacex_analytics_endpoint_live_failure_returns_error(client, monkeypatch):
    from server import main

    def boom():
        raise RuntimeError("Yahoo Finance unreachable")

    monkeypatch.setattr(main.spacex_case_study, "get_dashboard_payload", boom)
    r = client.get("/api/spacex-analytics")
    assert r.status_code == 200
    body = r.json()
    assert "error" in body
    assert "unavailable" in body["error"].lower()
