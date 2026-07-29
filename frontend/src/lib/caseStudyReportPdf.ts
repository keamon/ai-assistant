import { jsPDF } from "jspdf";

// Self-contained on purpose (no import from ../types) — this is a generic,
// reusable "market-impact case study" PDF report generator with no
// case-study-specific dependency, so it can be dropped into any dashboard
// that produces this shape of data.
export interface CaseStudyReport {
  generated_at: string;
  company: string;
  ticker: string;
  index_name: string;
  index_ticker: string;
  timeline: { date: string; label: string; kind: string; detail: string }[];
  prices: {
    spcx: { source: string; prices: { date: string; close: number }[] };
    index: { source: string; prices: { date: string; close: number }[] };
  };
  metrics: {
    ipo_price?: number;
    latest_price?: number;
    latest_date?: string;
    peak_price?: number;
    peak_date?: string;
    spcx_since_ipo_pct?: number;
    ndx_since_ipo_date_pct?: number;
    excess_return_since_ipo_pct?: number;
  };
  insights: string[];
  filings: { filings: { form: string; filed: string; description: string }[] };
  fred: {
    series: Record<string, { label: string; units: string; value: number; date: string }>;
    yield_curve_10y2y: number;
  };
  bank_impact: { title: string; points: string[] }[];
  narrative: string;
}

const NAVY: [number, number, number] = [11, 36, 71];
const INK: [number, number, number] = [15, 23, 42];
const MUTED: [number, number, number] = [100, 116, 139];
const SERIES_1: [number, number, number] = [42, 120, 214]; // series A
const SERIES_2: [number, number, number] = [235, 104, 52]; // series B
const LINE: [number, number, number] = [225, 224, 217];
const GREEN: [number, number, number] = [21, 128, 61];
const RED: [number, number, number] = [185, 28, 28];

const PAGE_W = 612; // US Letter, points
const PAGE_H = 792;
const MARGIN = 48;
const CONTENT_W = PAGE_W - MARGIN * 2;

class PdfWriter {
  doc: jsPDF;
  y = MARGIN;

  constructor() {
    this.doc = new jsPDF({ unit: "pt", format: "letter" });
  }

  ensureSpace(h: number) {
    if (this.y + h > PAGE_H - MARGIN) {
      this.doc.addPage();
      this.y = MARGIN;
    }
  }

  gap(h: number) {
    this.y += h;
  }

  h2(text: string) {
    this.ensureSpace(22);
    this.doc.setFont("helvetica", "bold").setFontSize(12.5).setTextColor(...NAVY);
    this.doc.text(text.toUpperCase(), MARGIN, this.y);
    this.doc.setDrawColor(...LINE).setLineWidth(0.75);
    this.doc.line(MARGIN, this.y + 5, PAGE_W - MARGIN, this.y + 5);
    this.y += 18;
  }

  body(text: string, opts: { size?: number; color?: [number, number, number]; bold?: boolean } = {}) {
    const size = opts.size ?? 10;
    this.doc.setFont("helvetica", opts.bold ? "bold" : "normal").setFontSize(size).setTextColor(...(opts.color ?? INK));
    const lines: string[] = this.doc.splitTextToSize(text, CONTENT_W);
    for (const line of lines) {
      this.ensureSpace(size * 1.5);
      this.doc.text(line, MARGIN, this.y);
      this.y += size * 1.45;
    }
  }

  bullet(text: string) {
    const size = 9.5;
    this.doc.setFont("helvetica", "normal").setFontSize(size).setTextColor(...INK);
    const lines: string[] = this.doc.splitTextToSize(text, CONTENT_W - 14);
    this.ensureSpace(size * 1.5 * lines.length + 2);
    this.doc.setFillColor(...NAVY);
    this.doc.circle(MARGIN + 3, this.y - 3, 1.6, "F");
    lines.forEach((line, i) => {
      this.doc.text(line, MARGIN + 14, this.y + i * size * 1.45);
    });
    this.y += size * 1.45 * lines.length + 3;
  }

  caption(text: string) {
    this.ensureSpace(12);
    this.doc.setFont("helvetica", "italic").setFontSize(8.5).setTextColor(...MUTED);
    this.doc.text(text, MARGIN, this.y);
    this.y += 14;
  }
}

function fmtPct(n?: number): string {
  if (typeof n !== "number") return "n/a";
  return `${n >= 0 ? "+" : ""}${n.toFixed(1)}%`;
}

function niceTicks(min: number, max: number, count = 4): number[] {
  const span = max - min || 1;
  const rawStep = span / count;
  const mag = Math.pow(10, Math.floor(Math.log10(rawStep)));
  const norm = rawStep / mag;
  const step = (norm >= 5 ? 10 : norm >= 2 ? 5 : norm >= 1 ? 2 : 1) * mag;
  const start = Math.floor(min / step) * step;
  const ticks: number[] = [];
  for (let t = start; t <= max + step * 0.001; t += step) ticks.push(Math.round(t));
  return ticks;
}

function drawChart(w: PdfWriter, report: CaseStudyReport) {
  const seriesA = report.prices.spcx.prices;
  const seriesB = report.prices.index.prices;
  if (!seriesA.length) return;

  const indexByDate = new Map(seriesB.map((p) => [p.date, p.close]));
  const baseA = seriesA[0].close;
  const baseB = indexByDate.get(seriesA[0].date) ?? seriesB[0]?.close ?? null;
  const rows = seriesA.map((p) => {
    const closeB = indexByDate.get(p.date) ?? null;
    return {
      date: p.date,
      aIndexed: (p.close / baseA) * 100,
      bIndexed: closeB != null && baseB ? (closeB / baseB) * 100 : null,
    };
  });

  const chartH = 200;
  w.ensureSpace(chartH + 30);
  const x0 = MARGIN + 32;
  const x1 = PAGE_W - MARGIN;
  const y0 = w.y;
  const y1 = w.y + chartH;
  const plotW = x1 - x0;
  const n = rows.length;
  const xAt = (i: number) => x0 + (n === 1 ? 0 : (i / (n - 1)) * plotW);

  const allVals = rows.flatMap((r) => [r.aIndexed, r.bIndexed].filter((v): v is number => v != null));
  const yMin = Math.min(...allVals);
  const yMax = Math.max(...allVals);
  const pad = (yMax - yMin) * 0.12 || 5;
  const domain: [number, number] = [yMin - pad, yMax + pad];
  const yAt = (v: number) => y1 - ((v - domain[0]) / (domain[1] - domain[0])) * chartH;

  const doc = w.doc;

  // gridlines + y labels
  doc.setDrawColor(...LINE).setLineWidth(0.5);
  doc.setFont("helvetica", "normal").setFontSize(7.5).setTextColor(...MUTED);
  for (const t of niceTicks(domain[0], domain[1], 4)) {
    const y = yAt(t);
    doc.line(x0, y, x1, y);
    doc.text(String(t), x0 - 6, y + 2, { align: "right" });
  }

  // axis
  doc.setDrawColor(...MUTED).setLineWidth(0.75);
  doc.line(x0, y0, x0, y1);
  doc.line(x0, y1, x1, y1);

  // series lines
  const drawSeries = (key: "aIndexed" | "bIndexed", color: [number, number, number]) => {
    doc.setDrawColor(...color).setLineWidth(1.4);
    let prev: { x: number; y: number } | null = null;
    rows.forEach((r, i) => {
      const v = r[key];
      if (v == null) {
        prev = null;
        return;
      }
      const pt = { x: xAt(i), y: yAt(v) };
      if (prev) doc.line(prev.x, prev.y, pt.x, pt.y);
      prev = pt;
    });
  };
  drawSeries("bIndexed", SERIES_2);
  drawSeries("aIndexed", SERIES_1);

  // x labels (first / mid / last)
  doc.setFont("helvetica", "normal").setFontSize(7.5).setTextColor(...MUTED);
  [0, Math.floor((n - 1) / 2), n - 1].forEach((i) => {
    doc.text(rows[i].date, xAt(i), y1 + 11, { align: "center" });
  });

  // legend
  const legendY = y1 + 24;
  doc.setDrawColor(...SERIES_1).setLineWidth(2);
  doc.line(x0, legendY, x0 + 16, legendY);
  doc.setFont("helvetica", "normal").setFontSize(8.5).setTextColor(...INK);
  doc.text(`${report.company} (${report.ticker})`, x0 + 20, legendY + 3);
  doc.setDrawColor(...SERIES_2).setLineWidth(2);
  doc.line(x0 + 160, legendY, x0 + 176, legendY);
  doc.text(report.index_name, x0 + 180, legendY + 3);

  w.y = legendY + 20;
}

/** Generate and download a multi-page PDF for a market-impact case study —
 * entirely client-side, no backend PDF dependency. */
export async function downloadCaseStudyReport(report: CaseStudyReport): Promise<void> {
  const w = new PdfWriter();
  const doc = w.doc;

  // ─── Header ─────────────────────────────────────────────────
  doc.setFillColor(...NAVY);
  doc.rect(0, 0, PAGE_W, 86, "F");
  doc.setFont("helvetica", "bold").setFontSize(19).setTextColor(255, 255, 255);
  doc.text("FinTechCo Market Intelligence", MARGIN, 42);
  doc.setFont("helvetica", "normal").setFontSize(11).setTextColor(214, 226, 245);
  doc.text(`${report.company} (${report.ticker}) — IPO & ${report.index_name} Inclusion Impact Analysis`, MARGIN, 62);
  const genDate = new Date(report.generated_at).toISOString().slice(0, 10);
  doc.setFontSize(8.5).setTextColor(182, 198, 220);
  doc.text(`Generated ${genDate} · Sources: SEC EDGAR, Yahoo Finance, FRED`, MARGIN, 78);
  w.y = 86 + 26;

  // ─── Key metrics ────────────────────────────────────────────
  w.h2("Key metrics");
  const m = report.metrics;
  const metricRows: [string, string, [number, number, number]?][] = [
    ["IPO offer price", `$${m.ipo_price?.toFixed(0) ?? "n/a"}`],
    [`Latest price (${m.latest_date})`, `$${m.latest_price?.toFixed(2) ?? "n/a"}  (${fmtPct(m.spcx_since_ipo_pct)} vs. offer)`,
      m.spcx_since_ipo_pct != null ? (m.spcx_since_ipo_pct >= 0 ? GREEN : RED) : undefined],
    [`Peak price (${m.peak_date})`, `$${m.peak_price?.toFixed(2) ?? "n/a"}`],
    [`${report.index_name} return since IPO`, fmtPct(m.ndx_since_ipo_date_pct)],
    ["Excess return vs. index since IPO", fmtPct(m.excess_return_since_ipo_pct),
      m.excess_return_since_ipo_pct != null ? (m.excess_return_since_ipo_pct >= 0 ? GREEN : RED) : undefined],
  ];
  for (const [label, value, color] of metricRows) {
    w.ensureSpace(15);
    doc.setFont("helvetica", "normal").setFontSize(9.5).setTextColor(...MUTED);
    doc.text(label, MARGIN, w.y);
    doc.setFont("helvetica", "bold").setFontSize(9.5).setTextColor(...(color ?? INK));
    doc.text(value, MARGIN + 260, w.y);
    w.y += 15;
  }
  w.gap(8);

  // ─── Chart ──────────────────────────────────────────────────
  w.h2(`${report.ticker} vs. ${report.index_name} — indexed to 100 at IPO`);
  drawChart(w, report);

  // ─── Narrative ──────────────────────────────────────────────
  w.h2("Analyst narrative");
  for (const para of report.narrative.split("\n\n")) {
    w.body(para.replace(/\*\*/g, ""));
    w.gap(4);
  }
  w.gap(6);

  // ─── Timeline ───────────────────────────────────────────────
  w.h2("Timeline");
  for (const ev of report.timeline) {
    w.ensureSpace(28);
    doc.setFont("helvetica", "bold").setFontSize(9).setTextColor(...NAVY);
    doc.text(`${ev.date} — ${ev.label}`, MARGIN, w.y);
    w.y += 12;
    w.body(ev.detail, { size: 9, color: MUTED });
    w.gap(3);
  }
  w.gap(4);

  // ─── SEC filings ────────────────────────────────────────────
  w.h2("SEC EDGAR filings");
  for (const f of report.filings.filings) {
    w.ensureSpace(13);
    doc.setFont("helvetica", "bold").setFontSize(8.5).setTextColor(...NAVY);
    doc.text(f.form, MARGIN, w.y);
    doc.setFont("helvetica", "normal").setFontSize(8.5).setTextColor(...MUTED);
    doc.text(f.filed, MARGIN + 46, w.y);
    doc.setTextColor(...INK);
    doc.text(f.description, MARGIN + 104, w.y);
    w.y += 13;
  }
  w.gap(8);

  // ─── Macro backdrop ─────────────────────────────────────────
  w.h2("Macro backdrop (FRED)");
  for (const [, s] of Object.entries(report.fred.series)) {
    w.ensureSpace(14);
    doc.setFont("helvetica", "normal").setFontSize(9.5).setTextColor(...MUTED);
    doc.text(s.label, MARGIN, w.y);
    doc.setFont("helvetica", "bold").setFontSize(9.5).setTextColor(...INK);
    doc.text(`${s.value.toFixed(2)}${s.units}  (as of ${s.date})`, MARGIN + 260, w.y);
    w.y += 14;
  }
  w.ensureSpace(14);
  doc.setFont("helvetica", "normal").setFontSize(9.5).setTextColor(...MUTED);
  doc.text("10Y–2Y yield curve", MARGIN, w.y);
  doc.setFont("helvetica", "bold").setFontSize(9.5).setTextColor(...INK);
  doc.text(`${report.fred.yield_curve_10y2y >= 0 ? "+" : ""}${report.fred.yield_curve_10y2y.toFixed(2)}pp`, MARGIN + 260, w.y);
  w.y += 20;

  // ─── Bank operations impact ─────────────────────────────────
  w.h2("Impact on bank operations");
  for (const section of report.bank_impact) {
    w.ensureSpace(16);
    doc.setFont("helvetica", "bold").setFontSize(10).setTextColor(...NAVY);
    doc.text(section.title, MARGIN, w.y);
    w.y += 13;
    for (const point of section.points) w.bullet(point);
    w.gap(4);
  }

  w.caption(
    `Data sources: SEC EDGAR (data.sec.gov), Yahoo Finance, Federal Reserve Economic Data (FRED, ` +
      `Federal Reserve Bank of St. Louis). ${report.ticker}/${report.index_name} data source: ` +
      `${report.prices.spcx.source}, ${report.prices.index.source}. This report is a demo analytics ` +
      `artifact, not investment advice.`
  );

  doc.save(`${report.ticker.toLowerCase()}-case-study-report-${genDate}.pdf`);
}
