import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import AssistantTab from "./AssistantTab";

const { briefingMock } = vi.hoisted(() => ({ briefingMock: vi.fn() }));
vi.mock("../api", () => ({ api: { briefing: briefingMock } }));

const BRIEFING = {
  date: "2026-07-25",
  events: [],
  upcoming_events: [],
  priority_emails: [],
  starred_emails: [],
  market: { ssim_payments_banking_snapshot: { total_tpv: "$11.2B", tpv_change_dod: "+2%" } },
  suggestions: [],
  public_company_watch: [
    {
      name: "Williams-Sonoma",
      company: "Williams-Sonoma, Inc.",
      ticker: "WSM",
      exchange: "NYSE",
      currency: "USD",
      price: 226.74,
      change: 8.14,
      change_pct: 3.72,
      next_earnings_date: "2026-08-26",
      latest_filing: { form: "8-K", filed: "2026-06-22", url: "https://www.sec.gov/x" },
      headline: "Williams-Sonoma tops Q2 estimates",
      source: "mock",
    },
  ],
  narrative: "**Good morning.**",
};

describe("AssistantTab — customer market watch", () => {
  it("renders the market-watch card from the briefing", async () => {
    briefingMock.mockResolvedValue(BRIEFING);
    render(<AssistantTab refreshKey={0} onAction={() => {}} />);

    expect(await screen.findByText(/Customer market watch/i)).toBeInTheDocument();
    expect(screen.getByText("Williams-Sonoma")).toBeInTheDocument();
    expect(screen.getByText("NYSE: WSM")).toBeInTheDocument();
    expect(screen.getByText("$226.74")).toBeInTheDocument();
    expect(screen.getByText("+3.72%")).toBeInTheDocument();
    // No source/provenance label shown in the UI — just the data.
    expect(screen.queryByText("mock")).not.toBeInTheDocument();
    expect(screen.queryByText("live")).not.toBeInTheDocument();
    expect(screen.getByText(/8-K/)).toBeInTheDocument();
  });
});
