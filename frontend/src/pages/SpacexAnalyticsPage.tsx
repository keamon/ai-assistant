import { useEffect, useState } from "react";
import type { SpacexAnalytics } from "../types";
import { api } from "../api";
import { renderRich } from "../richText";
import IndexedPriceChart from "../components/IndexedPriceChart";
import { downloadCaseStudyReport } from "../lib/caseStudyReportPdf";
import "../styles/spacex.css";

function SourceTag({ source }: { source?: "live" | "mock" }) {
  if (!source) return null;
  return <span className={`spx-source-tag ${source}`}>{source}</span>;
}

function pct(n?: number): string {
  if (typeof n !== "number") return "—";
  return `${n >= 0 ? "+" : ""}${n.toFixed(1)}%`;
}

function StatTile({
  label,
  value,
  tone,
  deltaPct,
  deltaSuffix,
}: {
  label: string;
  value: string;
  tone?: "pos" | "neg";
  deltaPct?: number;
  deltaSuffix?: string;
}) {
  const cls = tone ?? (deltaPct == null ? "" : deltaPct >= 0 ? "pos" : "neg");
  return (
    <div className="stat spx-stat">
      <div className="label">{label}</div>
      <div className={`value ${cls}`}>{value}</div>
      {deltaPct != null && (
        <div className="delta" style={{ color: cls === "neg" ? "var(--red)" : "var(--green)" }}>
          {pct(deltaPct)}
          {deltaSuffix}
        </div>
      )}
    </div>
  );
}

export default function SpacexAnalyticsPage() {
  const [data, setData] = useState<SpacexAnalytics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    api.spacexAnalytics().then(setData).catch((e) => setError(String(e)));
  }, []);

  const handleDownload = async () => {
    if (!data) return;
    setDownloading(true);
    try {
      await downloadCaseStudyReport(data);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="spx">
      <header className="spx-topbar">
        <div>
          <div className="brand">
            FinTechCo <span>·</span> Market Intelligence
          </div>
          <div className="sub">SpaceX (SPCX) — IPO &amp; index-inclusion impact analysis</div>
        </div>
        <div className="spacer" />
        <button className="btn-ghost" onClick={() => (window.location.href = "/")}>
          ← Back to Assistant
        </button>
        <button className="btn-ghost" onClick={handleDownload} disabled={!data || downloading}>
          {downloading ? "Preparing PDF…" : "Download PDF report ↓"}
        </button>
      </header>

      <main className="spx-main">
        {error && <div className="card card-pad empty">Failed to load: {error}</div>}
        {!data && !error && <div className="spin">Loading SpaceX analytics…</div>}

        {data && (
          <>
            <div className="card card-pad">
              <div className="section-title">
                Analyst narrative <SourceTag source={data.fred.source} />
              </div>
              <div className="spx-narrative">
                {data.narrative.split("\n\n").map((p, i) => (
                  <p key={i}>{renderRich(p)}</p>
                ))}
              </div>
            </div>

            <div className="spx-stat-grid">
              <StatTile label="IPO offer price" value={`$${data.metrics.ipo_price?.toFixed(0)}`} />
              <StatTile
                label={`Latest (${data.metrics.latest_date})`}
                value={`$${data.metrics.latest_price?.toFixed(2)}`}
                deltaPct={data.metrics.spcx_since_ipo_pct}
              />
              <StatTile
                label={`Peak (${data.metrics.peak_date})`}
                value={`$${data.metrics.peak_price?.toFixed(2)}`}
                deltaPct={data.metrics.spcx_from_peak_pct}
                deltaSuffix=" since peak"
              />
              <StatTile
                label={`${data.index_name} since IPO`}
                value={pct(data.metrics.ndx_since_ipo_date_pct)}
                tone={(data.metrics.ndx_since_ipo_date_pct ?? 0) >= 0 ? "pos" : "neg"}
              />
              <StatTile
                label="Excess return vs. index"
                value={pct(data.metrics.excess_return_since_ipo_pct)}
                tone={(data.metrics.excess_return_since_ipo_pct ?? 0) >= 0 ? "pos" : "neg"}
              />
            </div>

            <div className="card card-pad">
              <div className="section-title">
                SPCX vs. {data.index_name} — indexed to 100 at IPO
                <SourceTag source={data.prices.spcx.source} />
              </div>
              <IndexedPriceChart
                spcx={data.prices.spcx.prices}
                index={data.prices.index.prices}
                seriesALabel="SpaceX (SPCX)"
                indexLabel={data.index_name}
                markers={[
                  { date: data.metrics.first_close_date || "", label: "IPO" },
                  { date: "2026-07-06", label: `${data.index_name} inclusion` },
                ]}
              />
            </div>

            <div className="card card-pad">
              <div className="section-title">Timeline</div>
              <div className="spx-timeline">
                {data.timeline.map((ev) => (
                  <div className="spx-tl-item" key={ev.date + ev.label}>
                    <div className="spx-tl-rail">
                      <div className={`spx-tl-dot ${ev.kind}`} />
                      <div className="spx-tl-line" />
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

            <div className="card card-pad">
              <div className="section-title">
                Macro backdrop (FRED) <SourceTag source={data.fred.source} />
              </div>
              <div className="spx-stat-grid">
                {Object.entries(data.fred.series).map(([id, s]) => (
                  <div className="stat spx-stat" key={id}>
                    <div className="label">{s.label}</div>
                    <div className="value">{s.value.toFixed(2)}{s.units}</div>
                    <div className="delta muted">as of {s.date}</div>
                  </div>
                ))}
                <div className="stat spx-stat">
                  <div className="label">10Y–2Y yield curve</div>
                  <div className="value">{data.fred.yield_curve_10y2y >= 0 ? "+" : ""}{data.fred.yield_curve_10y2y.toFixed(2)}pp</div>
                  <div className="delta muted">{data.fred.yield_curve_10y2y >= 0 ? "normal" : "inverted"}</div>
                </div>
              </div>
            </div>

            <div className="card card-pad">
              <div className="section-title">
                SEC EDGAR filings <SourceTag source={data.filings.source} />
              </div>
              <div className="spx-filings">
                {data.filings.filings.map((f) => (
                  <div className="spx-filing" key={f.accession || f.form + f.filed}>
                    <span className="spx-filing-form">{f.form}</span>
                    <span className="spx-filing-date">{f.filed}</span>
                    <span className="spx-filing-desc">{f.description}</span>
                    {f.url && <a href={f.url} target="_blank" rel="noreferrer">View ↗</a>}
                  </div>
                ))}
              </div>
            </div>

            <div className="card card-pad">
              <div className="section-title">Impact on bank operations</div>
              <div className="spx-impact-grid">
                {data.bank_impact.map((section) => (
                  <div className="spx-impact-card" key={section.title}>
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
