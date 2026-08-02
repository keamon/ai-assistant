import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import SpacexAnalyticsPage from "./SpacexAnalyticsPage";

const { spacexAnalyticsMock } = vi.hoisted(() => ({ spacexAnalyticsMock: vi.fn() }));
vi.mock("../api", () => ({ api: { spacexAnalytics: spacexAnalyticsMock } }));

const ANALYTICS = {
  company: "Space Exploration Technologies Corp.",
  ticker: "SPCX",
  index_name: "Nasdaq-100",
  index_ticker: "^NDX",
  timeline: [
    { date: "2026-06-12", label: "IPO — SPCX begins trading", kind: "market", detail: "Priced at $135/share." },
    { date: "2026-07-06", label: "Fast-tracked into the Nasdaq-100", kind: "index", detail: "A 2026 rule change." },
  ],
  prices: {
    spcx: { ticker: "SPCX", source: "mock", prices: [{ date: "2026-06-12", close: 160.95 }, { date: "2026-07-28", close: 116.41 }] },
    index: { ticker: "^NDX", source: "mock", prices: [{ date: "2026-06-12", close: 29635.95 }, { date: "2026-07-28", close: 27763.13 }] },
  },
  metrics: {
    ipo_price: 135.0,
    ipo_date: "2026-06-12",
    latest_price: 116.41,
    latest_date: "2026-07-28",
    peak_price: 211.39,
    peak_date: "2026-06-16",
    spcx_since_ipo_pct: -13.8,
    ndx_since_ipo_date_pct: -6.3,
    excess_return_since_ipo_pct: -7.5,
    inclusion_date: "2026-07-06",
    price_at_inclusion: 160.42,
    since_inclusion_pct: -27.4,
    drawdown_from_peak_pct: -44.9,
  },
  insights: ["SPCX priced at $135 on 2026-06-12 and closed at $116.41 on 2026-07-28 (-13.8% since the IPO offer price)."],
  filings: {
    company: "Space Exploration Technologies Corp.",
    ticker: "SPCX",
    cik: "0001181412",
    source: "mock",
    filings: [{ form: "424B4", filed: "2026-06-12", description: "Final IPO prospectus" }],
  },
  fred: {
    as_of: "2026-07-27",
    source: "mock",
    series: {
      DFF: { label: "Effective Federal Funds Rate", units: "%", value: 3.63, prior: 3.63, date: "2026-07-27" },
    },
    yield_curve_10y2y: 0.34,
  },
  bank_impact: [
    { title: "Equity capital markets", points: ["Record IPO fee pool."] },
  ],
  narrative: "**SpaceX** priced its IPO at $135.\n\nThe stock has since given back most of its gains.",
};

describe("SpacexAnalyticsPage", () => {
  it("renders the dashboard from the analytics payload", async () => {
    spacexAnalyticsMock.mockResolvedValue(ANALYTICS);
    render(<SpacexAnalyticsPage />);

    expect(await screen.findByText(/SpaceX Analysis/i)).toBeInTheDocument();
    expect(screen.getByText("$135")).toBeInTheDocument(); // IPO price stat
    expect(screen.getByText("$116.41")).toBeInTheDocument(); // latest price stat
    expect(screen.getByText(/Final IPO prospectus/)).toBeInTheDocument();
    expect(screen.getByText(/Equity capital markets/)).toBeInTheDocument();
    expect(screen.getByText(/Fast-tracked into the Nasdaq-100/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Download PDF report/i })).toBeEnabled();
  });
});
