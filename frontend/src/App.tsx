import { useEffect, useState } from "react";
import type { ChatMessage } from "./types";
import { api } from "./api";
import AssistantTab from "./tabs/AssistantTab";
import JiraPage from "./pages/JiraPage";
import SalesforcePage from "./pages/SalesforcePage";
import Chat from "./components/Chat";

function useHashRoute(): string {
  const [hash, setHash] = useState(window.location.hash);
  useEffect(() => {
    const on = () => setHash(window.location.hash);
    window.addEventListener("hashchange", on);
    return () => window.removeEventListener("hashchange", on);
  }, []);
  return hash;
}

export default function App() {
  const route = useHashRoute();

  // Standalone product pages (open in their own browser tab).
  if (route.startsWith("#/jira")) return <JiraPage />;
  if (route.startsWith("#/salesforce")) return <SalesforcePage />;

  return <AssistantApp />;
}

function AssistantApp() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [date, setDate] = useState("");

  const bump = () => setRefreshKey((k) => k + 1);

  useEffect(() => {
    const t = setInterval(bump, 5000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    api.briefing().then((b) => setDate(b.date)).catch(() => {});
  }, [refreshKey]);

  const resetDemo = async () => {
    await api.reset();
    setMessages([]);
    setSessionId(null);
    bump();
  };

  const openPage = (page: "jira" | "salesforce") => window.open(`#/${page}`, "_blank");

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <div className="brand">
            FinTechCo <span>·</span> Employee Digital Assistant
          </div>
          <div className="sub">FinTechCo · $4.1T payment volume · commercial banking</div>
        </div>
        <div className="spacer" />
        <button className="btn-ghost" onClick={() => openPage("jira")}>Open Jira ↗</button>
        <button className="btn-ghost" onClick={() => openPage("salesforce")}>Open Salesforce ↗</button>
        {date && <span className="pill">{date}</span>}
        <button className="btn-ghost" onClick={resetDemo}>Reset demo</button>
      </header>

      <main className="main">
        <div className="assistant-grid">
          <AssistantTab refreshKey={refreshKey} onAction={bump} />
          <Chat
            sessionId={sessionId}
            setSessionId={setSessionId}
            messages={messages}
            setMessages={setMessages}
            onAction={bump}
          />
        </div>
      </main>
    </div>
  );
}
