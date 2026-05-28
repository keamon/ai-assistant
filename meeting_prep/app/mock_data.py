"""
Mock data for Meeting Prep Agent — State Street Investment Management.
Simulates Google Calendar, Gmail, Drive, and customer CRM responses.
"""

import datetime

_TODAY = datetime.date.today().isoformat()
_TOMORROW = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
_NEXT_WEEK = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()

MOCK_CALENDAR_EVENTS = [
    {
        "id": "cal_001",
        "date": _TODAY,
        "title": "CalPERS — Q2 2026 Investment Review",
        "start": f"{_TODAY}T10:00:00-04:00",
        "end": f"{_TODAY}T11:30:00-04:00",
        "location": "Zoom",
        "description": "Quarterly review of CalPERS' $8.2B passive equity mandate. Topics: Q2 performance attribution, ESG screening update, fee schedule discussion for upcoming renewal.",
        "attendees": [
            "michael.torres@calpers.ca.gov",
            "jennifer.wu@calpers.ca.gov",
            "dev@chenkeamonwang.altostrat.com",
            "sarah.chen@statestreet.com",
            "robert.kim@statestreet.com",
        ],
        "meeting_type": "customer",
        "is_customer_meeting": True,
        "video_link": "https://zoom.us/j/12345678",
        "organizer": "dev@chenkeamonwang.altostrat.com",
    },
    {
        "id": "cal_002",
        "date": _TODAY,
        "title": "New Mandate Pitch — Ontario Teachers' Pension Plan (OTPP)",
        "start": f"{_TODAY}T15:00:00-04:00",
        "end": f"{_TODAY}T16:30:00-04:00",
        "location": "Video",
        "description": "Final presentation for $2B Active Quantitative Equity mandate. OTPP shortlisted 4 managers. CIO Priya Mehta joining unexpectedly. Focus on systematic approach, risk management, and factor exposures.",
        "attendees": [
            "david.morrison@otpp.com",
            "francesca.lim@otpp.com",
            "priya.mehta@otpp.com",
            "dev@chenkeamonwang.altostrat.com",
            "peter.walsh@statestreet.com",
        ],
        "meeting_type": "customer",
        "is_customer_meeting": True,
        "video_link": "https://zoom.us/j/87654321",
        "organizer": "dev@chenkeamonwang.altostrat.com",
    },
    {
        "id": "cal_003",
        "date": _TOMORROW,
        "title": "Singapore GIC — ESG Mandate Scoping Call",
        "start": f"{_TOMORROW}T09:00:00-04:00",
        "end": f"{_TOMORROW}T10:00:00-04:00",
        "location": "Video",
        "description": "Initial scoping call for potential $5B ESG Global Equity mandate. GIC exploring options for new sustainable allocation. Pre-read requests: ESG policy, proxy voting record, Article 8/9 fund list.",
        "attendees": [
            "wei.chen@gic.com.sg",
            "dev@chenkeamonwang.altostrat.com",
        ],
        "meeting_type": "customer",
        "is_customer_meeting": True,
        "video_link": "https://meet.google.com/xyz-abc-def",
        "organizer": "wei.chen@gic.com.sg",
    },
    {
        "id": "cal_004",
        "date": _NEXT_WEEK,
        "title": "ESG Integration Working Group",
        "start": f"{_NEXT_WEEK}T13:00:00-04:00",
        "end": f"{_NEXT_WEEK}T14:00:00-04:00",
        "location": "Teams",
        "description": "Monthly working group: SFDR Article 8/9 reclassification, proxy voting decisions Q2, climate data vendor evaluation.",
        "attendees": [
            "anna.petrov@statestreet.com",
            "dev@chenkeamonwang.altostrat.com",
            "mark.johnson@statestreet.com",
            "lisa.huang@statestreet.com",
        ],
        "meeting_type": "internal",
        "is_customer_meeting": False,
        "video_link": "https://teams.microsoft.com/l/meetup-join/mock",
        "organizer": "anna.petrov@statestreet.com",
    },
    {
        "id": "cal_005",
        "date": _NEXT_WEEK,
        "title": "Mercer Consultant Briefing — SSIM Active Quant Capabilities",
        "start": f"{_NEXT_WEEK}T14:00:00-04:00",
        "end": f"{_NEXT_WEEK}T15:00:00-04:00",
        "location": "Boston Office",
        "description": "Annual update briefing with Mercer's investment consulting team. Covers SSIM AUM, strategy updates, performance, and new product launches.",
        "attendees": [
            "alexandra.reed@mercer.com",
            "brandon.lee@mercer.com",
            "dev@chenkeamonwang.altostrat.com",
            "peter.walsh@statestreet.com",
        ],
        "meeting_type": "external",
        "is_customer_meeting": False,
        "video_link": "",
        "organizer": "dev@chenkeamonwang.altostrat.com",
    },
]

MOCK_EMAILS = [
    {
        "id": "e001",
        "from": "michael.torres@calpers.ca.gov",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "RE: Q2 2026 Performance — Agenda Items for Today",
        "date": f"{_TODAY}T07:15:00-04:00",
        "snippet": "Please confirm Q2 attribution analysis is ready. CFO asking about fee schedule for renewal. Also — can we discuss an expansion to include EM allocation?",
    },
    {
        "id": "e002",
        "from": "jennifer.wu@calpers.ca.gov",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "CalPERS ESG Requirements — Updated Policy",
        "date": (datetime.date.today() - datetime.timedelta(days=14)).isoformat() + "T10:00:00-04:00",
        "snippet": "Please review our updated ESG investment policy attached. We require all managers to comply with our enhanced climate exclusions list effective September 2026.",
    },
    {
        "id": "e003",
        "from": "francesca.lim@otpp.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "OTPP Active Quant RFP — Today's Agenda",
        "date": f"{_TODAY}T08:00:00-04:00",
        "snippet": "Confirming today's 3pm call. CIO Priya Mehta will join. Please lead with: (1) live track record 5yr, (2) factor exposures, (3) drawdown in 2022, (4) fees for $2B.",
    },
    {
        "id": "e004",
        "from": "priya.mehta@otpp.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Background on OTPP's Active Equity Programme",
        "date": (datetime.date.today() - datetime.timedelta(days=30)).isoformat() + "T09:00:00-04:00",
        "snippet": "As we evaluate active managers, key priorities: (1) low correlation to our existing managers, (2) strong risk-adjusted returns over full cycle, (3) transparent factor exposures, (4) competitive fees.",
    },
    {
        "id": "e005",
        "from": "wei.chen@gic.com.sg",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "GIC ESG Mandate — Pre-call Questions",
        "date": f"{_TODAY}T03:00:00-04:00",
        "snippet": "Before tomorrow's call: please send (1) ESG integration policy, (2) proxy voting record 2025, (3) Article 8/9 fund list, (4) carbon footprint of flagship ESG equity strategy.",
    },
    {
        "id": "e006",
        "from": "alexandra.reed@mercer.com",
        "to": "dev@chenkeamonwang.altostrat.com",
        "subject": "Annual Manager Briefing — Mercer Next Week",
        "date": (datetime.date.today() - datetime.timedelta(days=5)).isoformat() + "T14:00:00-04:00",
        "snippet": "Looking forward to next week's briefing. We'd like to understand any changes to investment team, performance attribution for H1 2026, and your ESG analytics enhancements.",
    },
]

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
    {
        "name": "Mercer",
        "full_name": "Mercer Investment Consulting",
        "keywords": ["mercer"],
        "type": "Investment Consultant",
        "country": "United States",
        "total_aum": "N/A (consultant)",
        "ssim_relationship": {
            "status": "Consultant — Active Coverage",
            "since": "2015",
            "ssim_aum": "Influences ~$18B of SSIM mandates via ratings",
            "strategies": ["A-rated on: Global Equity Passive, Active Quant Equity, ESG strategies"],
            "primary_contact": "Alexandra Reed (Head of Manager Research — Americas)",
            "secondary_contact": "Brandon Lee (Manager Research Analyst)",
            "relationship_manager": "Peter Walsh (SSIM)",
        },
        "investment_profile": {
            "esg_requirements": "Assess ESG integration quality for all rated strategies",
            "key_concerns": ["Team stability", "Performance consistency", "ESG analytics"],
            "upcoming_decisions": "Annual manager briefing next week — ratings review scheduled",
        },
        "recent_activity": "Annual briefing next week. Want updates on team, H1 performance, ESG analytics.",
    },
]
