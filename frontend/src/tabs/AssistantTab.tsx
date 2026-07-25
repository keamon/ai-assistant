import { useEffect, useRef, useState } from "react";
import type { Briefing, MeetingPrep, Suggestion, PublicCompanyWatch } from "../types";
import { api } from "../api";
import DocModal from "../components/DocModal";
import ScheduleModal, { type ScheduleInitial } from "../components/ScheduleModal";
import { renderRich } from "../richText";

function fmtPct(n?: number): string {
  if (typeof n !== "number") return "";
  return `${n >= 0 ? "+" : ""}${n.toFixed(2)}%`;
}

function moveClass(n?: number): string {
  if (typeof n !== "number" || n === 0) return "flat";
  return n > 0 ? "up" : "down";
}

function fmtTime(iso?: string): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
}

function fmtDate(iso?: string): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return "";
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function addMinutes(hhmm: string, mins: number): string {
  const [h, m] = hhmm.split(":").map(Number);
  const total = h * 60 + m + mins;
  return `${String(Math.floor(total / 60) % 24).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`;
}

function MeetingRow({
  ev,
  onOpenDoc,
  showDate,
  refreshKey,
}: {
  ev: Briefing["events"][number];
  onOpenDoc: (id: string) => void;
  showDate?: boolean;
  refreshKey: number;
}) {
  const [open, setOpen] = useState(false);
  const [prep, setPrep] = useState<MeetingPrep | null>(null);
  const [loading, setLoading] = useState(false);
  const isFirstRender = useRef(true);

  const toggle = async () => {
    const next = !open;
    setOpen(next);
    if (next && !prep) {
      setLoading(true);
      try {
        setPrep(await api.prep(ev.id));
      } finally {
        setLoading(false);
      }
    }
  };

  // Re-fetch prep after any assistant action (e.g. a room booking) so an
  // already-open meeting card picks up the new room; invalidate it while
  // closed so the next open fetches fresh instead of showing stale data.
  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    if (open) {
      api.prep(ev.id).then(setPrep).catch(() => {});
    } else {
      setPrep(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshKey]);

  const type = ev.meeting_type || "internal";
  return (
    <div className="meeting">
      <div className="meeting-head" onClick={toggle}>
        <span className="time">{showDate ? `${fmtDate(ev.start)} · ${fmtTime(ev.start)}` : fmtTime(ev.start)}</span>
        <span className="title">{ev.title}</span>
        <span className={`badge ${type}`}>{type}</span>
        <span className="chev">{open ? "▲ prep" : "▼ prep"}</span>
      </div>
      {open && (
        <div className="meeting-body">
          {loading && <div className="spin">Preparing your brief & talking points…</div>}
          {prep && !prep.error && (
            <>
              {prep.objective && (
                <div className="prep-block">
                  <h4>Objective</h4>
                  <p className="small">{prep.objective}</p>
                </div>
              )}

              {!!prep.agenda?.length && (
                <div className="prep-block">
                  <h4>Suggested agenda</h4>
                  <ol className="prep-list">
                    {prep.agenda.map((a, i) => <li key={i}>{a}</li>)}
                  </ol>
                </div>
              )}

              {!!prep.talking_points?.length && (
                <div className="prep-block">
                  <h4>Talking points</h4>
                  <ul className="prep-list">
                    {prep.talking_points.map((t, i) => <li key={i}>{t}</li>)}
                  </ul>
                </div>
              )}

              {!!prep.anticipated_questions?.length && (
                <div className="prep-block">
                  <h4>Anticipated questions</h4>
                  <div className="qa-list">
                    {prep.anticipated_questions.map((q, i) => (
                      <div className="qa-item" key={i}>
                        <p className="qa-q">Q: {q.question}</p>
                        {q.answer && <p className="qa-a">A: {q.answer}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="prep-block">
                <h4>Details</h4>
                <div className="kv">
                  <span className="k">When</span>
                  <span>{fmtTime(prep.meeting.start)} – {fmtTime(prep.meeting.end)} · {prep.meeting.location || "—"}</span>
                  <span className="k">Attendees</span>
                  <span className="row wrap">
                    {prep.meeting.attendees.map((a) => <span className="chip" key={a}>{a}</span>)}
                  </span>
                </div>
              </div>

              {prep.customer_profile && (
                <div className="prep-block">
                  <h4>Client profile</h4>
                  <div className="kv">
                    <span className="k">Account</span>
                    <span>{prep.customer_profile.full_name || prep.customer_profile.name} · {prep.customer_profile.type}</span>
                    <span className="k">Relationship</span>
                    <span>{prep.customer_profile.ssim_relationship?.status} · {prep.customer_profile.ssim_relationship?.ssim_aum} with SSIM</span>
                    <span className="k">Key concerns</span>
                    <span>{(prep.customer_profile.investment_profile?.key_concerns || []).join(", ")}</span>
                  </div>
                </div>
              )}

              {(prep.stock_snapshot || prep.latest_filing) && (
                <div className="prep-block">
                  <h4>Market snapshot</h4>
                  {prep.stock_snapshot?.quote && (
                    <div className="kv">
                      <span className="k">Share price</span>
                      <span>
                        {typeof prep.stock_snapshot.quote.price === "number"
                          ? `$${prep.stock_snapshot.quote.price.toFixed(2)}`
                          : "—"}{" "}
                        <span className={`watch-move ${moveClass(prep.stock_snapshot.quote.change_pct)}`}>
                          {fmtPct(prep.stock_snapshot.quote.change_pct)}
                        </span>
                      </span>
                      {prep.stock_snapshot.next_earnings_date && (
                        <>
                          <span className="k">Next earnings</span>
                          <span>{prep.stock_snapshot.next_earnings_date}</span>
                        </>
                      )}
                    </div>
                  )}
                  {prep.latest_filing?.form && (
                    <p className="small" style={{ marginTop: 6 }}>
                      Latest SEC filing:{" "}
                      {prep.latest_filing.url ? (
                        <a href={prep.latest_filing.url} target="_blank" rel="noreferrer">
                          {prep.latest_filing.form} · filed {prep.latest_filing.filed}
                        </a>
                      ) : (
                        `${prep.latest_filing.form} · filed ${prep.latest_filing.filed}`
                      )}
                    </p>
                  )}
                </div>
              )}

              {prep.recent_emails.length > 0 && (
                <div className="prep-block">
                  <h4>Recent communications</h4>
                  <div className="stack">
                    {prep.recent_emails.slice(0, 4).map((e) => (
                      <div key={e.id} className="small">
                        <strong>{e.subject}</strong>
                        <div className="muted">{e.from}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {prep.related_documents.length > 0 && (
                <div className="prep-block">
                  <h4>Documents</h4>
                  <div className="stack">
                    {prep.related_documents.map((d) => (
                      <button key={d.id} className="doc-btn" onClick={() => onOpenDoc(d.id)}>
                        📄 {d.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
          {prep?.error && <div className="empty">No prep available.</div>}
        </div>
      )}
    </div>
  );
}

function SuggestionRow({ s, onSchedule }: { s: Suggestion; onSchedule: (init: ScheduleInitial) => void }) {
  return (
    <div className="suggestion">
      <div className="row" style={{ justifyContent: "space-between" }}>
        <span className="title">{s.title}</span>
        <span className={`badge ${s.priority}`}>{s.priority}</span>
      </div>
      <div className="why">{s.rationale}</div>
      <div className="row wrap" style={{ justifyContent: "space-between" }}>
        <span className="small muted">
          {s.suggested_date} · {s.suggested_duration_min} min · {s.suggested_attendees.length} attendees
        </span>
        <button
          className="btn"
          onClick={() =>
            onSchedule({
              title: s.title,
              attendees: s.suggested_attendees,
              date: s.suggested_date,
              start_time: "14:00",
              end_time: addMinutes("14:00", s.suggested_duration_min),
            })
          }
        >
          Schedule
        </button>
      </div>
    </div>
  );
}

function MarketWatchCard({ rows }: { rows: PublicCompanyWatch[] }) {
  if (!rows.length) return null;
  return (
    <div className="card card-pad mt">
      <div className="section-title">Customer market watch · public-company clients</div>
      <div className="watch-grid">
        {rows.map((w) => (
          <div className="watch-item" key={w.ticker}>
            <div className="watch-head">
              <span className="watch-name">{w.name}</span>
              <span className="watch-ticker">
                {w.exchange ? `${w.exchange}: ` : ""}{w.ticker}
              </span>
            </div>
            <div className="watch-price-row">
              <span className="watch-price">
                {typeof w.price === "number" ? `$${w.price.toFixed(2)}` : "—"}
              </span>
              <span className={`watch-move ${moveClass(w.change_pct)}`}>
                {fmtPct(w.change_pct)}
              </span>
            </div>
            <div className="watch-meta small muted">
              {w.next_earnings_date && <span>Earnings {w.next_earnings_date}</span>}
              {w.latest_filing?.form && (
                <span>
                  {" · "}
                  {w.latest_filing.url ? (
                    <a href={w.latest_filing.url} target="_blank" rel="noreferrer">
                      {w.latest_filing.form} · {w.latest_filing.filed}
                    </a>
                  ) : (
                    `${w.latest_filing.form} · ${w.latest_filing.filed}`
                  )}
                </span>
              )}
            </div>
            {w.headline && <div className="watch-news small">📰 {w.headline}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function AssistantTab({ refreshKey, onAction }: { refreshKey: number; onAction: () => void }) {
  const [b, setB] = useState<Briefing | null>(null);
  const [docId, setDocId] = useState<string | null>(null);
  const [scheduleInit, setScheduleInit] = useState<ScheduleInitial | null>(null);

  useEffect(() => {
    api.briefing().then(setB).catch(() => {});
  }, [refreshKey]);

  if (!b) return <div className="spin">Loading your briefing…</div>;
  const tpv = b.market?.ssim_payments_banking_snapshot?.total_tpv || "$11.2B";

  return (
    <div>
      <div className="stat-row">
        <div className="stat">
          <div className="label">Payment Volume (Yesterday)</div>
          <div className="value">{tpv}</div>
          <div className="delta">{b.market?.ssim_payments_banking_snapshot?.tpv_change_dod || ""}</div>
        </div>
        <div className="stat">
          <div className="label">Meetings today</div>
          <div className="value">{b.events.length}</div>
        </div>
        <div className="stat">
          <div className="label">Priority emails</div>
          <div className="value">{b.priority_emails.length}</div>
        </div>
        <div className="stat">
          <div className="label">To schedule</div>
          <div className="value">{b.suggestions.length}</div>
        </div>
      </div>

      {/* Auto-generated daily briefing */}
      <div className="card card-pad briefing-card">
        <div className="section-title">Daily briefing</div>
        {b.narrative ? (
          <p className="briefing-text">{renderRich(b.narrative)}</p>
        ) : (
          <div className="small muted">Generating your briefing…</div>
        )}
      </div>

      {b.public_company_watch && <MarketWatchCard rows={b.public_company_watch} />}

      <div className="card card-pad mt">
        <div className="section-title">Today's schedule · click a meeting for prep & talking points</div>
        <div className="stack">
          {b.events.map((ev) => (
            <MeetingRow key={ev.id} ev={ev} onOpenDoc={setDocId} refreshKey={refreshKey} />
          ))}
        </div>
      </div>

      <div className="card card-pad mt">
        <div className="section-title">Upcoming meetings</div>
        {b.upcoming_events.length === 0 ? (
          <div className="empty">Nothing scheduled beyond today.</div>
        ) : (
          <div className="stack">
            {b.upcoming_events.map((ev) => (
              <MeetingRow key={ev.id} ev={ev} onOpenDoc={setDocId} showDate refreshKey={refreshKey} />
            ))}
          </div>
        )}
      </div>

      <div className="card card-pad mt">
        <div className="section-title">Suggested meetings to schedule</div>
        {b.suggestions.length === 0 ? (
          <div className="empty">Nothing to schedule — you're all set.</div>
        ) : (
          <div className="stack">
            {b.suggestions.map((s) => (
              <SuggestionRow key={s.id} s={s} onSchedule={setScheduleInit} />
            ))}
          </div>
        )}
      </div>

      {docId && <DocModal docId={docId} onClose={() => setDocId(null)} />}
      {scheduleInit && (
        <ScheduleModal
          initial={scheduleInit}
          onClose={() => setScheduleInit(null)}
          onScheduled={onAction}
        />
      )}
    </div>
  );
}
