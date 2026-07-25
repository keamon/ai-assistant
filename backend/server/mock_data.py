"""
Mock data for Daily Briefing Agent — State Street Investment Management.
Simulates Gmail, Google Calendar, and payments/banking market context responses.
"""

import datetime

_TODAY = datetime.date.today().isoformat()
_TOMORROW = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

MOCK_CALENDAR_EVENTS = [
    {
        "id": "cal_001",
        "date": _TODAY,
        "title": "Morning Ops Review — Payments Network Team",
        "start": f"{_TODAY}T08:30:00-04:00",
        "end": f"{_TODAY}T09:00:00-04:00",
        "location": "Conference Room 4A, Boston",
        "description": "Daily review of overnight transaction volumes, authorization-rate anomalies, and network incidents.",
        "attendees": [
            "sarah.chen@statestreet.com",
            "james.okonkwo@statestreet.com",
            "dev@chenkeamonwang.altostrat.com",
        ],
        "meeting_type": "internal",
        "video_link": "https://meet.google.com/abc-defg-hij",
    },
    {
        "id": "cal_002",
        "date": _TODAY,
        "title": "Northwind Retail Group — Q3 2026 Processing Agreement Review",
        "start": f"{_TODAY}T10:00:00-04:00",
        "end": f"{_TODAY}T11:30:00-04:00",
        "location": "Zoom",
        "description": "Quarterly review of Northwind Retail Group's ~$12B annual TPV processing relationship. Agenda: Q3 performance, interchange/fee discussion, chargeback trends ahead of the renewal.",
        "attendees": [
            "marcus.webb@northwindretail.com",
            "jennifer.wu@northwindretail.com",
            "dev@chenkeamonwang.altostrat.com",
            "sarah.chen@statestreet.com",
            "robert.kim@statestreet.com",
        ],
        "meeting_type": "customer",
        "video_link": "https://zoom.us/j/12345678",
        "is_customer_meeting": True,
    },
    {
        "id": "cal_003",
        "date": _TODAY,
        "title": "BSA/AML & Compliance Working Group",
        "start": f"{_TODAY}T13:00:00-04:00",
        "end": f"{_TODAY}T14:00:00-04:00",
        "location": "Teams",
        "description": "Monthly working group: review of fraud model tuning, BSA/AML alert queue, PCI-DSS quarterly scan status, and OFAC sanctions-screening false-positive rate.",
        "attendees": [
            "anna.petrov@statestreet.com",
            "dev@chenkeamonwang.altostrat.com",
            "mark.johnson@statestreet.com",
            "lisa.huang@statestreet.com",
        ],
        "meeting_type": "internal",
        "video_link": "https://teams.microsoft.com/l/meetup-join/mock",
    },
    {
        "id": "cal_004",
        "date": _TODAY,
        "title": "RFP Finalist Pitch — Atlas Marketplace (Payments + BaaS)",
        "start": f"{_TODAY}T15:00:00-04:00",
        "end": f"{_TODAY}T16:30:00-04:00",
        "location": "Toronto Office / Video",
        "description": "Pitch for a combined payments processing + embedded-lending (BaaS) deal, ~$3B projected annual TPV. Atlas Marketplace is evaluating SSIM against Stripe and Adyen. Focus on network reliability and fraud/chargeback performance.",
        "attendees": [
            "divya.nair@atlasmarketplace.com",
            "ryan.cole@atlasmarketplace.com",
            "dev@chenkeamonwang.altostrat.com",
            "peter.walsh@statestreet.com",
        ],
        "meeting_type": "customer",
        "video_link": "https://zoom.us/j/87654321",
        "is_customer_meeting": True,
    },
    {
        "id": "cal_005",
        "date": _TODAY,
        "title": "Risk Committee — Weekly Standup",
        "start": f"{_TODAY}T16:30:00-04:00",
        "end": f"{_TODAY}T17:00:00-04:00",
        "location": "Internal",
        "description": "Weekly risk metrics review: fraud loss rate, chargeback rate, transaction authorization rate, and network uptime/SLA summary across all payment rails.",
        "attendees": [
            "dev@chenkeamonwang.altostrat.com",
            "james.okonkwo@statestreet.com",
            "anna.petrov@statestreet.com",
        ],
        "meeting_type": "internal",
        "video_link": "",
    },
    {
        "id": "cal_006",
        "date": _TOMORROW,
        "title": "Brightline Financial — BaaS Program Scoping Call",
        "start": f"{_TOMORROW}T09:00:00-04:00",
        "end": f"{_TOMORROW}T10:00:00-04:00",
        "location": "Video",
        "description": "Initial scoping call with Brightline Financial to expand their Banking-as-a-Service program (FBO accounts, card issuing, embedded lending). Currently ~$500M in program deposits.",
        "attendees": [
            "priya.desai@brightlinefinancial.com",
            "dev@chenkeamonwang.altostrat.com",
        ],
        "meeting_type": "customer",
        "is_customer_meeting": True,
        "video_link": "https://meet.google.com/xyz-abc-def",
    },
]

MOCK_EMAILS = [
    {
        "id": "email_001",
        "from": "marcus.webb@northwindretail.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "RE: Q3 2026 Renewal Terms — Action Required Before Meeting",
        "date": f"{_TODAY}T07:15:00-04:00",
        "snippet": "Could you please confirm the Q3 interchange/fee analysis will be ready before our 10am call today? Also, our CFO has asked about the fee schedule for the processing-agreement renewal — please bring updated numbers.",
        "labels": ["UNREAD", "IMPORTANT"],
        "needs_action": True,
        "starred": True,
    },
    {
        "id": "email_002",
        "from": "risk-alerts@statestreet.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "ALERT: Fraud Spike Detected — CNP Transactions Up 3.2x Overnight",
        "date": f"{_TODAY}T06:00:00-04:00",
        "snippet": "Automated alert: overnight card-not-present fraud attempts up 3.2x baseline across the network. 12 merchant accounts flagged for review. Response required by 3pm ET.",
        "labels": ["UNREAD"],
        "needs_action": True,
        "starred": False,
    },
    {
        "id": "email_003",
        "from": "ryan.cole@atlasmarketplace.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Agenda Confirmation — SSIM Payments + BaaS Pitch Today",
        "date": f"{_TODAY}T08:00:00-04:00",
        "snippet": "Confirming today's 3pm call. Our CFO will join unexpectedly. Please ensure you have slides on: (1) network uptime/SLA track record, (2) fraud/chargeback performance vs industry benchmark, (3) embedded-lending (BaaS) program structure, (4) fee structure for ~$3B projected TPV.",
        "labels": ["UNREAD"],
        "needs_action": True,
        "starred": False,
    },
    {
        "id": "email_004",
        "from": "compliance@statestreet.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Deadline: PCI-DSS Quarterly Scan Review — Response Due by EOD Friday",
        "date": f"{_TODAY}T09:30:00-04:00",
        "snippet": "Please review and approve the updated PCI-DSS quarterly scan results attached. Remediation sign-off must be completed before the compliance window closes. Deadline: Friday COB.",
        "labels": ["UNREAD"],
        "needs_action": True,
        "starred": False,
    },
    {
        "id": "email_005",
        "from": "bloomberg-data@bloomberg.net",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Morning Market Intelligence — May 16, 2026",
        "date": f"{_TODAY}T05:30:00-04:00",
        "snippet": "Fed funds rate held at 5.25%-5.50%. 10Y UST at 4.21%. USD index +0.3% — watch cross-border FX impact on remittance corridors. Visa/Mastercard network volumes tracking +6% YoY. Fed minutes today at 2pm ET.",
        "labels": ["INBOX"],
        "needs_action": False,
        "starred": False,
    },
    {
        "id": "email_006",
        "from": "anna.petrov@statestreet.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Compliance Working Group — Pre-read attached",
        "date": f"{_TODAY}T08:45:00-04:00",
        "snippet": "Sending pre-read for today's 1pm compliance working group. Key items: BSA/AML alert-queue tuning proposal, PCI-DSS quarterly scan status, and new OFAC sanctions-screening vendor evaluation summary.",
        "labels": ["INBOX"],
        "needs_action": False,
        "starred": True,
    },
    {
        "id": "email_007",
        "from": "peter.walsh@statestreet.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Atlas Marketplace CFO joining today — Update strategy",
        "date": f"{_TODAY}T09:00:00-04:00",
        "snippet": "Just got word that Atlas Marketplace CFO Elena Marsh will join the 3pm call. She's focused on network reliability and fraud economics. Adjust opening to lead with our risk/fraud management framework before pricing.",
        "labels": ["UNREAD", "STARRED"],
        "needs_action": True,
        "starred": True,
    },
    {
        "id": "email_008",
        "from": "priya.desai@brightlinefinancial.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "RE: Brightline Financial BaaS Program — Pre-call Questions",
        "date": f"{_TODAY}T03:00:00-04:00",
        "snippet": "Thank you for setting up tomorrow's call. Before we connect, could you send us: (1) your BSA/AML and KYC oversight framework, (2) FBO account reconciliation process, (3) card issuing program compliance summary, (4) OCC/FDIC exam readiness for the banking division.",
        "labels": ["UNREAD"],
        "needs_action": True,
        "starred": False,
    },
    {
        "id": "email_009",
        "from": "james.okonkwo@statestreet.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Q3 Interchange & Fee Analysis Ready",
        "date": f"{_TODAY}T07:45:00-04:00",
        "snippet": "Q3 renewal fee analysis is ready for Northwind Retail Group. Blended interchange cost: 1.8% of TPV, in line with card-mix assumptions. Main driver: increase in premium rewards card mix. Document shared in Drive.",
        "labels": ["INBOX"],
        "needs_action": False,
        "starred": False,
    },
    {
        "id": "email_010",
        "from": "ryan.cole@atlasmarketplace.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Atlas Marketplace RFP — Shortlist Notification",
        "date": (
            datetime.date.today() - datetime.timedelta(days=2)
        ).isoformat() + "T14:00:00-04:00",
        "snippet": "We are pleased to inform you that SSIM has been shortlisted for the combined payments + embedded-lending (BaaS) deal. You are one of 3 providers invited to present, alongside Stripe and Adyen. Today's call is your final presentation.",
        "labels": ["INBOX", "STARRED"],
        "needs_action": False,
        "starred": True,
    },
]

MOCK_MARKET_CONTEXT = {
    "date": _TODAY,
    "market_snapshot": {
        "fed_funds_rate": "5.25%-5.50% (held)",
        "us_10y_yield": "4.21%",
        "usd_index": "+0.3%",
        "card_network_auth_rate": "98.7%",
        "ach_same_day_volume": "+5.4% WoW",
    },
    "ssim_payments_banking_snapshot": {
        "as_of": f"yesterday ({(datetime.date.today() - datetime.timedelta(days=1)).isoformat()})",
        "total_tpv": "$11.2 billion",
        "card_tpv": "$7.9 billion",
        "ach_tpv": "$2.3 billion",
        "realtime_tpv": "$0.6 billion",
        "cross_border_tpv": "$0.4 billion",
        "commercial_deposits": "$85 billion",
        "commercial_loans": "$40 billion",
        "tpv_change_dod": "+3.4% vs. the prior day (+$370M on strong weekday e-commerce volume)",
    },
    "key_events_today": [
        "Visa network scheduled maintenance window 2:00-4:00 AM ET — completed, no incidents reported",
        "Fed funds rate held at 5.25%-5.50% — no immediate NIM impact expected",
        "New FedNow participant onboarding completed — real-time payments reach expanded",
        "PCI-DSS quarterly scan deadline: Friday COB",
    ],
    "risk_alerts": [
        {
            "type": "fraud_spike",
            "severity": "high",
            "message": "Overnight card-not-present fraud attempts up 3.2x baseline; 12 merchant accounts flagged for review.",
            "action_required": "Coordinate with fraud ops on rule tuning and merchant notifications",
        },
        {
            "type": "contract_renewal",
            "severity": "medium",
            "message": "Northwind Retail Group processing-agreement renewal due Q3 2026 — interchange/fee negotiation in progress",
            "action_required": "Confirm fee proposal with relationship team before today's meeting",
        },
        {
            "type": "authorization_rate_drop",
            "severity": "medium",
            "message": "Card network authorization rate dipped to 98.1% overnight (target: 98.5%+) on issuer-side timeouts",
            "action_required": "Compliance/risk working group review today at 1pm",
        },
    ],
    "regulatory_reminders": [
        "BSA/AML SAR filing deadline: June 30, 2026",
        "OCC exam prep materials due",
        "Reg E dispute resolution deadline: current",
        "PCI-DSS quarterly scan: Q2 due July 31",
    ],
    "treasury_sweep": {
        "sweep_participation_rate": "67%",
        "revenue_ytd": "$142M",
        "top_merchant_category": "Retail & E-commerce — led by Northwind Retail Group settlement float",
        "alert": "Quarter-end reconciliation pending on 3 merchant sweep positions — treasury desk notified",
    },
}

# ════════════════════════════════════════════════════════════════════════════
# Folded-in Meeting Prep data (Drive documents + customer/CRM profiles).
# Copied from the meeting_prep agent so Daily Briefing can produce a full prep
# brief for any meeting (the expandable per-meeting view). Covers SSIM's three
# active payments/banking relationships: Northwind Retail Group (existing
# processing client), Atlas Marketplace (RFP finalist), and Brightline
# Financial (Banking-as-a-Service partner).
# ════════════════════════════════════════════════════════════════════════════

MOCK_DRIVE_DOCS = [
    {
        "id": "doc_001",
        "name": "Northwind Retail Group — SSIM Payments Processing Agreement — Q3 2026 Report",
        "mimeType": "application/vnd.google-apps.document",
        "webViewLink": "https://docs.google.com/document/d/mock_northwind_q3/edit",
        "modifiedTime": f"{_TODAY}T07:00:00Z",
        "category": "client_report",
        "tags": ["northwind", "retail", "payments", "q3", "2026", "performance", "interchange"],
        "content": """Northwind Retail Group — Payments Processing Agreement — Q3 2026 Report

Program Overview:
- Annual TPV: $12.1 billion (card + ACH, as of June 30, 2026)
- Payment mix: 68% card, 32% ACH
- Relationship inception: March 2018

Q3 2026 Performance:
- Transaction authorization rate: 98.9%
- Chargeback rate: 0.06% of TPV (industry benchmark: 0.08%)
- Blended interchange cost: 1.8% of TPV
- Network uptime/SLA: 99.98%

Program Economics:
- Merchant Reserve & Treasury Sweep Program participation: +8 bps (zero losses since program inception)
- Settlement processing efficiency: +4 bps
- Dispute resolution time: avg 6.2 days (target: <7 days)
- Fee schedule: -3 bps (net, current tier)

Compliance & Risk Status:
- PCI-DSS Level 1 compliance: current
- OFAC sanctions screening: no flags this quarter
- Durbin Amendment debit-routing rule implementation: complete for Q3 2026

Processing-Agreement Renewal:
- Current contract expires: December 31, 2026
- Proposed fee: 1.2% blended interchange pass-through on first $10B TPV, 0.8% above $10B
- Competitor fee range (Stripe, Adyen, First Data): 1.0%-1.5%
""",
    },
    {
        "id": "doc_002",
        "name": "SSIM Payments + BaaS — Platform Overview & Performance Track Record",
        "mimeType": "application/vnd.google-apps.presentation",
        "webViewLink": "https://docs.google.com/presentation/d/mock_payments_baas/edit",
        "modifiedTime": (datetime.date.today() - datetime.timedelta(days=10)).isoformat() + "T12:00:00Z",
        "category": "strategy",
        "tags": ["payments", "baas", "embedded lending", "track record", "atlas"],
        "content": """SSIM Payments + Banking-as-a-Service — Platform Overview

Platform Overview:
- Total TPV processed: $4.13 trillion annually (as of May 2026)
- Platform founded: January 2008; BaaS division launched 2019
- Benchmark: industry authorization-rate and network-uptime standards
- Target performance: 99%+ network uptime, sub-100ms authorization latency

5-Year Performance Track Record (as of March 31, 2026):
- Average transaction authorization rate: 98.8% (industry benchmark: 97.6%)
- Chargeback rate: 0.05% of TPV (industry benchmark: 0.09%)
- Fraud loss rate: 4.2 bps of TPV
- Network uptime/SLA: 99.97% (2022 peak-volume stress period: 99.91%)
- Dispute resolution time: 6.5 days average (within 5-8 day target range)

Fraud & Risk Model Performance (as of May 2026):
- Card-not-present fraud detection lift: +0.22 vs baseline model
- False-positive decline improvement: +0.31
- Velocity-rule effectiveness: +0.18
- Device-fingerprinting coverage: +0.15
- Chargeback dispute win rate: -0.05 vs prior model

Fee Schedule (proposed for ~$3B projected annual TPV, combined payments + BaaS):
- Processing fee: 20 bps blended
- Embedded-lending program fee: none (available on request)
- Comparison: industry average for combined payments + BaaS ~25-35 bps
""",
    },
    {
        "id": "doc_003",
        "name": "SSIM BSA/AML & Compliance Policy — 2026",
        "mimeType": "application/vnd.google-apps.document",
        "webViewLink": "https://docs.google.com/document/d/mock_bsa_aml_policy/edit",
        "modifiedTime": (datetime.date.today() - datetime.timedelta(days=45)).isoformat() + "T09:00:00Z",
        "category": "policy",
        "tags": ["bsa aml", "compliance", "policy", "kyc", "ofac", "brightline", "northwind"],
        "content": """SSIM BSA/AML & Compliance Policy — 2026

1. BSA/AML & Sanctions Screening Framework
SSIM applies BSA/AML controls across all payments and banking-division programs through:
- Proprietary transaction-monitoring model (informed by FinCEN guidance, OFAC lists, network alerts)
- Real-time OFAC sanctions screening on all cross-border transactions
- Enhanced due diligence for BaaS partner programs (KYC/KYB oversight)
- SAR filing and case-management program

2. Sanctions Screening Record (2025)
- Total transactions screened: 4.1 billion
- Alerts requiring manual review: 0.4% (industry avg: 0.6%)
- SARs filed: 312
- Key oversight theme: partner-program KYC refresh cadence, high-risk merchant categories

3. Regulatory Oversight (as of Jan 2026)
- OCC-supervised programs: 12 (includes Brightline Financial FBO program)
- FDIC-insured deposit programs: 34
- State money-transmitter licenses held: 48 states + DC

4. Program Risk Profile (Flagship BaaS Program, Brightline Financial)
- Program deposits: $500 million (FBO accounts)
- KYC refresh completion rate: 97%
- Chargeback/dispute rate vs benchmark: -39% (below industry average)
- OCC exam readiness: on track for next scheduled exam

5. Exclusion / Restricted-Activity List
- OFAC-sanctioned entities: full transaction block
- High-risk merchant categories (>25% of program volume): enhanced monitoring
- Cannabis/adult/gambling (unless program-specific licensing): no exclusion
- Sanctioned jurisdictions: full exclusion
""",
    },
    {
        "id": "doc_004",
        "name": "Atlas Marketplace — RFP Response Draft — Payments + BaaS",
        "mimeType": "application/vnd.google-apps.document",
        "webViewLink": "https://docs.google.com/document/d/mock_atlas_rfp/edit",
        "modifiedTime": (datetime.date.today() - datetime.timedelta(days=21)).isoformat() + "T15:00:00Z",
        "category": "rfp",
        "tags": ["atlas", "rfp", "payments", "baas", "embedded lending"],
        "content": """SSIM RFP Response — Atlas Marketplace — Combined Payments + Embedded Lending (BaaS)

Section 1: Firm Overview
State Street Investment Management (SSIM) is a digital payments company processing $4.1
trillion in total payment volume (TPV) annually, with a commercial banking division holding
$85B in deposits and $40B in loans outstanding. We serve merchants and platforms across
card, ACH, real-time payments, and cross-border rails.

Section 2: Platform
Our combined Payments + BaaS offering has processed consistent, reliable volume since our
platform's founding, employing a systematic multi-rail approach (card, ACH, RTP/FedNow,
cross-border) with a proprietary fraud-detection and underwriting overlay for embedded lending.

Section 3: Risk Management
- Independent risk & compliance team reports to CRO (separate from product team)
- Real-time fraud monitoring and authorization-rate/exposure limits
- 2022 peak-volume stress period: 99.91% network uptime vs industry 99.80%

Section 4: Team
- Payments Product: 12 PMs, average experience 18 years
- Engineering/Risk Research: 24 engineers and risk analysts (8 with fraud-ML PhDs)
- Compliance: 8 compliance officers
- No departures from senior team in 5 years

Section 5: Fee Proposal
~$3B projected annual TPV: 20 bps blended processing fee
""",
    },
    {
        "id": "doc_005",
        "name": "SSIM Capabilities Deck — Brightline Financial BaaS Pre-read",
        "mimeType": "application/vnd.google-apps.presentation",
        "webViewLink": "https://docs.google.com/presentation/d/mock_brightline_deck/edit",
        "modifiedTime": (datetime.date.today() - datetime.timedelta(days=3)).isoformat() + "T11:00:00Z",
        "category": "pitch_deck",
        "tags": ["brightline", "baas", "banking", "compliance", "fintech partner"],
        "content": "SSIM Capabilities Deck prepared for Brightline Financial. Covers: firm overview, BaaS program structure (FBO accounts, card issuing, embedded lending), BSA/AML & KYC oversight framework, compliance track record, team structure.",
    },
]

MOCK_CUSTOMER_PROFILES = [
    {
        "name": "Northwind Retail Group",
        "full_name": "Northwind Retail Group, Inc.",
        "keywords": ["northwind", "retail group"],
        "type": "Omnichannel Retailer",
        "country": "United States",
        "total_aum": "$18 billion (annual revenue)",
        "ssim_relationship": {
            "status": "Active Client",
            "since": "March 2018",
            "ssim_aum": "$12.1 billion (annual TPV — card + ACH)",
            "strategies": ["Card Processing (Visa/Mastercard)", "ACH Settlement"],
            "primary_contact": "Marcus Webb (VP of Payments)",
            "secondary_contact": "Jennifer Wu (Treasury Manager)",
            "relationship_manager": "Sarah Chen (SSIM)",
            "mandate_expiry": "December 31, 2026",
        },
        "investment_profile": {
            "return_objective": "Sub-2% blended interchange cost with 99%+ authorization rate",
            "esg_requirements": "PCI-DSS Level 1 required, OFAC sanctions screening, quarterly compliance attestation",
            "key_concerns": ["Interchange/fee reduction", "Chargeback rate management", "Cross-border expansion"],
            "upcoming_decisions": "Processing-agreement renewal Q3 2026, potential cross-border expansion of $500M",
        },
        "recent_activity": "Q3 renewal review today. CFO asking about fees. Interest in expanding cross-border volume.",
    },
    {
        "name": "Atlas Marketplace",
        "full_name": "Atlas Marketplace, Inc.",
        "keywords": ["atlas", "marketplace"],
        "type": "E-Commerce Marketplace",
        "country": "United States",
        "total_aum": "$1.2 billion (annual revenue)",
        "ssim_relationship": {
            "status": "Prospect — RFP Finalist",
            "since": "N/A — new relationship",
            "ssim_aum": "$0 (prospect)",
            "strategies": ["Shortlisted for combined Payments + Embedded Lending (BaaS), ~$3B projected annual TPV"],
            "primary_contact": "Divya Nair (VP of Payments)",
            "secondary_contact": "Ryan Cole (Head of Finance)",
            "cio": "Elena Marsh (CFO)",
            "relationship_manager": "Peter Walsh (SSIM)",
        },
        "investment_profile": {
            "return_objective": "Sub-100ms authorization latency, 99.9%+ network uptime",
            "esg_requirements": "SOC 2 Type II required, PCI-DSS Level 1, state money-transmitter licensing coverage",
            "key_concerns": [
                "Competing against Stripe and Adyen",
                "Fraud/chargeback performance under high growth volume",
                "Embedded-lending underwriting transparency",
                "Fee competitiveness",
            ],
            "upcoming_decisions": "Final provider selection in 30 days. ~$3B projected annual TPV deal.",
        },
        "recent_activity": "Final pitch today. CFO joining unexpectedly. Must lead with risk/fraud management story.",
    },
    {
        "name": "Brightline Financial",
        "full_name": "Brightline Financial, Inc.",
        "keywords": ["brightline", "financial"],
        "type": "Fintech / Banking-as-a-Service Partner",
        "country": "United States",
        "total_aum": "$500 million (program deposits)",
        "ssim_relationship": {
            "status": "Prospect — Initial Scoping",
            "since": "N/A — new",
            "ssim_aum": "$0",
            "strategies": ["Exploring expanded BaaS program: FBO accounts, card issuing, embedded lending"],
            "primary_contact": "Priya Desai (Head of Compliance)",
            "relationship_manager": "Dev (SSIM — initial contact)",
        },
        "investment_profile": {
            "return_objective": "Reliable FBO reconciliation and compliant program growth",
            "esg_requirements": "Heavy BSA/AML and KYC oversight — OCC/FDIC exam readiness required",
            "key_concerns": [
                "BSA/AML and KYC oversight framework",
                "FBO account reconciliation accuracy",
                "Card issuing program compliance",
                "OCC/FDIC exam readiness for the banking division",
            ],
            "upcoming_decisions": "Initial scoping call tomorrow — no decision timeline set yet",
        },
        "recent_activity": "Pre-call questions received: BSA/AML framework, FBO reconciliation process, card issuing compliance, OCC/FDIC exam readiness.",
    },
]

# ════════════════════════════════════════════════════════════════════════════
# Room inventory + seat directory (compact copy of the meeting_room agent's
# data) so Daily Briefing can auto-assign a room when scheduling a meeting.
# ════════════════════════════════════════════════════════════════════════════

MOCK_ROOMS = [
    {"id": "room_bos1_4a", "name": "Conference Room 4A", "building": "One Congress", "floor": 4, "capacity": 8, "equipment": ["display", "video_conf", "whiteboard"], "av": True},
    {"id": "room_bos1_4b", "name": "Huddle 4B", "building": "One Congress", "floor": 4, "capacity": 4, "equipment": ["display"], "av": False},
    {"id": "room_bos1_12", "name": "Fenway Boardroom", "building": "One Congress", "floor": 12, "capacity": 20, "equipment": ["display", "video_conf", "whiteboard", "speakerphone"], "av": True},
    {"id": "room_bos1_7", "name": "Beacon Room", "building": "One Congress", "floor": 7, "capacity": 12, "equipment": ["display", "video_conf", "whiteboard"], "av": True},
    {"id": "room_bos2_3", "name": "Harbor View", "building": "Channel Center", "floor": 3, "capacity": 10, "equipment": ["display", "video_conf"], "av": True},
    {"id": "room_bos2_6", "name": "Seaport Suite", "building": "Channel Center", "floor": 6, "capacity": 6, "equipment": ["display", "video_conf", "whiteboard"], "av": True},
    {"id": "room_tor_18", "name": "CN Tower Room", "building": "Toronto", "floor": 18, "capacity": 14, "equipment": ["display", "video_conf", "whiteboard"], "av": True},
]

MOCK_EMPLOYEE_LOCATIONS = [
    {"email": "dev@chenkeamonwang.altostrat.com", "name": "Dev (You)", "building": "One Congress", "floor": 7, "seat": "7-114"},
    {"email": "sarah.chen@statestreet.com", "name": "Sarah Chen", "building": "One Congress", "floor": 7, "seat": "7-102"},
    {"email": "james.okonkwo@statestreet.com", "name": "James Okonkwo", "building": "One Congress", "floor": 4, "seat": "4-210"},
    {"email": "anna.petrov@statestreet.com", "name": "Anna Petrov", "building": "One Congress", "floor": 12, "seat": "12-045"},
    {"email": "mark.johnson@statestreet.com", "name": "Mark Johnson", "building": "Channel Center", "floor": 3, "seat": "3-330"},
    {"email": "lisa.huang@statestreet.com", "name": "Lisa Huang", "building": "Channel Center", "floor": 6, "seat": "6-118"},
    {"email": "robert.kim@statestreet.com", "name": "Robert Kim", "building": "One Congress", "floor": 7, "seat": "7-131"},
    {"email": "peter.walsh@statestreet.com", "name": "Peter Walsh", "building": "Toronto", "floor": 18, "seat": "18-204"},
]

MOCK_ROOM_BOOKINGS = [
    {"id": "bk_001", "room_id": "room_bos1_4a", "event_title": "Morning Ops Review", "date": _TODAY, "start": f"{_TODAY}T08:30:00-04:00", "end": f"{_TODAY}T09:00:00-04:00", "organizer": "james.okonkwo@statestreet.com"},
    {"id": "bk_002", "room_id": "room_bos1_12", "event_title": "Client Off-site", "date": _TODAY, "start": f"{_TODAY}T10:00:00-04:00", "end": f"{_TODAY}T12:00:00-04:00", "organizer": "peter.walsh@statestreet.com"},
    {"id": "bk_003", "room_id": "room_bos1_7", "event_title": "Risk Committee — Weekly Standup", "date": _TODAY, "start": f"{_TODAY}T16:30:00-04:00", "end": f"{_TODAY}T17:00:00-04:00", "organizer": "james.okonkwo@statestreet.com"},
]

# ════════════════════════════════════════════════════════════════════════════
# Suggested meetings to schedule — derived from today's emails/signals that
# imply a meeting is needed but none is yet on the calendar.
# ════════════════════════════════════════════════════════════════════════════

_IN_2_DAYS = (datetime.date.today() + datetime.timedelta(days=2)).isoformat()
_IN_3_DAYS = (datetime.date.today() + datetime.timedelta(days=3)).isoformat()

MOCK_MEETING_SUGGESTIONS = [
    {
        "id": "sug_001",
        "title": "Northwind Cross-Border Expansion — Scoping Call",
        "rationale": "Marcus Webb (Northwind Retail Group) raised interest in expanding $500M of cross-border volume; no meeting is on the calendar yet.",
        "suggested_attendees": [
            "marcus.webb@northwindretail.com",
            "sarah.chen@statestreet.com",
            "dev@chenkeamonwang.altostrat.com",
        ],
        "suggested_duration_min": 45,
        "priority": "high",
        "suggested_date": _IN_2_DAYS,
        "source_email_id": "email_001",
        "meeting_type": "customer",
    },
    {
        "id": "sug_002",
        "title": "Atlas Marketplace Pitch Debrief (internal)",
        "rationale": "After today's Atlas Marketplace final pitch, an internal debrief will capture follow-ups before the 30-day selection window closes.",
        "suggested_attendees": [
            "peter.walsh@statestreet.com",
            "dev@chenkeamonwang.altostrat.com",
        ],
        "suggested_duration_min": 30,
        "priority": "medium",
        "suggested_date": _TODAY,
        "source_email_id": "email_007",
        "meeting_type": "internal",
    },
    {
        "id": "sug_003",
        "title": "PCI-DSS Quarterly Scan — Compliance Sign-off Session",
        "rationale": "Compliance flagged the PCI-DSS quarterly scan review is due Friday COB; a working session is needed to review scan remediation results.",
        "suggested_attendees": [
            "compliance@statestreet.com",
            "dev@chenkeamonwang.altostrat.com",
        ],
        "suggested_duration_min": 60,
        "priority": "high",
        "suggested_date": _IN_2_DAYS,
        "source_email_id": "email_004",
        "meeting_type": "internal",
    },
    {
        "id": "sug_004",
        "title": "Fraud Spike Response — Network Ops Coordination",
        "rationale": "Overnight fraud spike (3.2x baseline in CNP transactions) needs a rule-tuning sync with network ops before end of week.",
        "suggested_attendees": [
            "james.okonkwo@statestreet.com",
            "dev@chenkeamonwang.altostrat.com",
        ],
        "suggested_duration_min": 30,
        "priority": "medium",
        "suggested_date": _IN_3_DAYS,
        "source_email_id": "email_002",
        "meeting_type": "internal",
    },
]
