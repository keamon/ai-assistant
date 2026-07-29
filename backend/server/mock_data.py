"""
Mock data for Daily Briefing Agent — FinTechCo.
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
            "sarah.chen@fintechco.com",
            "james.okonkwo@fintechco.com",
        ],
        "meeting_type": "internal",
        "video_link": "https://meet.google.com/abc-defg-hij",
    },
    {
        "id": "cal_002",
        "date": _TODAY,
        "title": "Williams-Sonoma — Q3 2026 Processing Agreement Review",
        "start": f"{_TODAY}T10:00:00-04:00",
        "end": f"{_TODAY}T11:30:00-04:00",
        "location": "Zoom",
        "description": "Quarterly review of Williams-Sonoma's ~$12B annual TPV processing relationship. Agenda: Q3 performance, interchange/fee discussion, chargeback trends ahead of the renewal.",
        "attendees": [
            "marcus.webb@williams-sonoma.com",
            "jennifer.wu@williams-sonoma.com",
            "sarah.chen@fintechco.com",
            "robert.kim@fintechco.com",
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
            "anna.petrov@fintechco.com",
            "mark.johnson@fintechco.com",
            "lisa.huang@fintechco.com",
        ],
        "meeting_type": "internal",
        "video_link": "https://teams.microsoft.com/l/meetup-join/mock",
    },
    {
        "id": "cal_004",
        "date": _TODAY,
        "title": "RFP Finalist Pitch — Etsy (Payments + BaaS)",
        "start": f"{_TODAY}T15:00:00-04:00",
        "end": f"{_TODAY}T16:30:00-04:00",
        "location": "Toronto Office / Video",
        "description": "Pitch for a combined payments processing + embedded-lending (BaaS) deal, ~$3B projected annual TPV. Etsy is evaluating FinTechCo against Stripe and Adyen. Focus on network reliability and fraud/chargeback performance.",
        "attendees": [
            "divya.nair@etsy.com",
            "ryan.cole@etsy.com",
            "peter.walsh@fintechco.com",
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
            "james.okonkwo@fintechco.com",
            "anna.petrov@fintechco.com",
        ],
        "meeting_type": "internal",
        "video_link": "",
    },
    {
        "id": "cal_006",
        "date": _TOMORROW,
        "title": "Dave — BaaS Program Scoping Call",
        "start": f"{_TOMORROW}T09:00:00-04:00",
        "end": f"{_TOMORROW}T10:00:00-04:00",
        "location": "Video",
        "description": "Initial scoping call with Dave to expand their Banking-as-a-Service program (FBO accounts, card issuing, embedded lending). Currently ~$500M in program deposits.",
        "attendees": [
            "priya.desai@dave.com",
        ],
        "meeting_type": "customer",
        "is_customer_meeting": True,
        "video_link": "https://meet.google.com/xyz-abc-def",
    },
]

MOCK_EMAILS = [
    {
        "id": "email_001",
        "from": "marcus.webb@williams-sonoma.com",
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
        "from": "risk-alerts@fintechco.com",
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
        "from": "ryan.cole@etsy.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Agenda Confirmation — FinTechCo Payments + BaaS Pitch Today",
        "date": f"{_TODAY}T08:00:00-04:00",
        "snippet": "Confirming today's 3pm call. Our CFO will join unexpectedly. Please ensure you have slides on: (1) network uptime/SLA track record, (2) fraud/chargeback performance vs industry benchmark, (3) embedded-lending (BaaS) program structure, (4) fee structure for ~$3B projected TPV.",
        "labels": ["UNREAD"],
        "needs_action": True,
        "starred": False,
    },
    {
        "id": "email_004",
        "from": "compliance@fintechco.com",
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
        "from": "anna.petrov@fintechco.com",
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
        "from": "peter.walsh@fintechco.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Etsy CFO joining today — Update strategy",
        "date": f"{_TODAY}T09:00:00-04:00",
        "snippet": "Just got word that Etsy CFO Elena Marsh will join the 3pm call. She's focused on network reliability and fraud economics. Adjust opening to lead with our risk/fraud management framework before pricing.",
        "labels": ["UNREAD", "STARRED"],
        "needs_action": True,
        "starred": True,
    },
    {
        "id": "email_008",
        "from": "priya.desai@dave.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "RE: Dave BaaS Program — Pre-call Questions",
        "date": f"{_TODAY}T03:00:00-04:00",
        "snippet": "Thank you for setting up tomorrow's call. Before we connect, could you send us: (1) your BSA/AML and KYC oversight framework, (2) FBO account reconciliation process, (3) card issuing program compliance summary, (4) OCC/FDIC exam readiness for the banking division.",
        "labels": ["UNREAD"],
        "needs_action": True,
        "starred": False,
    },
    {
        "id": "email_009",
        "from": "james.okonkwo@fintechco.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Q3 Interchange & Fee Analysis Ready",
        "date": f"{_TODAY}T07:45:00-04:00",
        "snippet": "Q3 renewal fee analysis is ready for Williams-Sonoma. Blended interchange cost: 1.8% of TPV, in line with card-mix assumptions. Main driver: increase in premium rewards card mix. Document shared in Drive.",
        "labels": ["INBOX"],
        "needs_action": False,
        "starred": False,
    },
    {
        "id": "email_010",
        "from": "ryan.cole@etsy.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Etsy RFP — Shortlist Notification",
        "date": (
            datetime.date.today() - datetime.timedelta(days=2)
        ).isoformat() + "T14:00:00-04:00",
        "snippet": "We are pleased to inform you that FinTechCo has been shortlisted for the combined payments + embedded-lending (BaaS) deal. You are one of 3 providers invited to present, alongside Stripe and Adyen. Today's call is your final presentation.",
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
            "message": "Williams-Sonoma processing-agreement renewal due Q3 2026 — interchange/fee negotiation in progress",
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
        "top_merchant_category": "Retail & E-commerce — led by Williams-Sonoma settlement float",
        "alert": "Quarter-end reconciliation pending on 3 merchant sweep positions — treasury desk notified",
    },
}

# ════════════════════════════════════════════════════════════════════════════
# Folded-in Meeting Prep data (Drive documents + customer/CRM profiles).
# Copied from the meeting_prep agent so Daily Briefing can produce a full prep
# brief for any meeting (the expandable per-meeting view). Covers FinTechCo's three
# active payments/banking relationships: Williams-Sonoma (existing
# processing client), Etsy (RFP finalist), and Dave
# Financial (Banking-as-a-Service partner).
# ════════════════════════════════════════════════════════════════════════════

MOCK_DRIVE_DOCS = [
    {
        "id": "doc_001",
        "name": "Williams-Sonoma — FinTechCo Payments Processing Agreement — Q3 2026 Report",
        "mimeType": "application/vnd.google-apps.document",
        "webViewLink": "https://docs.google.com/document/d/mock_williams-sonoma_q3/edit",
        "modifiedTime": f"{_TODAY}T07:00:00Z",
        "category": "client_report",
        "tags": ["williams-sonoma", "retail", "payments", "q3", "2026", "performance", "interchange"],
        "content": """Williams-Sonoma — Payments Processing Agreement — Q3 2026 Report

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
        "name": "FinTechCo Payments + BaaS — Platform Overview & Performance Track Record",
        "mimeType": "application/vnd.google-apps.presentation",
        "webViewLink": "https://docs.google.com/presentation/d/mock_payments_baas/edit",
        "modifiedTime": (datetime.date.today() - datetime.timedelta(days=10)).isoformat() + "T12:00:00Z",
        "category": "strategy",
        "tags": ["payments", "baas", "embedded lending", "track record", "etsy"],
        "content": """FinTechCo Payments + Banking-as-a-Service — Platform Overview

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
        "name": "FinTechCo BSA/AML & Compliance Policy — 2026",
        "mimeType": "application/vnd.google-apps.document",
        "webViewLink": "https://docs.google.com/document/d/mock_bsa_aml_policy/edit",
        "modifiedTime": (datetime.date.today() - datetime.timedelta(days=45)).isoformat() + "T09:00:00Z",
        "category": "policy",
        "tags": ["bsa aml", "compliance", "policy", "kyc", "ofac", "dave", "williams-sonoma"],
        "content": """FinTechCo BSA/AML & Compliance Policy — 2026

1. BSA/AML & Sanctions Screening Framework
FinTechCo applies BSA/AML controls across all payments and banking-division programs through:
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
- OCC-supervised programs: 12 (includes Dave FBO program)
- FDIC-insured deposit programs: 34
- State money-transmitter licenses held: 48 states + DC

4. Program Risk Profile (Flagship BaaS Program, Dave)
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
        "name": "Etsy — RFP Response Draft — Payments + BaaS",
        "mimeType": "application/vnd.google-apps.document",
        "webViewLink": "https://docs.google.com/document/d/mock_etsy_rfp/edit",
        "modifiedTime": (datetime.date.today() - datetime.timedelta(days=21)).isoformat() + "T15:00:00Z",
        "category": "rfp",
        "tags": ["etsy", "rfp", "payments", "baas", "embedded lending"],
        "content": """FinTechCo RFP Response — Etsy — Combined Payments + Embedded Lending (BaaS)

Section 1: Firm Overview
FinTechCo is a digital payments company processing $4.1
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
        "name": "FinTechCo Capabilities Deck — Dave BaaS Pre-read",
        "mimeType": "application/vnd.google-apps.presentation",
        "webViewLink": "https://docs.google.com/presentation/d/mock_dave_deck/edit",
        "modifiedTime": (datetime.date.today() - datetime.timedelta(days=3)).isoformat() + "T11:00:00Z",
        "category": "pitch_deck",
        "tags": ["dave", "baas", "banking", "compliance", "fintech partner"],
        "content": "FinTechCo Capabilities Deck prepared for Dave. Covers: firm overview, BaaS program structure (FBO accounts, card issuing, embedded lending), BSA/AML & KYC oversight framework, compliance track record, team structure.",
    },
]

MOCK_CUSTOMER_PROFILES = [
    {
        "name": "Williams-Sonoma",
        "full_name": "Williams-Sonoma, Inc.",
        "keywords": ["williams-sonoma", "williams sonoma", "wsm"],
        "ticker": "WSM",
        "exchange": "NYSE",
        "cik": "0000719955",
        "public": True,
        "type": "Omnichannel Retailer",
        "country": "United States",
        "total_aum": "$7.9 billion (annual revenue)",
        "ssim_relationship": {
            "status": "Active Client",
            "since": "March 2018",
            "ssim_aum": "$12.1 billion (annual TPV — card + ACH)",
            "strategies": ["Card Processing (Visa/Mastercard)", "ACH Settlement"],
            "primary_contact": "Marcus Webb (VP of Payments)",
            "secondary_contact": "Jennifer Wu (Treasury Manager)",
            "relationship_manager": "Sarah Chen (FinTechCo)",
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
        "name": "Etsy",
        "full_name": "Etsy, Inc.",
        "keywords": ["etsy"],
        "ticker": "ETSY",
        "exchange": "Nasdaq",
        "cik": "0001370637",
        "public": True,
        "type": "E-Commerce Marketplace",
        "country": "United States",
        "total_aum": "$2.8 billion (annual revenue)",
        "ssim_relationship": {
            "status": "Prospect — RFP Finalist",
            "since": "N/A — new relationship",
            "ssim_aum": "$0 (prospect)",
            "strategies": ["Shortlisted for combined Payments + Embedded Lending (BaaS), ~$3B projected annual TPV"],
            "primary_contact": "Divya Nair (VP of Payments)",
            "secondary_contact": "Ryan Cole (Head of Finance)",
            "cio": "Elena Marsh (CFO)",
            "relationship_manager": "Peter Walsh (FinTechCo)",
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
        "name": "Dave",
        "full_name": "Dave Inc.",
        "keywords": ["dave"],
        "ticker": "DAVE",
        "exchange": "Nasdaq",
        "cik": "0001841408",
        "public": True,
        "type": "Fintech / Banking-as-a-Service Partner",
        "country": "United States",
        "total_aum": "$500 million (program deposits)",
        "ssim_relationship": {
            "status": "Prospect — Initial Scoping",
            "since": "N/A — new",
            "ssim_aum": "$0",
            "strategies": ["Exploring expanded BaaS program: FBO accounts, card issuing, embedded lending"],
            "primary_contact": "Priya Desai (Head of Compliance)",
            "relationship_manager": "Dev (FinTechCo — initial contact)",
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
    {
        # Privately held — no ticker. Exercised so the SEC/market tools correctly
        # report "private company, no public filings" rather than erroring.
        "name": "Glenbrook Partners",
        "full_name": "Glenbrook Partners LLC",
        "keywords": ["glenbrook", "partners"],
        "public": False,
        "type": "Payments Advisory Firm (privately held)",
        "country": "United States",
        "total_aum": "N/A (private advisory firm)",
        "ssim_relationship": {
            "status": "Consultant / Advisor",
            "since": "2021",
            "ssim_aum": "$0 (advisory relationship)",
            "strategies": ["Payments strategy & benchmarking advisory"],
            "primary_contact": "Peter Walsh (FinTechCo sponsor)",
            "relationship_manager": "Peter Walsh (FinTechCo)",
        },
        "investment_profile": {
            "return_objective": "N/A — advisory engagement",
            "esg_requirements": "Standard NDA / confidentiality",
            "key_concerns": ["Independent benchmarking of interchange economics"],
            "upcoming_decisions": "None on file",
        },
        "recent_activity": "Engaged for independent benchmarking of the Williams-Sonoma renewal economics.",
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
    {"email": "sarah.chen@fintechco.com", "name": "Sarah Chen", "building": "One Congress", "floor": 7, "seat": "7-102"},
    {"email": "james.okonkwo@fintechco.com", "name": "James Okonkwo", "building": "One Congress", "floor": 4, "seat": "4-210"},
    {"email": "anna.petrov@fintechco.com", "name": "Anna Petrov", "building": "One Congress", "floor": 12, "seat": "12-045"},
    {"email": "mark.johnson@fintechco.com", "name": "Mark Johnson", "building": "Channel Center", "floor": 3, "seat": "3-330"},
    {"email": "lisa.huang@fintechco.com", "name": "Lisa Huang", "building": "Channel Center", "floor": 6, "seat": "6-118"},
    {"email": "robert.kim@fintechco.com", "name": "Robert Kim", "building": "One Congress", "floor": 7, "seat": "7-131"},
    {"email": "peter.walsh@fintechco.com", "name": "Peter Walsh", "building": "Toronto", "floor": 18, "seat": "18-204"},
]

MOCK_ROOM_BOOKINGS = [
    {"id": "bk_001", "room_id": "room_bos1_4a", "event_title": "Morning Ops Review", "date": _TODAY, "start": f"{_TODAY}T08:30:00-04:00", "end": f"{_TODAY}T09:00:00-04:00", "organizer": "james.okonkwo@fintechco.com"},
    {"id": "bk_002", "room_id": "room_bos1_12", "event_title": "Client Off-site", "date": _TODAY, "start": f"{_TODAY}T10:00:00-04:00", "end": f"{_TODAY}T12:00:00-04:00", "organizer": "peter.walsh@fintechco.com"},
    {"id": "bk_003", "room_id": "room_bos1_7", "event_title": "Risk Committee — Weekly Standup", "date": _TODAY, "start": f"{_TODAY}T16:30:00-04:00", "end": f"{_TODAY}T17:00:00-04:00", "organizer": "james.okonkwo@fintechco.com"},
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
        "title": "Williams-Sonoma Cross-Border Expansion — Scoping Call",
        "rationale": "Marcus Webb (Williams-Sonoma) raised interest in expanding $500M of cross-border volume; no meeting is on the calendar yet.",
        "suggested_attendees": [
            "marcus.webb@williams-sonoma.com",
            "sarah.chen@fintechco.com",
        ],
        "suggested_duration_min": 45,
        "priority": "high",
        "suggested_date": _IN_2_DAYS,
        "source_email_id": "email_001",
        "meeting_type": "customer",
    },
    {
        "id": "sug_002",
        "title": "Etsy Pitch Debrief (internal)",
        "rationale": "After today's Etsy final pitch, an internal debrief will capture follow-ups before the 30-day selection window closes.",
        "suggested_attendees": [
            "peter.walsh@fintechco.com",
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
            "compliance@fintechco.com",
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
            "james.okonkwo@fintechco.com",
        ],
        "suggested_duration_min": 30,
        "priority": "medium",
        "suggested_date": _IN_3_DAYS,
        "source_email_id": "email_002",
        "meeting_type": "internal",
    },
]

# ════════════════════════════════════════════════════════════════════════════
# Public-company market intelligence — SEC EDGAR + Yahoo Finance.
#
# FinTechCo's payments/banking customers are modelled as real mid-cap public
# companies so their filings and quotes are genuinely useful context for the
# daily briefing and meeting prep. The live tools (`server.market_data`) fetch
# the real APIs; the structures below are the offline fallback returned (tagged
# ``"source": "mock"``) whenever the network is unavailable or a request fails.
#
# CIKs verified against https://www.sec.gov/files/company_tickers.json.
# Accession numbers / document URLs below are real recent filings (as of the
# 2026 build) so the fallback links resolve on sec.gov.
# ════════════════════════════════════════════════════════════════════════════

TICKER_CIK = {
    "WSM": "0000719955",   # Williams-Sonoma, Inc. (NYSE)
    "ETSY": "0001370637",  # Etsy, Inc. (Nasdaq)
    "DAVE": "0001841408",  # Dave Inc. (Nasdaq)
}

MOCK_SEC_FILINGS = {
    "WSM": {
        "company": "WILLIAMS-SONOMA INC",
        "ticker": "WSM",
        "cik": "0000719955",
        "filings": [
            {"form": "8-K", "filed": "2026-06-22", "period": "2026-06-18",
             "accession": "0000719955-26-000164", "primary_doc": "wsm-20260618.htm",
             "url": "https://www.sec.gov/Archives/edgar/data/719955/000071995526000164/wsm-20260618.htm",
             "summary": "Q1 FY2026 results & management commentary — comparable brand revenue and merchandise-margin update."},
            {"form": "10-Q", "filed": "2026-05-22", "period": "2026-05-03",
             "accession": "0000719955-26-000131", "primary_doc": "wsm-20260503.htm",
             "url": "https://www.sec.gov/Archives/edgar/data/719955/000071995526000131/wsm-20260503.htm",
             "summary": "Q1 FY2026 (quarter ended May 3, 2026) — net revenues, e-commerce mix, and card-based payment volumes."},
            {"form": "10-K", "filed": "2026-03-26", "period": "2026-02-01",
             "accession": "0000719955-26-000059", "primary_doc": "wsm-20260201.htm",
             "url": "https://www.sec.gov/Archives/edgar/data/719955/000071995526000059/wsm-20260201.htm",
             "summary": "FY2025 annual report (year ended Feb 1, 2026) — omnichannel revenue, DTC mix, payment-processing costs."},
        ],
    },
    "ETSY": {
        "company": "Etsy Inc",
        "ticker": "ETSY",
        "cik": "0001370637",
        "filings": [
            {"form": "8-K", "filed": "2026-07-16", "period": "2026-07-12",
             "accession": "0001370637-26-000066", "primary_doc": "etsy-20260712.htm",
             "url": "https://www.sec.gov/Archives/edgar/data/1370637/000137063726000066/etsy-20260712.htm",
             "summary": "Q2 2026 earnings release — GMS (gross merchandise sales), take rate, and Etsy Payments adoption."},
            {"form": "10-Q", "filed": "2026-04-29", "period": "2026-03-31",
             "accession": "0001370637-26-000044", "primary_doc": "etsy-20260331.htm",
             "url": "https://www.sec.gov/Archives/edgar/data/1370637/000137063726000044/etsy-20260331.htm",
             "summary": "Q1 2026 (quarter ended Mar 31, 2026) — GMS, Etsy Payments processing volume, marketplace revenue."},
            {"form": "10-K", "filed": "2026-02-19", "period": "2025-12-31",
             "accession": "0001370637-26-000019", "primary_doc": "etsy-20251231.htm",
             "url": "https://www.sec.gov/Archives/edgar/data/1370637/000137063726000019/etsy-20251231.htm",
             "summary": "FY2025 annual report — GMS, Payments penetration, and payment-processing / chargeback risk factors."},
        ],
    },
    "DAVE": {
        "company": "Dave Inc.",
        "ticker": "DAVE",
        "cik": "0001841408",
        "filings": [
            {"form": "8-K", "filed": "2026-06-02", "period": "2026-06-02",
             "accession": "0001193125-26-253774", "primary_doc": "dave-20260602.htm",
             "url": "https://www.sec.gov/Archives/edgar/data/1841408/000119312526253774/dave-20260602.htm",
             "summary": "Corporate update — member growth, ExtraCash originations, and sponsor-bank program metrics."},
            {"form": "10-Q", "filed": "2026-05-05", "period": "2026-03-31",
             "accession": "0001193125-26-206446", "primary_doc": "dave-20260331.htm",
             "url": "https://www.sec.gov/Archives/edgar/data/1841408/000119312526206446/dave-20260331.htm",
             "summary": "Q1 2026 (quarter ended Mar 31, 2026) — transaction/interchange revenue and sponsor-bank (BaaS) deposits."},
            {"form": "10-K", "filed": "2026-03-02", "period": "2025-12-31",
             "accession": "0001193125-26-085370", "primary_doc": "dave-20251231.htm",
             "url": "https://www.sec.gov/Archives/edgar/data/1841408/000119312526085370/dave-20251231.htm",
             "summary": "FY2025 annual report — interchange & transaction revenue, sponsor-bank relationship, BSA/AML risk factors."},
        ],
    },
}

MOCK_YAHOO_FINANCE = {
    "WSM": {
        "company": "Williams-Sonoma, Inc.",
        "exchange": "NYSE",
        "currency": "USD",
        "quote": {
            "price": 226.74, "change": 8.14, "change_pct": 3.72, "prev_close": 218.60,
            "day_low": 219.05, "day_high": 228.40, "week52_low": 165.51, "week52_high": 244.65,
            "volume": 2150000, "market_cap": 26700000000, "pe_ratio": 25.4,
        },
        "next_earnings_date": "2026-08-26",
        "news": [
            {"headline": "Williams-Sonoma tops Q1 estimates as furnishings demand stabilizes",
             "source": "MarketWatch", "date": "2026-06-22", "url": "https://finance.yahoo.com/quote/WSM/news"},
            {"headline": "Retailer's e-commerce mix holds above 65% of revenue",
             "source": "Barron's", "date": "2026-06-18", "url": "https://finance.yahoo.com/quote/WSM/news"},
            {"headline": "Board authorizes additional share buyback",
             "source": "Bloomberg", "date": "2026-06-10", "url": "https://finance.yahoo.com/quote/WSM/news"},
        ],
    },
    "ETSY": {
        "company": "Etsy, Inc.",
        "exchange": "Nasdaq",
        "currency": "USD",
        "quote": {
            "price": 62.40, "change": 1.55, "change_pct": 2.55, "prev_close": 60.85,
            "day_low": 60.60, "day_high": 63.10, "week52_low": 40.15, "week52_high": 75.30,
            "volume": 3900000, "market_cap": 6600000000, "pe_ratio": 24.8,
        },
        "next_earnings_date": "2026-07-30",
        "news": [
            {"headline": "Etsy Q2 preview: GMS growth and take-rate expansion in focus",
             "source": "Reuters", "date": "2026-07-15", "url": "https://finance.yahoo.com/quote/ETSY/news"},
            {"headline": "Etsy Payments now processes the vast majority of marketplace volume",
             "source": "TechCrunch", "date": "2026-07-08", "url": "https://finance.yahoo.com/quote/ETSY/news"},
            {"headline": "Analysts weigh marketplace competition ahead of earnings",
             "source": "Bloomberg", "date": "2026-07-02", "url": "https://finance.yahoo.com/quote/ETSY/news"},
        ],
    },
    "DAVE": {
        "company": "Dave Inc.",
        "exchange": "Nasdaq",
        "currency": "USD",
        "quote": {
            "price": 205.30, "change": 5.90, "change_pct": 2.96, "prev_close": 199.40,
            "day_low": 197.80, "day_high": 208.10, "week52_low": 44.60, "week52_high": 262.00,
            "volume": 520000, "market_cap": 2800000000, "pe_ratio": 21.5,
        },
        "next_earnings_date": "2026-08-04",
        "news": [
            {"headline": "Dave posts record ExtraCash originations, raises guidance",
             "source": "CNBC", "date": "2026-06-02", "url": "https://finance.yahoo.com/quote/DAVE/news"},
            {"headline": "Consumer fintech leans on sponsor-bank model for deposits",
             "source": "American Banker", "date": "2026-05-28", "url": "https://finance.yahoo.com/quote/DAVE/news"},
            {"headline": "Dave shares extend rally on improving credit metrics",
             "source": "Bloomberg", "date": "2026-05-20", "url": "https://finance.yahoo.com/quote/DAVE/news"},
        ],
    },
}
