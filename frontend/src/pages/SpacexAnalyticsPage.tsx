import { useEffect, useState } from "react";
import type { SpacexAnalytics } from "../types";
import { api } from "../api";
import { renderRich } from "../richText";
import IndexedPriceChart from "../components/IndexedPriceChart";
import { downloadCaseStudyReport, type CaseStudyReport } from "../lib/caseStudyReportPdf";
import "../styles/spacex.css";

function fmtPct(n?: number): string {
  if (typeof n !== "number") return "n/a";
  return `${n >= 0 ? "+" : ""}${n.toFixed(1)}%`;
}

function fmtUsd(n?: number, digits = 2): string {
  return typeof n === "number" ? `$${n.toFixed(digits)}` : "n/a";
}

function buildReport(data: SpacexAnalytics): CaseStudyReport {
  return {
    generated_at: new Date().toISOString(),
    company: data.company,
    ticker: data.ticker,
    index_name: data.index_name,
    index_ticker: data.index_ticker,
    timeline: data.timeline,
    prices: data.prices,
    metrics: data.metrics,
    insights: data.insights,
    filings: data.filings,
    fred: data.fred,
    bank_impact: data.bank_impact,
    narrative: data.narrative,
  };
}

export default function SpacexAnalyticsPage() {
  const [data, setData] = useState<SpacexAnalytics | null>(null);
  const [error, setError] = useState(false);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    api.spacexAnalytics().then(setData).catch(() => setError(true));
  }, []);

  const handleDownload = async () => {
    if (!data) return;
    setDownloading(true);
    try {
      await downloadCaseStudyReport(buildReport(data));
    } finally {
      setDownloading(false);
    }
  };

  const m = data?.metrics;
  const markers =
    m?.ipo_date && m?.inclusion_date
      ? [
          { date: m.ipo_date, label: "IPO" },
          { date: m.inclusion_date, label: `${data!.index_name} incl.` },
        ]
      : [];

  return (
    <div className="spx">
      <div className="spx-topbar">
        <div>
          <div className="brand">
            FinTechCo <span>·</span> SpaceX Analysis
          </div>
          <div className="sub">
            {data ? `${data.company} (${data.ticker}) — IPO & ${data.index_name} inclusion impact analysis`
                  : "IPO & index-inclusion impact analysis"}
          </div>
        </div>
        <div className="spacer" />
        <button className="btn-ghost" onClick={handleDownload} disabled={!data || downloading}>
          {downloading ? "Preparing PDF…" : "Download PDF report ↓"}
        </button>
      </div>

      <div className="spx-main">
        {error && <div className="card card-pad">Could not load the SpaceX analytics dashboard.</div>}
        {!data && !error && <div className="card card-pad">Loading SpaceX analytics…</div>}

        {data && m && (
          <>
            <section className="card card-pad">
              <div className="section-title">Key metrics</div>
              <div className="spx-stat-grid">
                <div className="stat spx-stat">
                  <div className="label">IPO price</div>
                  <div className="value">{fmtUsd(m.ipo_price, 0)}</div>
                  <div className="delta">{m.ipo_date}</div>
                </div>
                <div className="stat spx-stat">
                  <div className="label">Latest price</div>
                  <div className={`value ${(m.spcx_since_ipo_pct ?? 0) >= 0 ? "pos" : "neg"}`}>
                    {fmtUsd(m.latest_price)}
                  </div>
                  <div className="delta">{fmtPct(m.spcx_since_ipo_pct)} since IPO</div>
                </div>
                <div className="stat spx-stat">
                  <div className="label">Peak price</div>
                  <div className="value">{fmtUsd(m.peak_price)}</div>
                  <div className="delta">{m.peak_date} · {fmtPct(m.drawdown_from_peak_pct)} off peak</div>
                </div>
                <div className="stat spx-stat">
                  <div className="label">{data.index_name} return since IPO</div>
                  <div className={`value ${(m.ndx_since_ipo_date_pct ?? 0) >= 0 ? "pos" : "neg"}`}>
                    {fmtPct(m.ndx_since_ipo_date_pct)}
                  </div>
                </div>
                <div className="stat spx-stat">
                  <div className="label">Excess return vs. index</div>
                  <div className={`value ${(m.excess_return_since_ipo_pct ?? 0) >= 0 ? "pos" : "neg"}`}>
                    {fmtPct(m.excess_return_since_ipo_pct)}
                  </div>
                  <div className="delta">since inclusion {fmtPct(m.since_inclusion_pct)}</div>
                </div>
              </div>
            </section>

            <section className="card card-pad">
              <div className="section-title">
                {data.ticker} vs. {data.index_name} — indexed to 100 at IPO
                <span className={`spx-source-tag ${data.prices.spcx.source}`}>{data.prices.spcx.source}</span>
              </div>
              <IndexedPriceChart
                spcx={data.prices.spcx.prices}
                index={data.prices.index.prices}
                seriesALabel={data.ticker}
                indexLabel={data.index_name}
                markers={markers}
              />
            </section>

            <section className="card card-pad">
              <div className="section-title">Analyst narrative</div>
              <div className="spx-narrative">
                {data.narrative.split("\n\n").map((para, i) => (
                  <p key={i}>{renderRich(para)}</p>
                ))}
              </div>
            </section>

            <section className="card card-pad">
              <div className="section-title">Timeline</div>
              <div className="spx-timeline">
                {data.timeline.map((ev) => (
                  <div className="spx-tl-item" key={`${ev.date}-${ev.label}`}>
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
            </section>

            <section className="card card-pad">
              <div className="section-title">
                Macro backdrop (FRED)
                <span className={`spx-source-tag ${data.fred.source}`}>{data.fred.source}</span>
              </div>
              <div className="spx-stat-grid">
                {Object.entries(data.fred.series).map(([id, s]) => (
                  <div className="stat" key={id}>
                    <div className="label">{s.label}</div>
                    <div className="value">{s.value}{s.units}</div>
                    <div className="delta">as of {s.date}</div>
                  </div>
                ))}
                <div className="stat">
                  <div className="label">10Y–2Y yield curve</div>
                  <div className="value">{fmtPct(data.fred.yield_curve_10y2y)}</div>
                </div>
              </div>
            </section>

            <section className="card card-pad">
              <div className="section-title">
                SEC EDGAR filings
                <span className={`spx-source-tag ${data.filings.source}`}>{data.filings.source}</span>
              </div>
              <div className="spx-filings">
                {data.filings.filings.map((f) => (
                  <div className="spx-filing" key={f.accession ?? `${f.form}-${f.filed}`}>
                    <span className="spx-filing-form">{f.form}</span>
                    <span className="spx-filing-date">{f.filed}</span>
                    <span className="spx-filing-desc">{f.description}</span>
                  </div>
                ))}
              </div>
            </section>

            <section className="card card-pad">
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
            </section>
          </>
        )}
      </div>
    </div>
  );
}
