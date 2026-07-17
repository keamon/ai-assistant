# SSIM Employee Digital Assistant — Ideas / Brainstorm

> Raw idea capture. Nothing here is committed scope. This feeds the PRD (`prd.md`),
> which feeds the spec (`spec.md`), which feeds stories, which feed code.
> Date: 2026-07-16

---

## 1. Vision

Combine SSIM's individual AI agents into a single **employee digital assistant** — one
clear, user-friendly surface where a State Street Investment Management employee can get
help across their whole day: briefings, meetings, projects, clients, RFPs, sales,
research, and compliance.

Today there are 5 standalone agents. The goal is to (a) add the missing agents and
(b) bring them together into one coherent product with a custom web app front-end.

**Audience:** portfolio managers, relationship managers, investment strategists, BD /
sales, project & ops leads, and senior leaders at SSIM (~$4.1T AUM, institutional-only).

---

## 2. What exists today (5 agents)

All are ADK + Gemini (`gemini-3.5-flash`) on Agent Runtime, GCP project
`logical-vim-478515-b1`, each with graceful **mock-data fallback** when Google APIs are
unavailable. Each lives in its own folder with `app/agent.py`, `app/mock_data.py`,
`app/agent_engine_app.py`, tests, and its own `pyproject.toml`/venv.

| Agent | Folder | Real data sources | Output |
|---|---|---|---|
| Daily Briefing | `daily_briefing/` | Gmail, Calendar, market context | Morning briefing (markdown) |
| Meeting Prep | `meeting_prep/` | Calendar, Gmail, Drive, customer profiles | Pre-meeting brief |
| Project Mgmt | `proj_ma/` | Jira (mock), Sheets | Workload analysis + exported plan sheet |
| RFP Response | `rfp/` | Drive docs | Drafted RFP → Google Doc |
| Sales Support | `sales/` | CRM (mock), products, competitive intel | Proposals, email drafts, competitive briefs |

**Gaps observed:**
1. **Investment/research side** is thin — PMs are a named audience but only get a shallow
   "market context" blob in Daily Briefing.
2. **Compliance/risk** is missing — RFP and Sales agents repeatedly emit `[VERIFY]` and
   "requires compliance review", but nothing catches those.
3. **No connective tissue** — the agents don't feed each other; each is a silo.
4. **No general "employee" support** — it's a client/BD/sales toolkit, not yet an
   all-employee assistant (no HR/IT/knowledge Q&A).

---

## 3. New agent ideas

### Tier 1 — highest leverage (gap filled × reuse of existing code)

#### 3.1 Compliance & Regulatory Assistant
- **Why:** closes the `[VERIFY]` / "requires compliance review" loop the RFP + Sales
  agents keep opening. Highest value in a regulated $4.1T shop.
- **Audience:** BD, sales, RFP, marketing, PMs — anyone producing client-facing material.
- **Data sources:** Drive compliance library (policies, DDQ answers, reg filings,
  disclosure templates); regulatory-calendar mock; disclosures/rules knowledge base mock.
- **Tools:**
  - `search_compliance_library(query, max_results=6)` — RAG over policies/IPS/reg filings.
  - `review_marketing_material(text, audience_type)` → `[{severity, issue, offending_text, suggested_fix, policy_source}]`.
  - `check_disclosure_requirements(document_type, jurisdiction, mandate_type)` → required disclosures (GIPS, Form ADV, Solvency II, ERISA 404(c)…).
  - `get_regulatory_calendar(jurisdiction="", days_ahead=90)` → upcoming filing deadlines.
  - `log_review_request(document_ref, requester, outcome)` — write, audit trail.
- **Prompt behavior:** first-pass reviewer, never final legal sign-off; always cite policy
  source; classify findings by severity; end with explicit "Escalate to Compliance: yes/no";
  never fabricate a rule (flag "not found in library").
- **Integration:** RFP + Sales call this before their `create_*_document` step; UI shows a
  compliance badge (green/amber/red) on generated drafts.

#### 3.2 Post-Meeting / Follow-up Agent
- **Why:** the **connective tissue**. Meeting Prep is the "before"; this is the "after".
  Writes back into the other agents, making the suite feel like one assistant.
- **Audience:** RMs, PMs, sales, project leads — everyone.
- **Data sources:** Calendar + Gmail (context), meeting notes/transcript (pasted, Drive
  Doc, or upload), CRM (write), Jira (write).
- **Tools:**
  - `get_meeting_context(event_id="", query="")` — reuses Calendar lookup.
  - `ingest_meeting_notes(source)` — pasted text, Drive/Docs file ID, or uploaded transcript.
  - `extract_action_items(notes)` → `[{owner, description, due_date, priority}]`.
  - `summarize_meeting(notes)` → decisions, risks, open questions, next steps.
  - `draft_followup_email(to, context)` — reuses Sales `draft_client_email` pattern.
  - `log_crm_interaction(customer, summary, outcome)` — write into CRM the Sales agent reads.
  - `create_jira_tasks(project_key, tasks)` — write into Jira the Project Mgmt agent reads.
- **Prompt behavior:** raw notes → summary + actions; **confirm before any write**;
  distinguish commitments SSIM made vs client actions.
- **Integration:** feeds Sales CRM, Project Mgmt Jira, and next-day Daily Briefing — a
  genuine closed loop.

#### 3.3 Investment Research / Market Intelligence
- **Why:** serves the PM/strategist audience currently underserved.
- **Audience:** PMs, investment strategists, RMs prepping for client questions.
- **Data sources:** market data (mock now, real feed later), internal research notes
  (Drive), fund holdings/exposures (mock), performance/attribution (mock), news (web
  search or mock).
- **Tools:**
  - `get_market_data(symbols_or_asset_class)` → quotes, moves, key levels.
  - `search_research_notes(query)` — internal Drive research library.
  - `get_fund_profile(fund_name)` → mandate, top holdings, sector/factor exposures.
  - `get_performance_attribution(fund_name, period)` → attribution breakdown (reusable in RFP).
  - `compare_to_benchmark(fund_name, benchmark)`.
  - `get_news_and_events(entity)` → recent, dated news items.
- **Prompt behavior:** synthesize + always cite; separate fact from house view; mark every
  number `[VERIFY]`; never give personalized investment advice (fiduciary context).
- **Integration:** feeds Meeting Prep (portfolio context), Sales (positioning), RFP
  (performance/attribution), Daily Briefing (richer market context).

### Tier 2 — rounds out "employee" (not just "client") assistant

#### 3.4 Client Reporting / Review-Pack Generator
- QBR & investment-committee decks from customer profile + attribution + products →
  Google Slides/Doc. Complements Sales + Meeting Prep + Research.

#### 3.5 Knowledge / Policy Q&A
- HR / IT / internal-wiki RAG ("how do I expense X", "PTO policy", "VPN setup"). The piece
  that makes this a genuine *employee* assistant, not just a sales toolkit.

### Tier 3 — quick wins / broadly applicable productivity
- **IT Helpdesk Agent** — password resets, access requests, common troubleshooting.
- **Expense & Travel Agent** — expense policy, report drafting, travel booking help.
- **New-Hire Onboarding Agent** — checklists, systems access, "who does what", first-week guide.

### Other ideas parked for later
- **Risk Monitoring Agent** — portfolio risk limits, breach alerts, stress-test summaries.
- **ESG / Stewardship Agent** — proxy-voting summaries, engagement tracking, ESG scoring
  (SSIM emphasizes ESG heavily; could be part of Research or standalone).
- **Client Onboarding / KYC Agent** — institutional client onboarding, KYC/AML doc collection.
- **General Document Drafting / Summarization Agent** — cross-cutting writing helper.

---

## 4. Bringing it together — UI / architecture

**Decision made:** custom **web app** front-end (React/Next calling Agent Engine),
maximum control over UX.

**Recommended entry pattern: Hybrid concierge (Option C).**
- **Daily Briefing = home dashboard** — the morning landing page.
- **Persistent concierge chat** = primary surface, backed by an **orchestrator/router
  agent** that classifies intent and delegates to the right specialist (ADK `sub_agents`
  or agent-as-tool).
- **Sidebar of capability cards + suggested prompts** for discovery.
- **Rich, structured outputs rendered as cards** — meeting brief card, compliance
  badge, action-item checklist, attribution table, doc/sheet links — NOT raw markdown.

**Alternatives considered:**
- Option A — App launcher (tiles), one chat per agent. Easy, discoverable, but feels like
  5 tools and user must self-route.
- Option B — Single concierge chat only. Feels like one assistant but weaker discovery of
  specialized capabilities.

**Surfaces considered:** custom web app (**chosen**), Google Agentspace (less frontend
work), ADK dev UI (dev-only).

---

## 5. Integration map

```
Meeting Prep ──► [meeting happens] ──► Post-Meeting ──┬──► CRM (Sales reads)
                                                       ├──► Jira (Project Mgmt reads)
                                                       └──► Daily Briefing (next day)

Research ──► feeds ──► Meeting Prep · Sales · RFP · Daily Briefing
Compliance ──► gates ──► RFP drafts · Sales proposals & emails
Orchestrator ──► routes user intent ──► any of the specialist agents
```

---

## 6. Technical considerations / principles

- **Structured JSON outputs** from tools so the web UI can render badges, checklists, and
  tables (not just paste markdown). Important for the custom-web-app surface.
- **Reuse existing patterns:** each new agent = own folder, `agent.py`, `mock_data.py`,
  mock fallbacks, `agent_engine_app.py`, tests, deployable to Agent Engine.
- **Shared conventions:** ADK system prompts must use `[VariableName]` not `{VariableName}`;
  Vertex `global` location; `gemini-2.0-flash-001` (or newer if now available).
- **Orchestrator agent** is a new top-level component that ties specialists together.
- **Write-back tools** (CRM, Jira, Gmail drafts) should always confirm before writing.
- **Cross-agent data contracts:** CRM and Jira mock schemas are shared read/write surfaces
  between agents — define these carefully.

---

## 7. Open questions / decisions for PRD

- Which agents are in scope for v1 vs later? (Proposal: v1 = orchestrator + 5 existing +
  Post-Meeting + Compliance; Research + Tier 2/3 later.)
- Auth / identity: how does the web app authenticate the employee and scope their
  Gmail/Calendar/Drive access? (Currently single dev account.)
- Real vs mock data timeline — which integrations go real first?
- Where do the planning docs and orchestrator live in the repo structure?
- Do we need a shared data/service layer (CRM, Jira) instead of per-agent mock files?
- Model version — confirm `gemini-2.0-flash-001` vs upgrading.
```
