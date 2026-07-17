"""
Mock data for Daily Briefing Agent — State Street Investment Management.
Simulates Gmail, Google Calendar, and market context responses.
"""

import datetime

_TODAY = datetime.date.today().isoformat()
_TOMORROW = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

MOCK_CALENDAR_EVENTS = [
    {
        "id": "cal_001",
        "date": _TODAY,
        "title": "Morning Portfolio Review — Global Equity Index Team",
        "start": f"{_TODAY}T08:30:00-04:00",
        "end": f"{_TODAY}T09:00:00-04:00",
        "location": "Conference Room 4A, Boston",
        "description": "Daily review of overnight NAV movements, index replication errors, and corporate actions.",
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
        "title": "CalPERS — Q2 2026 Investment Review",
        "start": f"{_TODAY}T10:00:00-04:00",
        "end": f"{_TODAY}T11:30:00-04:00",
        "location": "Zoom",
        "description": "Quarterly review of CalPERS' $8.2B passive equity mandate. Agenda: Q2 performance, ESG screening update, fee discussion for upcoming renewal.",
        "attendees": [
            "michael.torres@calpers.ca.gov",
            "jennifer.wu@calpers.ca.gov",
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
        "title": "ESG Integration Working Group",
        "start": f"{_TODAY}T13:00:00-04:00",
        "end": f"{_TODAY}T14:00:00-04:00",
        "location": "Teams",
        "description": "Monthly working group: review of proxy voting decisions, climate data vendors, SFDR Article 8/9 classification review.",
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
        "title": "New Mandate Pitch — Ontario Teachers' Pension Plan",
        "start": f"{_TODAY}T15:00:00-04:00",
        "end": f"{_TODAY}T16:30:00-04:00",
        "location": "Toronto Office / Video",
        "description": "Pitch for $2B Active Quantitative Equity mandate. OTPP is evaluating 4 managers. Focus on our systematic approach and factor exposures.",
        "attendees": [
            "david.morrison@otpp.com",
            "francesca.lim@otpp.com",
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
        "description": "Weekly risk metrics review: tracking error, factor exposures, liquidity, VaR summary across all strategies.",
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
        "title": "Singapore GIC — ESG Mandate Scoping Call",
        "start": f"{_TOMORROW}T09:00:00-04:00",
        "end": f"{_TOMORROW}T10:00:00-04:00",
        "location": "Video",
        "description": "Initial scoping for potential $5B ESG Global Equity mandate. GIC is exploring options for their new sustainable allocation.",
        "attendees": [
            "wei.chen@gic.com.sg",
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
        "from": "michael.torres@calpers.ca.gov",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "RE: Q2 2026 Performance Data — Action Required Before Meeting",
        "date": f"{_TODAY}T07:15:00-04:00",
        "snippet": "Could you please confirm the Q2 attribution analysis will be ready before our 10am call today? Also, CFO has asked about the fee schedule for the mandate renewal — please bring updated numbers.",
        "labels": ["UNREAD", "IMPORTANT"],
        "needs_action": True,
        "starred": True,
    },
    {
        "id": "email_002",
        "from": "risk-alerts@statestreet.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "ALERT: MSCI World Index Rebalance — 47 Constituent Changes Effective June 2",
        "date": f"{_TODAY}T06:00:00-04:00",
        "snippet": "Automated alert: MSCI World June 2026 rebalance confirmed. 47 additions, 31 deletions. Net flow impact estimated at $2.1B across all passive mandates. Review required by 3pm ET.",
        "labels": ["UNREAD"],
        "needs_action": True,
        "starred": False,
    },
    {
        "id": "email_003",
        "from": "francesca.lim@otpp.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Agenda Confirmation — SSIM Active Quant Pitch Today",
        "date": f"{_TODAY}T08:00:00-04:00",
        "snippet": "Confirming today's 3pm call. Our CIO will join unexpectedly. Please ensure you have slides on: (1) 5-year live track record, (2) factor exposures vs benchmark, (3) drawdown during 2022 selloff, (4) fee structure for $2B mandate.",
        "labels": ["UNREAD"],
        "needs_action": True,
        "starred": False,
    },
    {
        "id": "email_004",
        "from": "compliance@statestreet.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Deadline: SEC Marketing Rule Review — Response Due by EOD Friday",
        "date": f"{_TODAY}T09:30:00-04:00",
        "snippet": "Please review and approve the updated composite performance presentations attached. The SEC Marketing Rule compliance review must be completed before any external distribution. Deadline: Friday COB.",
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
        "snippet": "Global equities: S&P 500 futures +0.4%. MSCI EM -0.8% on USD strength. Fed minutes today at 2pm ET. 10Y UST at 4.21%. Oil -1.2%. NVDA earnings after close.",
        "labels": ["INBOX"],
        "needs_action": False,
        "starred": False,
    },
    {
        "id": "email_006",
        "from": "anna.petrov@statestreet.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "ESG Working Group — Pre-read attached",
        "date": f"{_TODAY}T08:45:00-04:00",
        "snippet": "Sending pre-read for today's 1pm ESG working group. Key items: SFDR reclassification proposal for 3 funds, ISS proxy policy update, and new climate data vendor evaluation summary.",
        "labels": ["INBOX"],
        "needs_action": False,
        "starred": True,
    },
    {
        "id": "email_007",
        "from": "peter.walsh@statestreet.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "OTPP CIO joining today — Update strategy",
        "date": f"{_TODAY}T09:00:00-04:00",
        "snippet": "Just got word that OTPP CIO Priya Mehta will join the 3pm call. She's focused on governance and drawdown risk. Adjust opening to lead with our risk management framework before performance.",
        "labels": ["UNREAD", "STARRED"],
        "needs_action": True,
        "starred": True,
    },
    {
        "id": "email_008",
        "from": "wei.chen@gic.com.sg",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "RE: Singapore GIC ESG Mandate — Pre-call Questions",
        "date": f"{_TODAY}T03:00:00-04:00",
        "snippet": "Thank you for setting up tomorrow's call. Before we connect, could you send us: (1) your ESG integration policy, (2) proxy voting record for 2025, (3) Article 8/9 fund list, (4) carbon footprint of SSIM's flagship ESG equity strategy.",
        "labels": ["UNREAD"],
        "needs_action": True,
        "starred": False,
    },
    {
        "id": "email_009",
        "from": "james.okonkwo@statestreet.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Q2 Attribution Analysis Ready",
        "date": f"{_TODAY}T07:45:00-04:00",
        "snippet": "Q2 attribution is ready for CalPERS. Global Equity passive: +12 bps vs benchmark net of fees. Main drag: healthcare sector tilt at rebalance. Document shared in Drive.",
        "labels": ["INBOX"],
        "needs_action": False,
        "starred": False,
    },
    {
        "id": "email_010",
        "from": "david.morrison@otpp.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "OTPP RFP — Shortlist Notification",
        "date": (
            datetime.date.today() - datetime.timedelta(days=2)
        ).isoformat() + "T14:00:00-04:00",
        "snippet": "We are pleased to inform you that SSIM has been shortlisted for the Active Quantitative Equity mandate. You are one of 4 managers invited to present. Today's call is your final presentation.",
        "labels": ["INBOX", "STARRED"],
        "needs_action": False,
        "starred": True,
    },
]

MOCK_MARKET_CONTEXT = {
    "date": _TODAY,
    "market_snapshot": {
        "sp500_futures": "+0.4%",
        "msci_world": "+0.2%",
        "msci_em": "-0.8%",
        "us_10y_yield": "4.21%",
        "usd_index": "+0.3%",
        "oil_wti": "-1.2%",
        "gold": "+0.1%",
        "vix": "14.2",
    },
    "ssim_aum_snapshot": {
        "total_aum": "$4.13 trillion",
        "equity_aum": "$2.8 trillion",
        "fixed_income_aum": "$0.9 trillion",
        "cash_aum": "$0.3 trillion",
        "multi_asset_aum": "$0.13 trillion",
        "esg_aum": "$0.6 trillion",
        "aum_change_mtd": "+$8.2B (net new + market appreciation)",
    },
    "key_events_today": [
        "Fed meeting minutes released at 2:00 PM ET — watch for language on rate path",
        "MSCI World rebalance effective date: June 2 — preparation and trade execution required",
        "NVDA earnings after market close — position review needed for tech-heavy mandates",
        "SEC Marketing Rule compliance deadline: Friday COB",
    ],
    "portfolio_alerts": [
        {
            "type": "index_rebalance",
            "severity": "high",
            "message": "MSCI World June rebalance: 47 additions, 31 deletions. Net flow ~$2.1B impact across passive mandates.",
            "action_required": "Coordinate with trading desk on execution schedule",
        },
        {
            "type": "mandate_renewal",
            "severity": "medium",
            "message": "CalPERS mandate renewal due Q3 2026 — fee negotiation in progress",
            "action_required": "Confirm fee proposal with BD team before today's meeting",
        },
        {
            "type": "esg_classification",
            "severity": "medium",
            "message": "3 SSIM funds under SFDR reclassification review (Article 8 → Article 9 upgrade)",
            "action_required": "ESG working group review today at 1pm",
        },
    ],
    "regulatory_reminders": [
        "AIFMD reporting deadline: June 30, 2026",
        "SEC Form ADV annual update: filed",
        "MiFID II transaction reporting: current",
        "SFDR periodic reports: Q2 due July 31",
    ],
    "securities_lending": {
        "utilisation_rate": "67%",
        "revenue_ytd": "$142M",
        "top_earner": "SSIM Global Equity Index (Enhanced Class)",
        "alert": "Recall pending on 3 positions for MSCI rebalance — trading desk notified",
    },
}

# ════════════════════════════════════════════════════════════════════════════
# Folded-in Meeting Prep data (Drive documents + customer/CRM profiles).
# Copied from the meeting_prep agent so Daily Briefing can produce a full prep
# brief for any meeting (the expandable per-meeting view).
# ════════════════════════════════════════════════════════════════════════════

MOCK_DRIVE_DOCS = [
    {
        "id": "doc_001",
        "name": "CalPERS — SSIM Global Equity Passive Mandate — Q2 2026 Report",
        "mimeType": "application/vnd.google-apps.document",
        "webViewLink": "https://docs.google.com/document/d/mock_calpers_q2/edit",
        "modifiedTime": f"{_TODAY}T07:00:00Z",
        "category": "client_report",
        "tags": ["calpers", "passive", "equity", "q2", "2026", "performance", "attribution"],
        "content": """CalPERS Global Equity Passive Mandate — Q2 2026 Report

Portfolio Overview:
- AUM: $8.24 billion (as of June 30, 2026)
- Benchmark: MSCI World ex-Tobacco
- Mandate inception: March 2018

Q2 2026 Performance:
- Portfolio return: 4.82%
- Benchmark return: 4.70%
- Active return: +12 bps
- Information ratio (trailing 3Y): 0.8

Attribution:
- Securities lending revenue: +8 bps
- Rebalance execution efficiency: +4 bps
- Residual tracking error: 0 bps
- Expense ratio: -3 bps (net)

ESG Screening Status:
- Tobacco exclusions: fully implemented (43 securities removed)
- Weapons exclusions: current
- New climate exclusion list from CalPERS received — implementation timeline: Q3 2026

Mandate Renewal:
- Current contract expires: December 31, 2026
- Proposed fee: 1.2 bps on first $5B, 0.8 bps above $5B
- Competitor fee range (Vanguard, BlackRock): 1.0–1.5 bps
""",
    },
    {
        "id": "doc_002",
        "name": "SSIM Active Quantitative Equity — Strategy Overview & Track Record",
        "mimeType": "application/vnd.google-apps.presentation",
        "webViewLink": "https://docs.google.com/presentation/d/mock_active_quant/edit",
        "modifiedTime": (datetime.date.today() - datetime.timedelta(days=10)).isoformat() + "T12:00:00Z",
        "category": "strategy",
        "tags": ["active", "quantitative", "equity", "factor", "track record", "otpp"],
        "content": """SSIM Active Quantitative Equity — Strategy Overview

Strategy Overview:
- AUM: $48.2 billion (as of May 2026)
- Inception: January 2008
- Benchmark: MSCI World
- Active Return Target: 150-250 bps gross of fees

5-Year Live Track Record (as of March 31, 2026):
- Annualised gross return: 11.8%
- Benchmark: 10.2%
- Active return (gross): +1.62%
- Active return (net of fees): +1.15%
- Sharpe ratio: 1.04
- Information ratio: 0.82
- Max drawdown (2022): -18.4% vs benchmark -20.1% (outperformed)
- Tracking error: 2.1% (within 1.5-3.0% target range)

Factor Exposures (as of May 2026):
- Value: +0.22
- Quality: +0.31
- Momentum: +0.18
- Low Volatility: +0.15
- Size: -0.05

Fee Schedule (proposed for $2B mandate):
- Management fee: 20 bps
- Performance fee: None (available on request)
- Comparison: Industry average for active quant ~25-35 bps
""",
    },
    {
        "id": "doc_003",
        "name": "SSIM ESG Integration Policy — 2026",
        "mimeType": "application/vnd.google-apps.document",
        "webViewLink": "https://docs.google.com/document/d/mock_esg_policy/edit",
        "modifiedTime": (datetime.date.today() - datetime.timedelta(days=45)).isoformat() + "T09:00:00Z",
        "category": "policy",
        "tags": ["esg", "integration", "policy", "sfdr", "article8", "article9", "gic", "calpers"],
        "content": """SSIM ESG Integration Policy — 2026

1. ESG Integration Framework
SSIM integrates ESG factors across all investment strategies through:
- Proprietary ESG scoring model (data from MSCI ESG, Sustainalytics, Bloomberg ESG)
- Negative screening (tobacco, weapons, coal, controversial weapons)
- Positive tilting in ESG-labelled strategies toward high ESG scorers
- Engagement and proxy voting programme

2. Proxy Voting Record (2025)
- Total meetings voted: 14,287
- Votes against management: 28% (industry avg: 22%)
- Climate resolutions supported: 89%
- Executive pay resolutions: 74% in line with management
- Key engagement theme: Board diversity, climate transition plans

3. SFDR Classification (as of Jan 2026)
- Article 9 funds: 12 (includes SSIM ESG Global Equity, SSIM Climate Leaders)
- Article 8 funds: 34
- Article 6 funds: 18

4. Carbon Footprint (Flagship ESG Equity Strategy, SSIM ESG Global Equity)
- Weighted Average Carbon Intensity: 87 tCO2e/$M revenue
- Benchmark (MSCI World): 142 tCO2e/$M revenue
- Carbon Reduction vs Benchmark: -39%
- Paris-alignment pathway: On track for 1.5°C scenario by 2040

5. Exclusion List
- Tobacco producers: full exclusion
- Thermal coal: >25% revenue threshold exclusion
- Conventional weapons: no exclusion (unless mandate-specific)
- Controversial weapons (cluster munitions, landmines): full exclusion
""",
    },
    {
        "id": "doc_004",
        "name": "Ontario Teachers' — RFP Response Draft — Active Quant Equity",
        "mimeType": "application/vnd.google-apps.document",
        "webViewLink": "https://docs.google.com/document/d/mock_otpp_rfp/edit",
        "modifiedTime": (datetime.date.today() - datetime.timedelta(days=21)).isoformat() + "T15:00:00Z",
        "category": "rfp",
        "tags": ["otpp", "rfp", "active", "quantitative", "equity"],
        "content": """SSIM RFP Response — Ontario Teachers' Pension Plan — Active Quantitative Equity

Section 1: Firm Overview
State Street Investment Management (SSIM) is a $4.1 trillion AUM global asset manager,
wholly owned by State Street Corporation. We serve 2,000+ institutional clients across 30 countries.

Section 2: Strategy
Our Active Quantitative Equity strategy has delivered consistent alpha since inception in 2008.
The strategy employs a systematic multi-factor approach combining value, quality, momentum,
and low volatility signals with a proprietary alternative data overlay.

Section 3: Risk Management
- Independent risk team reports to CRO (separate from PM team)
- Real-time factor monitoring and exposure limits
- 2022 max drawdown: -18.4% vs MSCI World -20.1%

Section 4: Team
- Portfolio Management: 12 PMs, average experience 18 years
- Research: 24 quant researchers (8 PhDs)
- Risk: 8 risk managers
- No departures from senior team in 5 years

Section 5: Fee Proposal
$2B mandate: 20 bps flat management fee
""",
    },
    {
        "id": "doc_005",
        "name": "SSIM Capabilities Deck — GIC Singapore Pre-read",
        "mimeType": "application/vnd.google-apps.presentation",
        "webViewLink": "https://docs.google.com/presentation/d/mock_gic_deck/edit",
        "modifiedTime": (datetime.date.today() - datetime.timedelta(days=3)).isoformat() + "T11:00:00Z",
        "category": "pitch_deck",
        "tags": ["gic", "singapore", "esg", "equity", "sfdr", "sovereign wealth"],
        "content": "SSIM Capabilities Deck prepared for GIC. Covers: firm overview, ESG integration, SFDR compliance, track records, team structure.",
    },
]

MOCK_CUSTOMER_PROFILES = [
    {
        "name": "CalPERS",
        "full_name": "California Public Employees' Retirement System",
        "keywords": ["calpers", "california"],
        "type": "Public Pension Fund",
        "country": "United States",
        "total_aum": "$490 billion",
        "ssim_relationship": {
            "status": "Active Client",
            "since": "March 2018",
            "ssim_aum": "$8.24 billion",
            "strategies": ["Global Equity Passive (MSCI World ex-Tobacco)", "US Large Cap Index"],
            "primary_contact": "Michael Torres (Director of External Management)",
            "secondary_contact": "Jennifer Wu (Portfolio Analyst)",
            "relationship_manager": "Sarah Chen (SSIM)",
            "mandate_expiry": "December 31, 2026",
        },
        "investment_profile": {
            "return_objective": "7.0% actuarial return",
            "esg_requirements": "Active ESG voter, climate exclusions required, tobacco/weapons excluded",
            "key_concerns": ["Fee reduction", "ESG implementation", "EM expansion"],
            "upcoming_decisions": "Mandate renewal Q3 2026, potential EM allocation of $500M",
        },
        "recent_activity": "Q2 review today. CFO asking about fees. Interest in expanding to EM.",
    },
    {
        "name": "Ontario Teachers' Pension Plan",
        "full_name": "Ontario Teachers' Pension Plan Board (OTPP)",
        "keywords": ["otpp", "ontario", "teachers"],
        "type": "Canadian Public Pension Fund",
        "country": "Canada",
        "total_aum": "$255 billion (CAD)",
        "ssim_relationship": {
            "status": "Prospect — RFP Finalist",
            "since": "N/A — new mandate",
            "ssim_aum": "$0 (prospect)",
            "strategies": ["Shortlisted for $2B Active Quantitative Equity"],
            "primary_contact": "David Morrison (Head of External Managers)",
            "secondary_contact": "Francesca Lim (Senior Investment Analyst)",
            "cio": "Priya Mehta",
            "relationship_manager": "Peter Walsh (SSIM)",
        },
        "investment_profile": {
            "return_objective": "Real return of 4% above inflation",
            "esg_requirements": "Net Zero by 2050 commitment, TCFD aligned",
            "key_concerns": [
                "Correlation to existing managers (currently: Acadian, Two Sigma)",
                "Drawdown behaviour in stress periods",
                "Factor transparency",
                "Fee competitiveness",
            ],
            "upcoming_decisions": "Final manager selection in 30 days. $2B mandate award.",
        },
        "recent_activity": "Final pitch today. CIO joining unexpectedly. Must lead with risk management story.",
    },
    {
        "name": "GIC",
        "full_name": "GIC Private Limited (Government of Singapore Investment Corporation)",
        "keywords": ["gic", "singapore", "government of singapore"],
        "type": "Sovereign Wealth Fund",
        "country": "Singapore",
        "total_aum": ">$770 billion (estimated)",
        "ssim_relationship": {
            "status": "Prospect — Initial Scoping",
            "since": "N/A — new",
            "ssim_aum": "$0",
            "strategies": ["Exploring $5B ESG Global Equity mandate"],
            "primary_contact": "Wei Chen (Senior Investment Manager)",
            "relationship_manager": "Dev (SSIM — initial contact)",
        },
        "investment_profile": {
            "return_objective": "Long-term real returns above global inflation",
            "esg_requirements": "Strong ESG requirements — SFDR Article 8 minimum, Article 9 preferred",
            "key_concerns": [
                "SFDR compliance (EU classification)",
                "Carbon footprint vs benchmark",
                "Proxy voting record on climate",
                "ESG data quality and transparency",
            ],
            "upcoming_decisions": "Initial scoping call tomorrow — no decision timeline set yet",
        },
        "recent_activity": "Pre-call questions received: ESG policy, proxy record, Article list, carbon footprint.",
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
    {"id": "bk_001", "room_id": "room_bos1_4a", "event_title": "Morning Portfolio Review", "date": _TODAY, "start": f"{_TODAY}T08:30:00-04:00", "end": f"{_TODAY}T09:00:00-04:00", "organizer": "james.okonkwo@statestreet.com"},
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
        "title": "CalPERS EM Allocation — Scoping Call",
        "rationale": "Michael Torres (CalPERS) raised interest in a $500M EM allocation; no meeting is on the calendar yet.",
        "suggested_attendees": [
            "michael.torres@calpers.ca.gov",
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
        "title": "OTPP Pitch Debrief (internal)",
        "rationale": "After today's OTPP final pitch, an internal debrief will capture follow-ups before the 30-day selection window closes.",
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
        "title": "SEC Marketing Rule — Compliance Sign-off Session",
        "rationale": "Compliance flagged the SEC Marketing Rule review is due Friday COB; a working session is needed to review composite performance presentations.",
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
        "title": "MSCI World Rebalance — Trading Desk Coordination",
        "rationale": "MSCI World June rebalance (~$2.1B flow impact) needs an execution-schedule sync with the trading desk before the effective date.",
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
