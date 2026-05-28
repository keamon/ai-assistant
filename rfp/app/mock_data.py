"""
Mock data for RFP Response Agent — State Street Investment Management.
Simulates internal SSIM document library and sample RFP content.
"""

MOCK_DRIVE_DOCS = [
    {
        "id": "drive_001",
        "name": "SSIM Firm Overview — 2026",
        "category": "firm_overview",
        "tags": ["firm overview", "aum", "history", "team", "structure"],
        "content": """State Street Investment Management (SSIM) — Firm Overview 2026

Firm Overview:
State Street Investment Management is the asset management arm of State Street Corporation,
one of the world's largest financial services companies. SSIM manages approximately $4.13
trillion in assets under management (as of March 31, 2026) on behalf of approximately 2,000
institutional clients in over 40 countries.

Key Facts:
- Founded: 1978 (as part of State Street Corporation, est. 1792)
- Headquarters: Boston, Massachusetts
- Offices: 28 offices globally (US, Europe, Asia-Pacific)
- Employees: ~2,400 investment professionals
- AUM: $4.13 trillion
- Client types: Pension funds, sovereign wealth funds, insurance companies,
  endowments, foundations, wealth management platforms

AUM Breakdown by Asset Class:
- Passive Equity: $2.1 trillion
- Fixed Income: $0.9 trillion (passive and active)
- Active Quantitative Equity: $0.48 billion
- Multi-Asset: $0.13 trillion
- ESG/Sustainable: $0.6 trillion
- Cash Management: $0.3 trillion

Investment Philosophy:
SSIM believes that combining disciplined index replication with active risk management
and ESG integration delivers superior long-term outcomes for institutional investors.
Our passive strategies are designed to minimise tracking error and maximise securities
lending income, while our active strategies employ systematic, factor-based approaches
backed by over 40 years of research.

Ownership:
SSIM is wholly owned by State Street Corporation (NYSE: STT), providing clients with
the financial stability of a $3.1 trillion custodian bank combined with the investment
excellence of a dedicated asset manager.
""",
    },
    {
        "id": "drive_002",
        "name": "SSIM Investment Team Biographies — 2026",
        "category": "team",
        "tags": ["team", "investment team", "biographies", "portfolio managers", "experience"],
        "content": """SSIM Investment Team — Key Biographies 2026

Portfolio Management Leadership:

Dr. Katherine Morris — CIO, Active Strategies
- 25 years investment management experience
- Ph.D. Finance, MIT Sloan
- Former: Goldman Sachs Asset Management, AQR Capital
- Oversees $0.6T active strategies including Active Quant Equity

Richard Zhang — Head of Index Strategies
- 20 years index management experience
- CFA, MSc Statistics, London School of Economics
- Former: Vanguard Institutional (10 years)
- Oversees $2.1T passive equity strategies; tracking error <3bps across mandates

Dr. Amara Osei — Head of ESG Research & Integration
- 18 years ESG and responsible investment experience
- Ph.D. Environmental Economics, Cambridge University
- Former: UNPRI Secretariat, Hermes Investment Management
- Leads ESG integration across all $4.1T AUM

Investment Team Composition:
- Portfolio Managers: 48 (average experience: 17 years)
- Quantitative Researchers: 35 (12 with Ph.D.)
- Risk Managers: 22
- ESG Analysts: 18
- Traders: 65
- Operations: 120

Team Stability:
- Senior PM departures (last 5 years): 2 (both retirement)
- Average PM tenure at SSIM: 11.4 years
""",
    },
    {
        "id": "drive_003",
        "name": "SSIM Global Equity Index — Strategy Fact Sheet — Q1 2026",
        "category": "fund_fact_sheet",
        "tags": ["global equity", "index", "passive", "track record", "msci world", "performance",
                 "composite", "attribution"],
        "content": """SSIM Global Equity Index Strategy — Fact Sheet Q1 2026

Strategy Overview:
- AUM: $890 billion (as of March 31, 2026)
- Benchmark: MSCI World Index (standard)
- Inception Date: January 2002
- Vehicle Types: SMA, commingled fund, UCITS

Performance (Net of Fees, Annualised as of March 31, 2026):
              Strategy    Benchmark    Excess Return
1 Year:       18.4%       18.2%        +0.2%
3 Year:       11.2%       11.0%        +0.2%
5 Year:       14.8%       14.6%        +0.2%
10 Year:      12.4%       12.2%        +0.2%
Since Inception: 9.8%     9.6%         +0.2%

Key Metrics:
- Tracking Error (3Y): 0.03% (3 basis points)
- Average Annual Securities Lending Revenue: +8 to +12 bps
- Total Expense Ratio: 1.2 bps (large mandate > $1B)
- Number of Holdings: 1,512 (full replication to 99.8%)

Portfolio Construction:
Full physical replication of MSCI World Index.
Securities lending programme adds 8-12 bps annually.
Corporate action processing: same-day execution.
Dividend reinvestment: immediate (T+0 where possible).

ESG Overlay Options:
- Standard (no ESG screen): base fee 1.2 bps
- ESG screened (tobacco, weapons exclusion): +0.2 bps
- Enhanced ESG (SSIM exclusion list + tilt): +0.5 bps
- Custom ESG (client-defined): fee on request

Risk Controls:
- Automated factor exposure monitoring vs benchmark
- Liquidity buffer maintained at 0.5% cash minimum
- Rebalancing: at index reconstitution dates + corporate actions
""",
    },
    {
        "id": "drive_004",
        "name": "SSIM Active Quantitative Equity — Strategy Overview & Track Record",
        "category": "strategy",
        "tags": ["active", "quantitative", "equity", "factor", "track record", "composite",
                 "performance", "attribution", "systematic"],
        "content": """SSIM Active Quantitative Equity Strategy — Overview & Track Record

Strategy Overview:
- AUM: $48.2 billion
- Benchmark: MSCI World
- Active Return Target: 150-250 bps gross of fees
- Inception: January 2008
- Vehicles: SMA, UCITS, Cayman fund

Investment Process:
1. Universe: MSCI World (1,500+ securities)
2. Signals: Proprietary multi-factor model
   - Value (P/E, P/B, FCF yield): 25% weight
   - Quality (ROE, earnings stability, leverage): 25% weight
   - Momentum (12-1 month): 20% weight
   - Low Volatility (3Y beta, realized vol): 15% weight
   - Alternative Data (sentiment, supply chain): 15% weight
3. Portfolio Construction: Risk-controlled optimisation
   - Tracking error target: 1.5-3.0%
   - Sector deviation: ±5%
   - Single stock: ±2% active weight
4. Risk Management: Independent daily monitoring, pre-trade compliance

Performance (Gross of Fees, Annualised as of March 31, 2026):
              Strategy    Benchmark    Alpha
1 Year:       19.8%       18.2%        +1.6%
3 Year:       13.1%       11.0%        +2.1%
5 Year:       16.5%       14.6%        +1.9%
Since Inception: 11.2%    9.2%         +2.0%

Risk Metrics (5Y):
- Annualised Tracking Error: 2.1%
- Information Ratio: 0.90
- Sharpe Ratio (net): 1.04
- Maximum Drawdown (2022 selloff): -18.4% vs MSCI World -20.1%
- Upside Capture: 106% | Downside Capture: 91%

Fee Schedule:
- First $1B: 25 bps
- $1B - $3B: 20 bps
- Above $3B: 15 bps
- Minimum investment: $200M
""",
    },
    {
        "id": "drive_005",
        "name": "SSIM ESG Integration Policy & Stewardship Report — 2026",
        "category": "policy",
        "tags": ["esg", "integration", "policy", "stewardship", "proxy voting", "engagement",
                 "sfdr", "article8", "article9", "carbon", "climate", "responsible investment",
                 "net zero", "tcfd"],
        "content": """SSIM ESG Integration Policy & Stewardship Report 2026

1. ESG Integration Philosophy
SSIM integrates ESG considerations across all investment strategies as a material risk
and opportunity factor. We believe companies with strong ESG profiles are better
positioned for long-term value creation.

2. ESG Data Sources
- MSCI ESG Research (primary equity ESG scores)
- Sustainalytics (risk ratings, controversy monitoring)
- Bloomberg ESG (fixed income, green bonds)
- ISS Governance (proxy voting intelligence)
- SSIM Proprietary ESG Model (alternative data overlay)

3. SFDR Classification (as of January 2026)
- Article 9 (Sustainable Investment): 12 funds
  Including: SSIM Climate Leaders Fund, SSIM ESG Global Equity UCITS
- Article 8 (Promotes ESG Characteristics): 34 funds
  Including: SSIM Global Equity ESG Screened, SSIM ESG Corporate Bond
- Article 6 (Mainstream): 18 funds

4. Proxy Voting Programme
2025 Voting Statistics:
- Total meetings voted: 14,287 (across 48 markets)
- Total resolutions voted: 142,891
- Votes against management: 28% (industry average: 22%)
- Climate/environment resolutions supported: 89%
- Board diversity resolutions supported: 94%
- Executive compensation: 74% aligned with management

Key Engagement Theme 2025-2026: Climate Transition Planning
- 187 companies engaged on climate transition plans
- 23 companies added to SSIM watch list for escalation

5. Exclusion Lists
Standard Exclusion (all SSIM funds):
- Controversial weapons: 100% (cluster munitions, biological, chemical, anti-personnel mines)

ESG Screened Exclusions (Article 8+ funds):
- Tobacco producers: 100% exclusion
- Thermal coal: >25% revenue exclusion
- Civilian firearms manufacturers: exclusion

ESG Enhanced / Article 9 Exclusions:
- All above plus: Gambling >50% revenue, Adult entertainment

6. Carbon Footprint (Flagship: SSIM ESG Global Equity)
- Weighted Average Carbon Intensity: 87 tCO2e/$M revenue
- Benchmark (MSCI World): 142 tCO2e/$M revenue
- Carbon Reduction vs Benchmark: -39%
- Paris-alignment pathway: On track for 1.5°C by 2040
- Net Zero commitment: SSIM is a signatory to Net Zero Asset Managers initiative
  Target: 100% of AUM aligned to net zero by 2050
""",
    },
    {
        "id": "drive_006",
        "name": "SSIM Fee Schedule — Institutional Mandates 2026",
        "category": "fee_schedule",
        "tags": ["fee", "fee schedule", "management fee", "pricing", "bps", "basis points",
                 "performance fee", "minimum"],
        "content": """SSIM Institutional Fee Schedule — 2026

PASSIVE EQUITY STRATEGIES
Global Equity Index (MSCI World/ACWI):
  < $500M:     2.5 bps
  $500M - $1B: 1.8 bps
  $1B - $5B:   1.2 bps
  > $5B:       0.8 bps

US Equity Index (S&P 500, Russell):
  < $500M:     1.5 bps
  $500M - $1B: 1.0 bps
  > $1B:       0.7 bps

Emerging Markets Index (MSCI EM):
  < $500M:     8.0 bps
  $500M - $1B: 5.5 bps
  > $1B:       4.0 bps

ESG Screened overlay: +0.2-0.5 bps to base fee

PASSIVE FIXED INCOME STRATEGIES
Global Aggregate (Bloomberg Global Agg):
  < $500M:     3.5 bps
  > $500M:     2.5 bps

Investment Grade Credit:
  < $500M:     4.0 bps
  > $500M:     3.0 bps

ACTIVE QUANTITATIVE EQUITY
  < $1B:       25 bps
  $1B - $3B:   20 bps
  > $3B:       15 bps
  Performance fee: Available on request (20% above benchmark)

ESG / SUSTAINABLE STRATEGIES
SSIM ESG Global Equity (Article 9):
  < $500M:     12 bps
  $500M - $1B: 8 bps
  > $1B:       6 bps

SSIM Climate Leaders Fund (Article 9):
  < $500M:     15 bps
  > $500M:     10 bps

CASH MANAGEMENT
SSIM Prime Liquidity Fund:   5 bps
SSIM Government Money Market: 3.5 bps
SSIM Enhanced Cash (1-3M):   7 bps

SECURITIES LENDING
Revenue share to client: 70-80% of gross lending revenue
(net benefit to client typically +8-15 bps on equity mandates)

Notes:
- All fees quoted in basis points per annum on AUM
- Fees are negotiable for large mandates (>$3B) and multi-strategy relationships
- Minimum investment: $100M (passive), $200M (active)
- Performance fees available on active strategies (subject to negotiation)
""",
    },
    {
        "id": "drive_007",
        "name": "SSIM Operations & Risk Framework — Due Diligence Questionnaire Response",
        "category": "ddq",
        "tags": ["operations", "risk framework", "compliance", "trade execution", "custodian",
                 "reporting", "due diligence", "ddq", "controls", "settlement"],
        "content": """SSIM Operations & Risk Framework — Due Diligence Questionnaire (DDQ) 2026

1. Investment Risk Management
- Independent Risk team (25 professionals) separate from portfolio management
- Reports to Chief Risk Officer (not CIO) — ensures independence
- Daily VaR monitoring (parametric and historical simulation)
- Real-time pre-trade compliance checking (Charles River)
- Stress testing: weekly (market scenarios) and monthly (custom scenarios)
- Investment policy violations: zero tolerance; automatic position block

2. Trade Execution
- Best execution policy: mandatory for all mandates
- Execution venues: 85+ global brokers, 12 electronic trading platforms
- Average slippage vs VWAP (2025): -0.4 bps (outperforming target)
- TCA (Transaction Cost Analysis): daily, provided to clients quarterly

3. Operational Infrastructure
- OMS: Charles River Development (upgrading to cloud-native 2026)
- Portfolio accounting: SimCorp Dimension
- Custodians: Multiple (client choice); State Street Global Services preferred
- NAV calculation: T+1 for all funds
- Reconciliation: Daily automated reconciliation with all custodians

4. Compliance & Regulatory
- Chief Compliance Officer: independent function
- Regulatory coverage: SEC, FCA, BaFin, MAS, CSSF registered
- Marketing Rule compliance: automated validation system
- MiFID II: fully compliant (transaction reporting, best execution)
- AIFMD: compliant for all EU-distributed funds
- GIPS: All composites maintained in compliance with GIPS 2020

5. Business Continuity
- RPO: 4 hours | RTO: 2 hours for critical trading systems
- Dual data centres (Boston, London primary; failover sites active)
- BCP testing: semi-annual
- Pandemic/remote work: fully operational (proven during COVID-19)

6. Client Reporting
- Standard reporting: monthly (performance, attribution, risk), quarterly (full)
- Custom reporting: available in Excel, PDF, API formats
- Reporting platform: SSIM Client Portal (24/7 access)
- Ad-hoc requests: 48-hour turnaround SLA
""",
    },
    {
        "id": "drive_008",
        "name": "SSIM Fixed Income — Strategy Lineup & Fact Sheets",
        "category": "fund_fact_sheet",
        "tags": ["fixed income", "bond", "aggregate", "credit", "government", "esg bond",
                 "passive", "track record", "performance"],
        "content": """SSIM Fixed Income Strategies — Overview 2026

1. SSIM Global Aggregate Bond Index
AUM: $180B | Benchmark: Bloomberg Global Aggregate
5Y Net Return: 2.8% vs 2.6% (benchmark) | TE: 2 bps

2. SSIM US Investment Grade Corporate Bond
AUM: $95B | Benchmark: Bloomberg US Corporate
5Y Net Return: 4.1% vs 3.9% | TE: 4 bps

3. SSIM ESG Corporate Bond (Article 8)
AUM: $28B | Benchmark: Bloomberg MSCI ESG Corporate
5Y Net Return: 4.3% vs 4.1% | ESG score avg: 7.2/10
Carbon reduction vs parent index: -42%

4. SSIM Emerging Market Debt
AUM: $32B | Benchmark: JPMorgan EMBI Global
5Y Net Return: 5.8% vs 5.4% | TE: 18 bps

5. SSIM Short Duration / Cash Management
- Prime Liquidity: $85B | 7-day yield: 5.21%
- Government MMF: $42B | 7-day yield: 5.08%
- Enhanced Cash (1-3M): $18B | 30-day yield: 5.45%
""",
    },
]

MOCK_RFP_INTERNAL_DOCS = {
    "sample_rfp": {
        "name": "Sample RFP — California Public Employees' Retirement System",
        "content": """REQUEST FOR PROPOSAL
Investment Management Services — Global Equity Index Strategy
California Public Employees' Retirement System (CalPERS)

Issued: May 1, 2026
Response Deadline: June 30, 2026

SECTION 1: INTRODUCTION
CalPERS, with approximately $490 billion in assets under management, is seeking proposals
from qualified investment management firms to manage a $3 billion Global Equity Index
mandate benchmarked to the MSCI World ex-Tobacco Index.

SECTION 2: FIRM INFORMATION
2.1 Please provide a brief description of your firm, ownership structure, and AUM.
2.2 Describe your firm's financial stability and regulatory standing.
2.3 Provide a list of your 10 largest institutional clients (fund type and AUM only).
2.4 Describe any material regulatory actions, litigation, or significant business changes
    in the past 3 years.

SECTION 3: INVESTMENT PROCESS
3.1 Describe your index replication methodology for this mandate.
3.2 How do you handle corporate actions, index rebalances, and liquidity events?
3.3 Describe your securities lending programme and typical income generated.
3.4 What is your approach to cash management and dividend reinvestment?
3.5 Describe your execution approach and how you minimise market impact.

SECTION 4: ESG & RESPONSIBLE INVESTMENT
4.1 How do you integrate ESG factors into passive index management?
4.2 Describe your proxy voting programme: governance, record, key themes.
4.3 How do you implement custom ESG exclusion lists?
4.4 Provide your carbon footprint data vs benchmark.
4.5 Describe your commitment to net zero and climate transition.

SECTION 5: PERFORMANCE & RISK
5.1 Provide 10-year GIPS-compliant composite performance vs benchmark (net and gross).
5.2 What is your historical tracking error? Target going forward?
5.3 Describe your risk management framework and monitoring processes.
5.4 How did the mandate perform during market stress events (2020 COVID, 2022 selloff)?

SECTION 6: TEAM & ORGANISATION
6.1 Describe the portfolio management team responsible for this mandate.
6.2 Describe key person risk and succession planning.
6.3 Any team changes in the past 3 years?

SECTION 7: OPERATIONS & REPORTING
7.1 Describe your operational infrastructure: OMS, accounting, custodian relationships.
7.2 What reporting do you provide? Frequency, format, customisation?
7.3 Describe your business continuity and disaster recovery capabilities.
7.4 Are you GIPS compliant?

SECTION 8: FEES
8.1 Provide your proposed fee schedule for a $3 billion mandate.
8.2 Are there additional charges (transition, reporting, etc.)?
8.3 What is the fee structure if the mandate grows above $5 billion?

SECTION 9: REFERENCES
Please provide 3 institutional client references with similar mandates.

Submission: Please respond to all sections. Responses should be no longer than 50 pages
plus appendices. Submit via secure portal by June 30, 2026.
""",
        "tags": ["rfp", "calpers", "global equity", "index", "msci world"],
    },
    "past_rfp_global_equity": {
        "name": "SSIM Past RFP Response — Global Equity Index (Template)",
        "tags": ["rfp response", "global equity", "index", "template", "past rfp"],
        "content": """[SSIM Internal Use Only — Past RFP Response Template]
SSIM Global Equity Index RFP — Standard Response Template

Section 2 (Firm): SSIM manages $4.13T for 2,000+ institutional clients. Wholly owned by
State Street Corporation (NYSE: STT, $3.1T custodian). No material regulatory actions.
Largest clients include sovereign wealth funds, pension funds, and insurance companies.

Section 3 (Process): Full physical replication methodology. Corporate actions processed
same-day. Securities lending programme generates +8-12 bps annually (client receives 70%
of gross income). Dividend reinvestment T+0 where operationally possible. TCA provided
quarterly; average slippage -0.4 bps vs VWAP.

Section 5 (Performance): 10Y composite: +0.2% net of fees above benchmark consistently.
Historical tracking error: 2-4 bps. COVID 2020: minimal divergence (+1 bp TE spike for
2 weeks). 2022 selloff: portfolio fell in line with benchmark; securities lending provided
+10 bps cushion.

Section 8 (Fees): $3B mandate: 1.2 bps management fee. No transition fee (we fund
transition costs for mandates >$1B). Reporting included. Fee reduces to 0.8 bps above $5B.
""",
    },
    "esg_ddq_standard": {
        "name": "SSIM ESG Due Diligence Questionnaire — Standard Response",
        "tags": ["esg", "ddq", "due diligence", "sfdr", "proxy voting", "responsible investment",
                 "stewardship", "carbon", "net zero"],
        "content": """SSIM ESG DDQ — Standard Response

Q: How do you integrate ESG into passive strategies?
A: SSIM integrates ESG through: (1) negative screening (client-customisable), (2) securities
lending recall for critical votes, (3) engagement with index constituents on material ESG
issues, (4) ESG data overlay for risk monitoring.

Q: Proxy voting approach?
A: SSIM votes 100% of proxies across all markets. 2025: 14,287 meetings, 89% climate
resolutions supported. We engage companies pre-vote on material issues. ISS advisory
but SSIM maintains independent voting policy.

Q: SFDR classification?
A: 12 Article 9 funds (sustainable investment objective), 34 Article 8 funds (ESG promotion),
18 Article 6. Custom mandates can achieve Article 8 with ESG screen + engagement.

Q: Carbon footprint?
A: Standard global equity index: same footprint as MSCI World (142 tCO2e/$M revenue).
ESG screened: -25% reduction vs benchmark. Article 9 (ESG Global Equity): -39% reduction
(87 tCO2e/$M vs 142 benchmark). Article 9 funds Paris-aligned for 1.5°C by 2040.

Q: Net zero commitment?
A: SSIM is signatory to Net Zero Asset Managers initiative. Target: 100% AUM aligned
to net zero pathways by 2050. 2025 milestone: 50% AUM covered by net zero targets.
""",
    },
    "securities_lending_overview": {
        "name": "SSIM Securities Lending Programme — Overview",
        "tags": ["securities lending", "revenue", "lending", "collateral", "beneficial owner",
                 "income", "returns"],
        "content": """SSIM Securities Lending Programme 2026

Programme Overview:
SSIM's securities lending programme leverages State Street Corporation's global agency
lending infrastructure, one of the largest in the world with $4.2 trillion in lendable assets.

Key Benefits to Clients:
- Revenue share: 70-80% of gross lending income to client
- Typical annual revenue: +8 to +15 basis points on equity mandates
- Conservative collateral management (102% cash or government bonds)
- Indemnification: SSIM provides borrower default indemnification (counterparty risk eliminated)
- Recall: any position recalled within T+1 for voting, corporate actions, or liquidity needs

2025 Programme Statistics:
- Total assets on loan: $285 billion peak
- Average utilisation rate: 62%
- Revenue generated for clients: $1.8 billion gross ($1.3 billion net to clients)
- Borrower defaults: 0 (zero losses to clients in 20-year programme history)
- Average collateral over-collateralisation: 105.8%

Revenue by Strategy (2025, basis points net to client):
- SSIM Global Equity Index: +11 bps
- SSIM US Equity Index: +8 bps
- SSIM Emerging Markets Index: +22 bps
- SSIM Global Aggregate Bond: +3 bps

Competitive Advantage:
State Street is the world's largest securities lender. Our scale allows us to serve the
most specialised borrower demands (emerging markets, small caps, special situations),
typically generating 20-40% more revenue than smaller lending agents.
""",
    },
}
