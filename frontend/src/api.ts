import type {
  Briefing,
  JiraBoard,
  SalesforceData,
  MeetingPrep,
  DocContent,
  RoomAssignment,
  Room,
  StockSnapshot,
  SecFilingsResult,
  SpacexAnalytics,
} from "./types";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return res.json();
}

export const api = {
  briefing: () => get<Briefing>("/api/briefing"),
  jira: () => get<JiraBoard>("/api/jira"),
  salesforce: () => get<SalesforceData>("/api/salesforce"),
  prep: (eventId: string) => get<MeetingPrep>(`/api/prep/${encodeURIComponent(eventId)}`),
  doc: (docId: string) => get<DocContent>(`/api/doc/${encodeURIComponent(docId)}`),
  stock: (query: string) => get<StockSnapshot>(`/api/stock/${encodeURIComponent(query)}`),
  sec: (query: string) => get<SecFilingsResult>(`/api/sec/${encodeURIComponent(query)}`),
  spacexAnalytics: () => get<SpacexAnalytics>("/api/spacex-analytics"),
  assignRoom: (body: {
    attendees: string[];
    date: string;
    start_time: string;
    end_time: string;
  }) => post<RoomAssignment>("/api/assign-room", body),
  availableRooms: (body: {
    attendees: string[];
    date: string;
    start_time: string;
    end_time: string;
  }) => post<{ available_rooms: Room[] }>("/api/available-rooms", body),
  assistant: (message: string, sessionId: string | null) =>
    post<{ reply: string; session_id: string }>("/api/assistant", {
      message,
      session_id: sessionId,
    }),
  schedule: (body: {
    title: string;
    attendees: string[];
    date: string;
    start_time: string;
    end_time: string;
    room_id?: string;
  }) => post<any>("/api/schedule", body),
  reset: () => post<{ reset: boolean; date: string }>("/api/reset", {}),
};
