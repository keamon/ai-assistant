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

export interface Briefing {
  date: string;
  events: CalendarEvent[];
  upcoming_events: CalendarEvent[];
  priority_emails: EmailItem[];
  starred_emails: EmailItem[];
  market: any;
  suggestions: Suggestion[];
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
