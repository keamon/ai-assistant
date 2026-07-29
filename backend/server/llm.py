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
LLM generation helpers for the SSIM assistant demo: a morning-briefing narrative
and per-meeting prep + talking points. Uses gemini-3.5-flash on Vertex (us).
Callers cache the results in the store; every function degrades gracefully to
composed text if Vertex is unavailable.
"""

import json

_MODEL = "gemini-3.5-flash"
_client = None


def _get_client():
    global _client
    if _client is None:
        import google.auth
        from google import genai

        _, project = google.auth.default()
        _client = genai.Client(vertexai=True, project=project, location="us")
    return _client


def _generate(prompt: str) -> str:
    resp = _get_client().models.generate_content(model=_MODEL, contents=prompt)
    return (resp.text or "").strip()


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
    tpv = (market.get("ssim_payments_banking_snapshot", {}) or {}).get("total_tpv", "")
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
    rel = profile.get("ssim_relationship", {}) or {}
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
Relationship: {rel.get('status','')}, {rel.get('ssim_aum','')} with FinTechCo, strategies: {', '.join(rel.get('strategies', []))}
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
