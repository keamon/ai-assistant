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

"""Seed / mock-data sanity: customers are the renamed public companies and no
stale fictional names remain."""

import json

from server import mock_data, seed

OLD_NAMES = ["Northwind", "Atlas Marketplace", "Brightline"]
OLD_DOMAINS = ["@northwind", "@atlas", "@brightline"]


def test_no_stale_customer_names_in_seed():
    blob = json.dumps(seed.build_seed(), default=str)
    for name in OLD_NAMES:
        assert name not in blob, f"stale name {name!r} still in seed"
    for dom in OLD_DOMAINS:
        assert dom not in blob, f"stale domain {dom!r} still in seed"


def test_public_profiles_have_ticker_and_cik():
    public = [p for p in mock_data.MOCK_CUSTOMER_PROFILES if p.get("public")]
    assert len(public) == 3
    for p in public:
        assert p["ticker"] in mock_data.TICKER_CIK
        assert p["cik"]
        assert p["ticker"] in mock_data.MOCK_SEC_FILINGS
        assert p["ticker"] in mock_data.MOCK_YAHOO_FINANCE


def test_glenbrook_is_private():
    g = next(p for p in mock_data.MOCK_CUSTOMER_PROFILES if "Glenbrook" in p.get("name", ""))
    assert g.get("public") is False
    assert not g.get("ticker")


def test_salesforce_accounts_renamed():
    sf = seed.build_seed()["salesforce"]
    names = {a["name"] for a in sf["accounts"]}
    assert names == {"Williams-Sonoma, Inc.", "Etsy, Inc.", "Dave Inc.", "Glenbrook Partners"}
