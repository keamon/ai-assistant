export interface CalendarEvent {
  id: string;
  title: string;
  start: string;
  end: string;
  location?: string;
  description?: string;
  attendees: string[];
  meeting_type?: string;
  video_link?: string;
  date?: string;
}

export interface EmailItem {
  id: string;
  from: string;
  subject: string;
  date: string;
  snippet: string;
  needs_action?: boolean;
  starred?: boolean;
}

export interface Suggestion {
  id: string;
  title: string;
  rationale: string;
  suggested_attendees: string[];
  suggested_duration_min: number;
  priority: string;
  suggested_date: string;
  meeting_type?: string;
}

export interface SecFiling {
  form: string;
  filed: string;
  period?: string;
  accession?: string;
  primary_doc?: string;
  url?: string;
  summary?: string;
  description?: string;
}

export interface StockNews {
  headline: string;
  source?: string;
  date?: string;
  url?: string;
}

export interface StockQuote {
  price?: number;
  change?: number;
  change_pct?: number;
  prev_close?: number;
  day_low?: number;
  day_high?: number;
  week52_low?: number;
  week52_high?: number;
  volume?: number;
  market_cap?: number;
  pe_ratio?: number;
}

export interface StockSnapshot {
  ticker: string;
  company?: string;
  exchange?: string;
  currency?: string;
  source?: "live" | "mock";
  quote?: StockQuote;
  next_earnings_date?: string;
  news?: StockNews[];
  error?: string;
  public?: boolean;
  message?: string;
}

export interface SecFilingsResult {
  company?: string;
  ticker?: string;
  cik?: string;
  source?: "live" | "mock";
  filings: SecFiling[];
  error?: string;
  public?: boolean;
  message?: string;
}

export interface PublicCompanyWatch {
  name: string;
  company?: string;
  ticker: string;
  exchange?: string;
  currency?: string;
  price?: number;
  change?: number;
  change_pct?: number;
  next_earnings_date?: string;
  latest_filing?: SecFiling | null;
  headline?: string;
  source?: string;
}

export interface Briefing {
  date: string;
  events: CalendarEvent[];
  upcoming_events: CalendarEvent[];
  priority_emails: EmailItem[];
  starred_emails: EmailItem[];
  market: any;
  suggestions: Suggestion[];
  public_company_watch?: PublicCompanyWatch[];
  narrative?: string;
}

export interface Room {
  id: string;
  name: string;
  building: string;
  floor: number;
  capacity: number;
  equipment: string[];
  av: boolean;
}

export interface JiraIssue {
  id: string;
  key: string;
  project: string;
  title: string;
  description: string;
  assignee: string;
  status: string;
  priority: string;
  created: string;
}

export interface JiraBoard {
  project: string;
  columns: string[];
  issues: JiraIssue[];
}

export interface SalesforceAccount {
  id: string;
  name: string;
  type: string;
  scale: string;
  owner: string;
  status: string;
}

export interface Opportunity {
  id: string;
  account: string;
  name: string;
  stage: string;
  amount: string;
  close_date: string;
}

export interface Activity {
  id: string;
  account: string;
  type: string;
  summary: string;
  date: string;
}

export interface SalesforceData {
  accounts: SalesforceAccount[];
  opportunities: Opportunity[];
  activities: Activity[];
}

export interface RelatedDoc {
  id: string;
  name: string;
  webViewLink?: string;
  category?: string;
}

export interface AnticipatedQuestion {
  question: string;
  answer?: string;
}

export interface MeetingPrep {
  meeting: CalendarEvent;
  is_customer_meeting: boolean;
  customer_profile: any | null;
  stock_snapshot?: StockSnapshot | null;
  latest_filing?: SecFiling | null;
  recent_emails: EmailItem[];
  related_documents: RelatedDoc[];
  objective?: string;
  agenda?: string[];
  talking_points?: string[];
  anticipated_questions?: AnticipatedQuestion[];
  error?: string;
}

export interface DocContent {
  id: string;
  name: string;
  content: string;
  webViewLink?: string;
  category?: string;
  error?: string;
}

export interface RoomAssignment {
  assigned: Room | null;
  rationale?: string;
  required_capacity?: number;
  in_person_count?: number;
  remote_count?: number;
  alternatives?: Room[];
  reason?: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  text: string;
}

// ─── SpaceX index-inclusion analytics dashboard ────────────────────────────

export interface PriceSeries {
  ticker: string;
  source: "live" | "mock";
  currency?: string;
  prices: { date: string; close: number }[];
}

export interface TimelineEvent {
  date: string;
  label: string;
  kind: "filing" | "market" | "index";
  detail: string;
}

export interface EventStudyMetrics {
  ipo_price?: number;
  first_close_price?: number;
  first_close_pop_pct?: number;
  peak_price?: number;
  peak_date?: string;
  latest_price?: number;
  latest_date?: string;
  inclusion_date_price?: number | null;
  since_inclusion_pct?: number | null;
  since_peak_pct?: number;
  spcx_since_ipo_pct?: number;
  ndx_since_ipo_date_pct?: number;
  excess_return_since_ipo_pct?: number;
}

export interface FredSeriesPoint {
  label: string;
  units: string;
  value: number;
  prior?: number;
  date: string;
}

export interface FredSnapshot {
  as_of: string;
  source: "live" | "mock";
  series: Record<string, FredSeriesPoint>;
  yield_curve_10y2y: number;
}

export interface BankImpactSection {
  title: string;
  points: string[];
}

export interface SpacexAnalytics {
  company: string;
  ticker: string;
  index_name: string;
  index_ticker: string;
  ipo_date: string;
  inclusion_date: string;
  timeline: TimelineEvent[];
  prices: { spcx: PriceSeries; index: PriceSeries };
  metrics: EventStudyMetrics;
  insights: string[];
  filings: {
    company?: string;
    ticker?: string;
    cik?: string;
    source?: "live" | "mock";
    filings: (SecFiling & { description: string })[];
  };
  fred: FredSnapshot;
  bank_impact: BankImpactSection[];
  narrative: string;
}
