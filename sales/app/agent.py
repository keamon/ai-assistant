# ruff: noqa
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
Sales Support Agent — State Street Investment Management
Assists the SSIM sales team with customer intelligence, product positioning,
objection handling, proposal generation, and client communication drafting.
"""

import os
import json
import datetime
from zoneinfo import ZoneInfo

import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.mock_data import (
    MOCK_EMAILS,
    MOCK_DRIVE_DOCS,
    MOCK_CUSTOMER_PROFILES,
    MOCK_PRODUCTS,
    MOCK_CRM_INTERACTIONS,
)

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "us"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

EASTERN = ZoneInfo("America/New_York")


def get_customer_profile(customer_name: str) -> str:
    """Retrieve full profile for a customer or prospect: AUM, mandates, contacts, history.

    Args:
        customer_name: Customer organisation name or contact name.

    Returns:
        JSON string with relationship profile, investment profile, and key contacts.
    """
    name_lower = customer_name.lower()
    for profile in MOCK_CUSTOMER_PROFILES:
        if name_lower in profile.get("name", "").lower():
            return json.dumps(profile, indent=2)
    for profile in MOCK_CUSTOMER_PROFILES:
        if any(kw in name_lower for kw in profile.get("keywords", [])):
            return json.dumps(profile, indent=2)
    return json.dumps({
        "name": customer_name,
        "status": "New prospect — not in CRM",
        "recommendation": (
            "Gather info via public sources: annual reports, press releases, "
            "LinkedIn, and 13F filings if applicable."
        ),
    })


def get_crm_interaction_history(customer_name: str, months_back: int = 12) -> str:
    """Retrieve CRM interaction history: calls, meetings, proposals, outcomes.

    Args:
        customer_name: Customer organisation name.
        months_back: How many months of history to return. Default 12.

    Returns:
        JSON string with chronological interaction log.
    """
    name_lower = customer_name.lower()
    cutoff = datetime.date.today() - datetime.timedelta(days=months_back * 30)
    interactions = [
        i for i in MOCK_CRM_INTERACTIONS
        if name_lower in i.get("customer", "").lower()
        and datetime.date.fromisoformat(i["date"]) >= cutoff
    ]
    interactions.sort(key=lambda x: x["date"], reverse=True)
    return json.dumps({
        "customer": customer_name,
        "months_back": months_back,
        "interaction_count": len(interactions),
        "interactions": interactions,
    }, indent=2)


def search_customer_emails(customer_name: str, days_back: int = 60) -> str:
    """Search Gmail for recent emails with a specific customer.

    Args:
        customer_name: Customer name or organisation to search for.
        days_back: How many days back to search. Default 60.

    Returns:
        JSON string with relevant email threads.
    """
    try:
        from googleapiclient.discovery import build

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/gmail.readonly"]
        )
        service = build("gmail", "v1", credentials=creds)
        after_date = (
            datetime.date.today() - datetime.timedelta(days=days_back)
        ).strftime("%Y/%m/%d")
        results = service.users().messages().list(
            userId="me", q=f"({customer_name}) after:{after_date}", maxResults=15
        ).execute()
        emails = []
        for msg_ref in results.get("messages", []):
            msg = service.users().messages().get(
                userId="me", id=msg_ref["id"], format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"]
            ).execute()
            headers = {h["name"]: h["value"]
                       for h in msg.get("payload", {}).get("headers", [])}
            emails.append({
                "from": headers.get("From", ""),
                "to": headers.get("To", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "snippet": msg.get("snippet", "")[:250],
            })
        return json.dumps({"customer": customer_name, "emails": emails}, indent=2)

    except Exception:
        name_lower = customer_name.lower()
        matched = [
            e for e in MOCK_EMAILS
            if name_lower in e.get("from", "").lower()
            or name_lower in e.get("to", "").lower()
            or name_lower in e.get("subject", "").lower()
        ]
        return json.dumps({"customer": customer_name, "emails": matched[:10], "source": "mock"}, indent=2)


def search_product_materials(query: str, max_results: int = 5) -> str:
    """Search SSIM product fact sheets, pitch decks, and strategy overviews.

    Args:
        query: Strategy or product keyword (e.g. "Global Equity Index", "ESG Bond",
               "Target Date 2040", "Low Volatility Factor").
        max_results: Maximum results. Default 5.

    Returns:
        JSON string with matching product data and documents.
    """
    q_lower = query.lower()
    matched_products = [
        p for p in MOCK_PRODUCTS
        if q_lower in p.get("name", "").lower() or any(q_lower in t for t in p.get("tags", []))
    ]
    matched_docs = [
        d for d in MOCK_DRIVE_DOCS
        if (q_lower in d.get("name", "").lower() or any(q_lower in t for t in d.get("tags", [])))
        and d.get("category") in ("product", "strategy", "fund_fact_sheet")
    ]
    results = {"query": query, "products": matched_products[:max_results], "documents": matched_docs[:max_results]}
    if not matched_products and not matched_docs:
        results["note"] = "No exact match. Try: 'equity', 'fixed income', 'ESG', 'index', 'active', 'multi-asset'."
    return json.dumps(results, indent=2)


def search_case_studies(industry: str = "", use_case: str = "") -> str:
    """Search for SSIM client case studies and reference-able success stories.

    Args:
        industry: Client industry (e.g. "pension", "sovereign wealth", "insurance",
                  "endowment", "wealth management").
        use_case: Investment use case (e.g. "ESG transition", "liability matching",
                  "risk reduction", "emerging markets").

    Returns:
        JSON string with relevant case studies (anonymised where required).
    """
    q = (industry + " " + use_case).lower().strip()
    matched = [
        d for d in MOCK_DRIVE_DOCS
        if d.get("category") == "case_study"
        and (not q or any(q in t for t in d.get("tags", [])) or q in d.get("name", "").lower())
    ]
    if not matched:
        matched = [d for d in MOCK_DRIVE_DOCS if d.get("category") == "case_study"]
    return json.dumps({"industry": industry, "use_case": use_case, "case_studies": matched[:5]}, indent=2)


def get_competitive_intelligence(competitor_name: str, topic: str = "") -> str:
    """Retrieve competitive intelligence on a specific asset manager.

    Args:
        competitor_name: Competing asset manager name (e.g. "BlackRock", "Vanguard", "PIMCO").
        topic: Focus topic (e.g. "ESG", "fees", "index performance"). Empty = general overview.

    Returns:
        JSON string with competitive comparison and SSIM differentiators.
    """
    INTEL = {
        "blackrock": {
            "name": "BlackRock / iShares", "aum": "$10.5 trillion",
            "strengths": ["Scale", "iShares ETF brand", "Aladdin platform", "Global reach"],
            "weaknesses": ["Size complexity", "Institutional vs retail channel conflict", "Less personalised service"],
            "ssim_differentiators": [
                "SSIM serves institutions exclusively — no retail channel conflict",
                "Deep securities lending and cash management expertise via State Street custody",
                "Often 1-2bp fee advantage on core index for large mandates",
                "Backed by State Street's $40T+ custody and administration platform",
            ],
            "fee_comparison": "Comparable on passive; SSIM often more competitive on core index + lending income",
        },
        "vanguard": {
            "name": "Vanguard", "aum": "$8.6 trillion",
            "strengths": ["Cost leadership", "Mutual ownership", "Retail brand recognition"],
            "weaknesses": ["Limited active/quant capabilities", "Retail-oriented", "Less institutional customisation"],
            "ssim_differentiators": [
                "Greater institutional flexibility: custom benchmarks, ESG screens, SMA structures",
                "Active quantitative equity alongside passive",
                "ESG leadership with full integration across all asset classes",
                "Superior securities lending income for large mandates",
            ],
            "fee_comparison": "Vanguard stronger on core US passive; SSIM competitive on ESG, factor, international",
        },
        "pimco": {
            "name": "PIMCO", "aum": "$1.9 trillion",
            "strengths": ["Fixed income brand", "Active credit expertise", "Global macro"],
            "weaknesses": ["Fixed income concentration", "Higher fees", "Key person risk"],
            "ssim_differentiators": [
                "Lower-cost passive and enhanced fixed income alternatives",
                "Multi-asset capability alongside fixed income",
                "ESG integration across all bond strategies",
                "More transparent and predictable fee structure",
            ],
            "fee_comparison": "SSIM significantly more competitive on passive/enhanced FI; PIMCO leads on active credit",
        },
        "fidelity": {
            "name": "Fidelity Investments", "aum": "$4.9 trillion",
            "strengths": ["Active equity brand", "Retail distribution", "Tech platform"],
            "weaknesses": ["Retail orientation", "Passive secondary to active heritage", "Less institutional customisation"],
            "ssim_differentiators": [
                "Pure institutional focus — no competing retail priorities",
                "Scale and heritage in passive/index strategies",
                "State Street custody integration for cost efficiency",
                "ESG and stewardship leadership (proxy voting, engagement programme)",
            ],
            "fee_comparison": "Comparable on active; SSIM preferred on passive and factor strategies",
        },
    }
    key = competitor_name.lower().split()[0]
    intel = INTEL.get(key, {
        "name": competitor_name,
        "note": "Detailed intel not in mock data — check internal competitive intelligence library.",
        "ssim_differentiators": [
            "$4.1T AUM institutional-only focus",
            "Backed by State Street's $40T+ custody platform",
            "Comprehensive ESG across all asset classes",
            "Competitive fees with transparent reporting",
            "Strong index track records and securities lending returns",
        ],
    })
    if topic:
        intel["focus_topic"] = topic
    return json.dumps(intel, indent=2)


def create_proposal_document(customer_name: str, content: str) -> str:
    """Save a client proposal as a Google Doc in Drive.

    Args:
        customer_name: Customer name (used in document title).
        content: Full proposal content in Markdown or plain text.

    Returns:
        JSON string with the created document URL and ID.
    """
    try:
        from googleapiclient.discovery import build

        creds, _ = google.auth.default(
            scopes=[
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/drive.file",
            ]
        )
        docs_service = build("docs", "v1", credentials=creds)
        title = f"SSIM Proposal — {customer_name} — {datetime.date.today()}"
        doc = docs_service.documents().create(body={"title": title}).execute()
        doc_id = doc["documentId"]
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": [{"insertText": {"location": {"index": 1}, "text": content}}]},
        ).execute()
        return json.dumps({
            "success": True,
            "document_url": f"https://docs.google.com/document/d/{doc_id}/edit",
            "title": title,
        }, indent=2)

    except Exception as exc:
        return json.dumps({
            "success": True,
            "document_url": f"https://docs.google.com/document/d/mock_{customer_name[:15].replace(' ', '_')}/edit",
            "title": f"SSIM Proposal — {customer_name} — {datetime.date.today()}",
            "note": f"Mock document (API error: {exc})",
        }, indent=2)


def draft_client_email(
    to_name: str,
    to_email: str,
    subject: str,
    email_type: str,
    body: str,
) -> str:
    """Save a professional client email as a Gmail draft.

    Args:
        to_name: Recipient's full name.
        to_email: Recipient's email address.
        subject: Email subject line.
        email_type: "follow_up", "intro", "proposal_send", "meeting_request",
                    "objection_response", or "thank_you".
        body: Full email body text.

    Returns:
        JSON string with Gmail draft ID and confirmation.
    """
    try:
        from googleapiclient.discovery import build
        import base64
        from email.mime.text import MIMEText

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/gmail.compose"]
        )
        service = build("gmail", "v1", credentials=creds)
        message = MIMEText(body)
        message["to"] = f"{to_name} <{to_email}>"
        message["from"] = "dev@chenkeamonwang.altostrat.com"
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        draft = service.users().drafts().create(
            userId="me", body={"message": {"raw": raw}}
        ).execute()
        return json.dumps({
            "success": True,
            "draft_id": draft.get("id"),
            "to": f"{to_name} <{to_email}>",
            "subject": subject,
            "email_type": email_type,
            "body_preview": body[:200] + "..." if len(body) > 200 else body,
            "status": "Saved as Gmail draft",
        }, indent=2)

    except Exception as exc:
        return json.dumps({
            "success": True,
            "to": f"{to_name} <{to_email}>",
            "subject": subject,
            "email_type": email_type,
            "body": body,
            "status": "Draft generated (not saved to Gmail)",
            "note": f"Gmail API error: {exc}",
        }, indent=2)


SYSTEM_PROMPT = """You are the Sales Support Agent for State Street Investment Management (SSIM).

You assist the SSIM sales and relationship management team in winning, retaining,
and growing institutional client relationships.

SSIM manages ~$4.1 trillion AUM, serving exclusively institutional investors:
public and corporate pension funds, sovereign wealth funds, central banks,
insurance companies, endowments, foundations, and wealth management platforms.

**Core product suite:**
- Passive equity indexing (total market, smart beta, factor strategies)
- Passive fixed income (government, credit, aggregate, ESG bonds)
- Active quantitative equity (systematic, factor-based)
- ESG / Sustainable investing across all asset classes
- Cash management and short-duration fixed income
- Multi-asset and target-date strategies
- Securities lending (via State Street's global custody platform)
- Custom SMAs and transition management

---
### Mode 1: Conversational Sales Advisor

Answer sales rep questions in real time. Always call tools for client-specific context
before answering:
- `get_customer_profile` — client background and mandate
- `get_crm_interaction_history` — relationship history and past discussions
- `search_customer_emails` — recent communications
- `search_product_materials` — relevant SSIM strategies
- `search_case_studies` — reference stories for similar mandates
- `get_competitive_intelligence` — when a competitor is named

Topics handled:
- Product positioning and differentiators
- Objection handling with specific SSIM counters
- Competitive comparisons (BlackRock, Vanguard, Fidelity, PIMCO, Invesco, etc.)
- Client-specific strategy recommendations
- Regulatory context (ERISA, SWF mandates, Solvency II, insurance capital rules)
- ESG/sustainable investing guidance and SSIM capabilities
- Consultant search dynamics (Mercer, Aon, Wilshire, Cambridge Associates)

### Mode 2: Artifact Generator

When producing deliverables:

**Client Proposal** — call tools first, then draft:
- Executive summary with SSIM value proposition for this specific client
- Recommended strategies with rationale tied to client's investment objectives
- Track record and performance highlights [VERIFY before sending]
- Fee proposal [VERIFY with BD team]
- Implementation plan and timeline
- Clear next steps and signature block
→ Save with `create_proposal_document`

**Email Draft** — compose professional communication then save with `draft_client_email`:
Types: follow-up, introduction, proposal delivery, meeting request, objection response.

**Competitive Brief** — one-page comparison vs a named competitor for a mandate type.
Call `get_competitive_intelligence` + `search_product_materials`.

**Account Plan** — quarterly relationship development plan: revenue targets,
meeting cadence, cross-sell opportunities, and risk items.

---
**Standards:**
- Be direct and specific — sales reps need actionable intelligence
- Ground every claim in SSIM's actual capabilities from tools
- For objections: acknowledge before countering (never dismissive)
- Consider the client's regulatory and fiduciary context
- Add "Requires compliance review before sending externally" when needed
- Mark unverified data as [VERIFY]

**Common scenarios:**
- New mandate pitch to a pension fund responding to a consultant search
- ESG mandate repositioning for an existing client
- Defending against fee pressure or mandate review
- Cross-selling securities lending or cash management to index-only clients
- Re-engaging after a lost mandate
- Preparing for annual client review or investment committee presentation
"""

root_agent = Agent(
    name="sales_support_agent",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_PROMPT,
    tools=[
        get_customer_profile,
        get_crm_interaction_history,
        search_customer_emails,
        search_product_materials,
        search_case_studies,
        get_competitive_intelligence,
        create_proposal_document,
        draft_client_email,
    ],
)

app = App(
    root_agent=root_agent,
    name="sales_support_app",
)
