import { useEffect, useState } from "react";
import type { SpacexAnalytics } from "../types";
import { api } from "../api";
import { renderRich } from "../richText";
import IndexedPriceChart from "../components/IndexedPriceChart";
import { downloadCaseStudyReport } from "../lib/caseStudyReportPdf";
import type { CaseStudyReport } from "../lib/caseStudyReportPdf";
import "../styles/spacex.css";

function fmtPct(n?: number): string {
  if (typeof n !== "number") return "n/a";
  return `${n >= 0 ? "+" : ""}${n.toFixed(1)}%`;
}

function fmtUsd(n?: number, decimals = 2): string {
  return typeof n === "number" ? `$${n.toFixed(decimals)}` : "n/a";
}

export default function SpacexAnalyticsPage() {
  const [data, setData] = useState<SpacexAnalytics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .spacexAnalytics()
      .then((d) => {
        if (d.error) setError(d.error);
        else setData(d);
      })
      .catch((e) => setError(String(e)));
  }, []);

  const handleDownload = async () => {
    if (!data) return;
    const report: CaseStudyReport = {
      generated_at: new Date().toISOString(),
      // Short common name, not the full SEC legal entity name — the PDF
      // chart legend has a fixed-width column and a long name overlaps it.
      company: "SpaceX",
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
      narrative: data.narrative || data.insights.join(" "),
    };
    await downloadCaseStudyReport(report);
  };

  if (error) {
    return (
      <div className="spx">
        <header className="spx-topbar">
          <div className="brand">
            FinTechCo <span>·</span> SpaceX Analysis
          </div>
        </header>
        <main className="spx-main">
          <div className="card card-pad">
            <div className="section-title">Live data unavailable</div>
            <p className="muted">{error}</p>
          </div>
        </main>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="spx">
        <header className="spx-topbar">
          <div className="brand">
            FinTechCo <span>·</span> SpaceX Analysis
          </div>
        </header>
        <main className="spx-main">
          <div className="empty">Loading live SEC EDGAR, Yahoo Finance, and FRED data…</div>
        </main>
      </div>
    );
  }

  const m = data.metrics;
  const markers = [
    { date: data.ipo_date, label: "IPO" },
    { date: data.inclusion_date, label: `${data.index_name} inclusion` },
  ];

  return (
    <div className="spx">
      <header className="spx-topbar">
        <div>
          <div className="brand">
            {data.company} <span>({data.ticker})</span> — Index-Inclusion Market Intelligence
          </div>
          <div className="sub">
            IPO {data.ipo_date} · {data.ipo_raise} raised · {data.ipo_valuation} valuation ·{" "}
            {data.index_name} inclusion {data.inclusion_date}
          </div>
        </div>
        <div className="spacer" />
        <button className="btn-ghost" onClick={handleDownload}>
          ⬇ Download PDF report
        </button>
      </header>

      <main className="spx-main">
        <div className="spx-stat-grid">
          <div className="stat spx-stat">
            <div className="label">IPO offer price</div>
            <div className="value">{fmtUsd(m.ipo_price, 0)}</div>
          </div>
          <div className="stat spx-stat">
            <div className="label">Latest price ({m.latest_date})</div>
            <div className={`value ${(m.spcx_since_ipo_pct ?? 0) >= 0 ? "pos" : "neg"}`}>
              {fmtUsd(m.latest_price)}
            </div>
            <div className="delta">{fmtPct(m.spcx_since_ipo_pct)} vs. offer</div>
          </div>
          <div className="stat spx-stat">
            <div className="label">Peak price ({m.peak_date})</div>
            <div className="value">{fmtUsd(m.peak_price)}</div>
          </div>
          <div className="stat spx-stat">
            <div className="label">Excess return vs. {data.index_name}</div>
            <div className={`value ${(m.excess_return_since_ipo_pct ?? 0) >= 0 ? "pos" : "neg"}`}>
              {fmtPct(m.excess_return_since_ipo_pct)}
            </div>
            <div className="delta">since IPO</div>
          </div>
        </div>

        <div className="card card-pad">
          <div className="section-title">Analyst narrative</div>
          <div className="spx-narrative">
            <p>{renderRich(data.narrative || data.insights.join(" "))}</p>
          </div>
        </div>

        <div className="card card-pad">
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
        </div>

        <div className="spx-two-col">
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

          <div className="spx-side-col">
            <div className="card card-pad">
              <div className="section-title">
                Macro backdrop (FRED)
                <span className={`spx-source-tag ${data.fred.source}`}>{data.fred.source}</span>
              </div>
              <div className="spx-stat-grid">
                {Object.entries(data.fred.series).map(([id, s]) => (
                  <div key={id} className="stat spx-stat">
                    <div className="label">{s.label}</div>
                    <div className="value">
                      {s.value.toFixed(2)}
                      {s.units}
                    </div>
                    <div className="delta muted">as of {s.date}</div>
                  </div>
                ))}
                <div className="stat spx-stat">
                  <div className="label">10Y–2Y yield curve</div>
                  <div className="value">
                    {data.fred.yield_curve_10y2y >= 0 ? "+" : ""}
                    {data.fred.yield_curve_10y2y.toFixed(2)}pp
                  </div>
                </div>
              </div>
            </div>

            <div className="card card-pad">
              <div className="section-title">
                SEC EDGAR filings
                <span className={`spx-source-tag ${data.filings.source}`}>{data.filings.source}</span>
              </div>
              <div className="spx-filings">
                {data.filings.filings.map((f) => (
                  <div key={(f.accession || "") + f.form + f.filed} className="spx-filing">
                    <span className="spx-filing-form">{f.form}</span>
                    <span className="spx-filing-date">{f.filed}</span>
                    <span className="spx-filing-desc">{f.description}</span>
                    {f.url && (
                      <a href={f.url} target="_blank" rel="noreferrer">
                        View ↗
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {data.news.length > 0 && (
              <div className="card card-pad">
                <div className="section-title">Recent news</div>
                <div className="spx-news">
                  {data.news.map((n, i) => (
                    <div key={i} className="spx-news-item">
                      <a className="spx-news-headline" href={n.url} target="_blank" rel="noreferrer">
                        {n.headline}
                      </a>
                      <div className="spx-news-meta">
                        {n.source} · {n.date}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="card card-pad">
          <div className="section-title">Impact on bank operations</div>
          <div className="spx-impact-grid">
            {data.bank_impact.map((sec) => (
              <div key={sec.title} className="spx-impact-card">
                <h4>{sec.title}</h4>
                <ul>
                  {sec.points.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
