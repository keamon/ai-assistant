import { useMemo, useRef, useState } from "react";

// Self-contained on purpose (no import from ../types) — this is a generic,
// reusable 2-series indexed-line-chart component with no case-study-specific
// dependency, so it can be dropped into any dashboard.
export interface PricePoint {
  date: string;
  close: number;
}

interface Marker {
  date: string;
  label: string;
}

interface Props {
  spcx: PricePoint[];
  index: PricePoint[];
  seriesALabel: string;
  indexLabel: string;
  markers: Marker[];
}

interface Row {
  date: string;
  spcxClose: number;
  spcxIndexed: number;
  indexClose: number | null;
  indexIndexed: number | null;
}

const W = 760;
const H = 320;
const PAD = { top: 18, right: 108, bottom: 34, left: 44 };
const SERIES_1 = "#2a78d6"; // SPCX — dataviz categorical slot 1 (blue)
const SERIES_2 = "#eb6834"; // Nasdaq-100 — dataviz categorical slot 2 (orange)

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

export default function IndexedPriceChart({ spcx, index, seriesALabel, indexLabel, markers }: Props) {
  const [hoverIdx, setHoverIdx] = useState<number | null>(null);
  const [showTable, setShowTable] = useState(false);
  const svgRef = useRef<SVGSVGElement>(null);

  const rows: Row[] = useMemo(() => {
    if (!spcx.length) return [];
    const indexByDate = new Map(index.map((p) => [p.date, p.close]));
    const spcxBase = spcx[0].close;
    // Anchor the index series to the same first date SPCX has a price for,
    // so both series read 100 on SPCX's first trading day.
    const indexBase = indexByDate.get(spcx[0].date) ?? index[0]?.close ?? null;
    return spcx.map((p) => {
      const iClose = indexByDate.get(p.date) ?? null;
      return {
        date: p.date,
        spcxClose: p.close,
        spcxIndexed: (p.close / spcxBase) * 100,
        indexClose: iClose,
        indexIndexed: iClose != null && indexBase ? (iClose / indexBase) * 100 : null,
      };
    });
  }, [spcx, index]);

  if (!rows.length) return <div className="empty">No price data available.</div>;

  const n = rows.length;
  const plotW = W - PAD.left - PAD.right;
  const plotH = H - PAD.top - PAD.bottom;
  const xAt = (i: number) => PAD.left + (n === 1 ? 0 : (i / (n - 1)) * plotW);

  const allIndexed = rows.flatMap((r) => [r.spcxIndexed, r.indexIndexed].filter((v): v is number => v != null));
  const yMin = Math.min(...allIndexed);
  const yMax = Math.max(...allIndexed);
  const yPad = (yMax - yMin) * 0.12 || 5;
  const yDomain: [number, number] = [yMin - yPad, yMax + yPad];
  const yAt = (v: number) => PAD.top + plotH - ((v - yDomain[0]) / (yDomain[1] - yDomain[0])) * plotH;
  const yTicks = niceTicks(yDomain[0], yDomain[1], 4);

  const linePath = (key: "spcxIndexed" | "indexIndexed") =>
    rows
      .map((r, i) => (r[key] == null ? null : `${i === 0 || rows[i - 1]?.[key] == null ? "M" : "L"} ${xAt(i)} ${yAt(r[key]!)}`))
      .filter(Boolean)
      .join(" ");

  const lastSpcx = rows[rows.length - 1];
  const lastIndex = [...rows].reverse().find((r) => r.indexIndexed != null) ?? lastSpcx;

  const markerPositions = markers
    .map((m) => ({ ...m, i: rows.findIndex((r) => r.date === m.date) }))
    .filter((m) => m.i >= 0);

  // A few evenly-spaced date labels along the x-axis.
  const xLabelCount = 5;
  const xLabelIdxs = Array.from({ length: xLabelCount }, (_, k) => Math.round((k / (xLabelCount - 1)) * (n - 1)));

  const handleMove = (e: React.MouseEvent<SVGRectElement>) => {
    const svg = svgRef.current;
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    const xFrac = (e.clientX - rect.left) * (W / rect.width);
    const rel = (xFrac - PAD.left) / plotW;
    const i = Math.max(0, Math.min(n - 1, Math.round(rel * (n - 1))));
    setHoverIdx(i);
  };

  const hovered = hoverIdx != null ? rows[hoverIdx] : null;
  const tooltipLeft = hoverIdx != null && xAt(hoverIdx) > W - 220;

  return (
    <div>
      <div className="chart-toolbar">
        <div className="chart-legend">
          <span className="legend-item">
            <span className="legend-key" style={{ background: SERIES_1 }} />
            {seriesALabel}
          </span>
          <span className="legend-item">
            <span className="legend-key" style={{ background: SERIES_2 }} />
            {indexLabel}
          </span>
        </div>
        <button className="btn-outline chart-toggle" onClick={() => setShowTable((s) => !s)}>
          {showTable ? "View chart" : "View as table"}
        </button>
      </div>

      {showTable ? (
        <div className="chart-table-wrap">
          <table className="chart-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>{seriesALabel} close</th>
                <th>{seriesALabel} indexed</th>
                <th>{indexLabel} close</th>
                <th>{indexLabel} indexed</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.date}>
                  <td>{r.date}</td>
                  <td>${r.spcxClose.toFixed(2)}</td>
                  <td>{r.spcxIndexed.toFixed(1)}</td>
                  <td>{r.indexClose != null ? r.indexClose.toLocaleString() : "—"}</td>
                  <td>{r.indexIndexed != null ? r.indexIndexed.toFixed(1) : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="chart-svg-wrap">
          <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} width="100%" height={H} role="img"
               aria-label={`Indexed price chart comparing ${seriesALabel} and ${indexLabel}`}>
            {yTicks.map((t) => (
              <g key={t}>
                <line x1={PAD.left} x2={W - PAD.right} y1={yAt(t)} y2={yAt(t)} stroke="#e1e0d9" strokeWidth={1} />
                <text x={PAD.left - 8} y={yAt(t)} textAnchor="end" dominantBaseline="middle"
                      fontSize={10.5} fill="#898781">{t}</text>
              </g>
            ))}

            <line x1={PAD.left} x2={PAD.left} y1={PAD.top} y2={H - PAD.bottom} stroke="#c3c2b7" strokeWidth={1} />
            <line x1={PAD.left} x2={W - PAD.right} y1={H - PAD.bottom} y2={H - PAD.bottom} stroke="#c3c2b7" strokeWidth={1} />

            {xLabelIdxs.map((i) => (
              <text key={i} x={xAt(i)} y={H - PAD.bottom + 16} textAnchor="middle" fontSize={10.5} fill="#898781">
                {rows[i].date.slice(5)}
              </text>
            ))}

            {markerPositions.map((m) => (
              <g key={m.date}>
                <line x1={xAt(m.i)} x2={xAt(m.i)} y1={PAD.top} y2={H - PAD.bottom}
                      stroke="#898781" strokeWidth={1} strokeDasharray="3,3" />
                <text x={xAt(m.i)} y={PAD.top - 6} textAnchor="middle" fontSize={10} fontWeight={700} fill="#52514e">
                  {m.label}
                </text>
              </g>
            ))}

            <path d={linePath("indexIndexed")} fill="none" stroke={SERIES_2} strokeWidth={2}
                  strokeLinejoin="round" strokeLinecap="round" />
            <path d={linePath("spcxIndexed")} fill="none" stroke={SERIES_1} strokeWidth={2}
                  strokeLinejoin="round" strokeLinecap="round" />

            {lastIndex.indexIndexed != null && (
              <circle cx={xAt(rows.indexOf(lastIndex))} cy={yAt(lastIndex.indexIndexed)} r={4}
                      fill={SERIES_2} stroke="#fff" strokeWidth={2} />
            )}
            <circle cx={xAt(n - 1)} cy={yAt(lastSpcx.spcxIndexed)} r={4} fill={SERIES_1} stroke="#fff" strokeWidth={2} />

            <text x={xAt(n - 1) + 8} y={yAt(lastSpcx.spcxIndexed)} dominantBaseline="middle" fontSize={11}
                  fontWeight={700} fill="#0b0b0b">
              {seriesALabel} {lastSpcx.spcxIndexed.toFixed(0)}
            </text>
            {lastIndex.indexIndexed != null && (
              <text x={xAt(rows.indexOf(lastIndex)) + 8} y={yAt(lastIndex.indexIndexed)} dominantBaseline="middle"
                    fontSize={11} fontWeight={700} fill="#0b0b0b">
                {indexLabel} {lastIndex.indexIndexed.toFixed(0)}
              </text>
            )}

            {hoverIdx != null && (
              <line x1={xAt(hoverIdx)} x2={xAt(hoverIdx)} y1={PAD.top} y2={H - PAD.bottom}
                    stroke="#0b0b0b" strokeOpacity={0.35} strokeWidth={1} />
            )}

            <rect x={PAD.left} y={PAD.top} width={plotW} height={plotH} fill="transparent"
                  onMouseMove={handleMove} onMouseLeave={() => setHoverIdx(null)} />
          </svg>

          {hovered && (
            <div className="chart-tooltip" style={{ left: tooltipLeft ? undefined : `${(xAt(hoverIdx!) / W) * 100}%`, right: tooltipLeft ? `${100 - (xAt(hoverIdx!) / W) * 100}%` : undefined }}>
              <div className="chart-tooltip-date">{hovered.date}</div>
              <div className="chart-tooltip-row">
                <span className="chart-tooltip-key" style={{ background: SERIES_1 }} />
                <span className="chart-tooltip-label">{seriesALabel}</span>
                <strong>${hovered.spcxClose.toFixed(2)}</strong>
                <span className="muted small">({hovered.spcxIndexed.toFixed(1)} indexed)</span>
              </div>
              {hovered.indexClose != null && (
                <div className="chart-tooltip-row">
                  <span className="chart-tooltip-key" style={{ background: SERIES_2 }} />
                  <span className="chart-tooltip-label">{indexLabel}</span>
                  <strong>{hovered.indexClose.toLocaleString()}</strong>
                  <span className="muted small">({hovered.indexIndexed!.toFixed(1)} indexed)</span>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
