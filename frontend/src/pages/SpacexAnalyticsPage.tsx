import { useEffect, useState } from "react";
import type { SpacexAnalytics } from "../types";
import { api } from "../api";
import { renderRich } from "../richText";
import IndexedPriceChart from "../components/IndexedPriceChart";
import { downloadCaseStudyReport } from "../lib/caseStudyReportPdf";
import "../styles/spacex.css";

function fmtUsd(n?: number | null): string {
  return typeof n === "number" ? `$${n.toFixed(2)}` : "—";
}

function fmtPct(n?: number | null): string {
  if (typeof n !== "number") return "—";
  return `${n >= 0 ? "+" : ""}${n.toFixed(1)}%`;
}

function pctClass(n?: number | null): string {
  if (typeof n !== "number") return "";
  return n >= 0 ? "pos" : "neg";
}

function SourceTag({ source }: { source?: "live" | "mock" }) {
  if (!source) return null;
  return <span className={`spx-source-tag ${source}`}>{source}</span>;
}

export default function SpacexAnalyticsPage() {
  const [data, setData] = useState<SpacexAnalytics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    api.spacexAnalytics().then(setData).catch(() => setError("Failed to load the SpaceX analytics dashboard."));
  }, []);

  const handleDownload = async () => {
    if (!data) return;
    setDownloading(true);
    try {
      await downloadCaseStudyReport({ ...data, generated_at: new Date().toISOString() });
    } finally {
      setDownloading(false);
    }
  };

  const m = data?.metrics;
  const markers = data
    ? [
        { date: data.ipo_date, label: "IPO" },
        { date: data.inclusion_date, label: "Index incl." },
      ]
    : [];

  return (
    <div className="spx">
      <div className="spx-topbar">
        <div>
          <div className="brand">
            FinTechCo <span>·</span> Market Intelligence
          </div>
          <div className="sub">
            {data ? `${data.company} (${data.ticker}) — IPO & ${data.index_name} inclusion impact analysis` : "SpaceX index-inclusion analytics"}
          </div>
        </div>
        <div className="spacer" />
        <button className="btn-ghost" onClick={handleDownload} disabled={!data || downloading}>
          {downloading ? "Generating…" : "Download PDF report ⬇"}
        </button>
      </div>

      <main className="spx-main">
        {error && <div className="card card-pad">{error}</div>}
        {!data && !error && <div className="card card-pad">Loading…</div>}

        {data && (
          <>
            <div className="spx-stat-grid">
              <div className="stat spx-stat">
                <div className="label">IPO offer price</div>
                <div className="value">{fmtUsd(m?.ipo_price)}</div>
                <div className="delta">{data.ipo_date}</div>
              </div>
              <div className="stat spx-stat">
                <div className="label">Latest price</div>
                <div className={`value ${pctClass(m?.spcx_since_ipo_pct)}`}>{fmtUsd(m?.latest_price)}</div>
                <div className="delta">{fmtPct(m?.spcx_since_ipo_pct)} vs. offer · {m?.latest_date}</div>
              </div>
              <div className="stat spx-stat">
                <div className="label">Post-IPO peak</div>
                <div className="value">{fmtUsd(m?.peak_price)}</div>
                <div className="delta">{m?.peak_date}</div>
              </div>
              <div className="stat spx-stat">
                <div className="label">Excess return vs. {data.index_name}</div>
                <div className={`value ${pctClass(m?.excess_return_since_ipo_pct)}`}>{fmtPct(m?.excess_return_since_ipo_pct)}</div>
                <div className="delta">since IPO</div>
              </div>
            </div>

            <div className="card card-pad">
              <div className="section-title">
                Analyst narrative <SourceTag source="live" />
              </div>
              <div className="spx-narrative">
                {data.narrative.split("\n\n").map((p, i) => (
                  <p key={i}>{renderRich(p)}</p>
                ))}
              </div>
            </div>

            <div className="card card-pad">
              <div className="section-title">
                {data.ticker} vs. {data.index_name} — indexed to 100 at IPO <SourceTag source={data.prices.spcx.source} />
              </div>
              <IndexedPriceChart
                spcx={data.prices.spcx.prices}
                index={data.prices.index.prices}
                seriesALabel={data.ticker}
                indexLabel={data.index_name}
                markers={markers}
              />
            </div>

            <div className="card card-pad">
              <div className="section-title">Key insights</div>
              <ul className="spx-impact-card" style={{ border: "none", padding: 0, background: "none" }}>
                {data.insights.map((ins, i) => (
                  <li key={i}>{ins}</li>
                ))}
              </ul>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: 14 }} className="mt">
              <div className="card card-pad">
                <div className="section-title">Timeline</div>
                <div className="spx-timeline">
                  {data.timeline.map((ev, i) => (
                    <div key={ev.date + ev.label} className="spx-tl-item">
                      <div className="spx-tl-rail">
                        <div className={`spx-tl-dot ${ev.kind}`} />
                        {i < data.timeline.length - 1 && <div className="spx-tl-line" />}
                      </div>
                      <div className="spx-tl-body">
                        <div className="spx-tl-date">{ev.date}</div>
                        <div className="spx-tl-label">{ev.label}</div>
                        <div className="spx-tl-detail">{ev.detail}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="stack">
                <div className="card card-pad">
                  <div className="section-title">
                    Macro backdrop (FRED) <SourceTag source={data.fred.source} />
                  </div>
                  <div className="stack" style={{ gap: 8 }}>
                    {Object.entries(data.fred.series).map(([id, s]) => (
                      <div key={id} className="row" style={{ justifyContent: "space-between" }}>
                        <span className="small muted">{s.label}</span>
                        <strong className="small">
                          {s.value.toFixed(2)}
                          {s.units} <span className="muted">({s.date})</span>
                        </strong>
                      </div>
                    ))}
                    <div className="row" style={{ justifyContent: "space-between" }}>
                      <span className="small muted">10Y–2Y yield curve</span>
                      <strong className="small">
                        {data.fred.yield_curve_10y2y >= 0 ? "+" : ""}
                        {data.fred.yield_curve_10y2y.toFixed(2)}pp
                      </strong>
                    </div>
                  </div>
                </div>

                <div className="card card-pad">
                  <div className="section-title">
                    SEC EDGAR filings <SourceTag source={data.filings.source} />
                  </div>
                  <div className="spx-filings">
                    {data.filings.filings.map((f) => (
                      <div key={f.accession || f.form + f.filed} className="spx-filing">
                        <span className="spx-filing-form">{f.form}</span>
                        <span className="spx-filing-date">{f.filed}</span>
                        <span className="spx-filing-desc">
                          {f.description || f.form}
                          {f.url && (
                            <>
                              {" "}
                              <a href={f.url} target="_blank" rel="noreferrer">
                                view ↗
                              </a>
                            </>
                          )}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="card card-pad">
              <div className="section-title">Impact on bank operations</div>
              <div className="spx-impact-grid">
                {data.bank_impact.map((section) => (
                  <div key={section.title} className="spx-impact-card">
                    <h4>{section.title}</h4>
                    <ul>
                      {section.points.map((p, i) => (
                        <li key={i}>{p}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
