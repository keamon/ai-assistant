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
LLM generation helpers for the FinTechCo assistant demo: a morning-briefing narrative
and per-meeting prep + talking points. Uses Claude Haiku 4.5 via the Anthropic API.
Callers cache the results in the store; every function degrades gracefully to
composed text if the Anthropic API is unavailable.
"""

import json
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass

_MODEL = "claude-haiku-4-5-20251001"
_client = None


def _get_client():
    global _client
    if _client is None:
        import anthropic

        _client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    return _client


def _generate(prompt: str) -> str:
    resp = _get_client().messages.create(
        model=_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return (resp.content[0].text or "").strip()


def _extract_json(text: str):
    """Best-effort parse of a JSON object from a model response."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        return json.loads(text[start : end + 1])
    return json.loads(text)


# ─── Briefing narrative ─────────────────────────────────────────────────────

def generate_briefing_narrative(summary: dict) -> str:
    """Concise morning-briefing prose from the structured briefing summary."""
    events = [
        f"- {e.get('title')} ({e.get('meeting_type')})" for e in summary.get("events", [])
    ]
    emails = [f"- {e.get('subject')}" for e in summary.get("priority_emails", [])[:5]]
    suggestions = [f"- {s.get('title')}" for s in summary.get("suggestions", [])]
    market = summary.get("market", {}) or {}
    tpv = (market.get("fintechco_payments_banking_snapshot", {}) or {}).get("total_tpv", "")
    # Public-company customer intelligence (SEC filings + market snapshot) for context.
    watch_lines = []
    for w in summary.get("public_company_watch", []) or []:
        bits = [f"{w.get('name')} ({w.get('ticker')})"]
        price, chg = w.get("price"), w.get("change_pct")
        if price is not None:
            move = f" {chg:+.2f}%" if isinstance(chg, (int, float)) else ""
            bits.append(f"${price}{move}")
        if w.get("next_earnings_date"):
            bits.append(f"earnings {w['next_earnings_date']}")
        lf = w.get("latest_filing") or {}
        if lf.get("form"):
            bits.append(f"latest {lf['form']} filed {lf.get('filed','')}")
        watch_lines.append("- " + ", ".join(bits))
    prompt = f"""You are the FinTechCo Daily Briefing agent for a FinTechCo
professional at a digital payment services company with a commercial banking division. Write a
crisp morning briefing (120-160 words, first person addressed to "you", markdown with short bold
lead-ins, no title header). Do NOT open with a greeting such as "Good morning" — start directly
with the substance of the day. Cover: the shape of the day, the most important customer meetings,
the top 2-3 priority actions from emails, any payments/risk note, and — when relevant — a brief
**market watch** line on public-company customers with earnings this week or a notable recent
filing. Be specific and professional; no filler.

Date: {summary.get('date')}
Yesterday's total payment volume (TPV): {tpv}
Today's meetings:
{chr(10).join(events) or '- none'}
Priority emails:
{chr(10).join(emails) or '- none'}
Meetings that should be scheduled:
{chr(10).join(suggestions) or '- none'}
Public-company customer watch (price, next earnings, latest SEC filing):
{chr(10).join(watch_lines) or '- none'}
"""
    try:
        return _generate(prompt)
    except Exception:
        # Composed fallback
        n_cust = sum(1 for e in summary.get("events", []) if e.get("meeting_type") == "customer")
        return (
            f"**You have {len(summary.get('events', []))} meetings** today"
            f"{f' ({n_cust} customer)' if n_cust else ''}, "
            f"**{len(summary.get('priority_emails', []))} priority emails**, and "
            f"**{len(summary.get('suggestions', []))} meetings to schedule**. "
            "Open a meeting below for its full prep brief and talking points."
        )


# ─── Meeting prep + talking points ──────────────────────────────────────────

def _normalize_qa(q) -> dict:
    """Coerce a model-returned anticipated-question entry into {question, answer}."""
    if isinstance(q, dict):
        return {
            "question": str(q.get("question") or q.get("q") or ""),
            "answer": str(q.get("answer") or q.get("a") or ""),
        }
    text = str(q)
    for sep in (" — ", " - "):
        if sep in text:
            question, answer = text.split(sep, 1)
            return {"question": question.strip(), "answer": answer.strip()}
    return {"question": text, "answer": ""}


def generate_meeting_prep(prep: dict) -> dict:
    """Return {objective, agenda[], talking_points[], anticipated_questions[]} for a meeting."""
    m = prep.get("meeting", {})
    profile = prep.get("customer_profile") or {}
    emails = [f"- {e.get('subject')}: {e.get('snippet','')[:140]}" for e in prep.get("recent_emails", [])[:4]]
    docs = [f"- {d.get('name')}" for d in prep.get("related_documents", [])]
    inv = profile.get("investment_profile", {}) or {}
    rel = profile.get("fintechco_relationship", {}) or {}
    prompt = f"""You are the FinTechCo Meeting Prep agent. Prepare a meeting brief for a FinTechCo
professional. Return ONLY JSON with keys:
  "objective": string (one sentence),
  "agenda": array of 3-5 short strings,
  "talking_points": array of 4-6 specific, data-driven strings the FinTechCo person should make,
  "anticipated_questions": array of 2-4 objects {{"question": string, "answer": string}} —
    likely client/attendee questions with a short suggested answer.

Meeting: {m.get('title')} ({m.get('meeting_type')})
When: {m.get('start')} – {m.get('end')} · {m.get('location','')}
Attendees: {', '.join(m.get('attendees', []))}
Description: {m.get('description','')}
Client: {profile.get('full_name') or profile.get('name') or 'n/a'} — {profile.get('type','')}
Relationship: {rel.get('status','')}, {rel.get('fintechco_aum','')} with FinTechCo, strategies: {', '.join(rel.get('strategies', []))}
Key client concerns: {', '.join(inv.get('key_concerns', []))}
Recent emails:
{chr(10).join(emails) or '- none'}
Relevant documents:
{chr(10).join(docs) or '- none'}
"""
    try:
        data = _extract_json(_generate(prompt))
        return {
            "objective": str(data.get("objective", "")),
            "agenda": list(data.get("agenda", []) or []),
            "talking_points": list(data.get("talking_points", []) or []),
            "anticipated_questions": [
                _normalize_qa(q) for q in (data.get("anticipated_questions", []) or [])
            ],
        }
    except Exception:
        # Composed fallback from structured data
        return {
            "objective": f"Prepare for {m.get('title','the meeting')}.",
            "agenda": ["Introductions", "Review of key items", "Discussion", "Next steps"],
            "talking_points": (
                [f"Address client concern: {c}" for c in inv.get("key_concerns", [])[:4]]
                or ["Confirm objectives and desired outcomes for the meeting."]
            ),
            "anticipated_questions": [
                {"question": "What are next steps and timelines?", "answer": "Confirm owners and dates before close."},
            ],
        }


# ─── SpaceX index-inclusion case study narrative ────────────────────────────

def generate_spacex_narrative(payload: dict) -> str:
    """2-3 paragraph analyst narrative for the SpaceX index-inclusion dashboard.

    Degrades to ``payload["insights"]`` (joined into prose) if the Anthropic
    model is unavailable — a graceful-LLM-degradation fallback, not a
    live-market-data mock, so it's unaffected by the "No mock data" policy.
    Every concrete dollar figure the prompt might need is passed explicitly
    (an LLM asked to discuss IPO size without the real raise amount will
    invent one), and a leading ``#``-prefixed line is stripped defensively —
    "no title header" in the prompt doesn't reliably stop the model from
    adding one, and the frontend's renderRich() doesn't support headings.
    """
    m = payload.get("metrics", {})
    insights = payload.get("insights", [])
    prompt = f"""You are a market-intelligence analyst at FinTechCo, a digital payments company
with a commercial banking division, writing for internal bankers who need to understand a
newsworthy IPO and index-inclusion event. Use ONLY the facts given below — do not invent or
estimate any dollar figure, percentage, or date that isn't provided.

Facts:
- Company: SpaceX (NASDAQ: {payload.get('ticker')}), CIK {payload.get('cik')}
- IPO date: {payload.get('ipo_date')}; offer price ${m.get('ipo_price')}
- IPO raise: {payload.get('ipo_raise')}; implied valuation: {payload.get('ipo_valuation')}
- First-day close: ${m.get('first_close')} on {m.get('first_close_date')}
- Peak price: ${m.get('peak_price')} on {m.get('peak_date')}
- Latest price: ${m.get('latest_price')} on {m.get('latest_date')} ({m.get('spcx_since_ipo_pct')}% vs. offer price)
- {payload.get('index_name')} fast-track inclusion date: {payload.get('inclusion_date')}
- {payload.get('index_name')} return over the same period since IPO: {m.get('ndx_since_ipo_date_pct')}%
- SPCX excess return vs. the index since IPO: {m.get('excess_return_since_ipo_pct')} percentage points

Write a 2-3 paragraph narrative (150-220 words) covering: the IPO and its size, the fast-tracked
index inclusion and what drove it, and what the price action since implies about index-fund-driven
demand. Do NOT include a title, heading, or '#'/'##' line of any kind before it — start directly
with the first sentence of the narrative.
"""
    try:
        text = _generate(prompt)
        lines = text.split("\n")
        while lines and lines[0].strip().startswith("#"):
            lines.pop(0)
        cleaned = "\n".join(lines).strip()
        return cleaned or " ".join(insights)
    except Exception:
        return " ".join(insights)
