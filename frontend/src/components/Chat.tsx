import { useEffect, useRef, useState } from "react";
import type { ChatMessage } from "../types";
import { api } from "../api";
import { renderRich } from "../richText";

const STARTERS = [
  "What's Williams-Sonoma's latest 10-Q and stock snapshot?",
  "Create Jira tasks for the Williams-Sonoma follow-ups",
  "Log a call with Etsy to Salesforce about the RFP",
  "Book a room for my 3pm Dave BaaS review",
];

export default function Chat({
  sessionId,
  setSessionId,
  messages,
  setMessages,
  onAction,
}: {
  sessionId: string | null;
  setSessionId: (s: string) => void;
  messages: ChatMessage[];
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  onAction: () => void;
}) {
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  const send = async (text: string) => {
    const message = text.trim();
    if (!message || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: message }]);
    setBusy(true);
    try {
      const res = await api.assistant(message, sessionId);
      if (!sessionId) setSessionId(res.session_id);
      setMessages((m) => [...m, { role: "assistant", text: res.reply }]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: `⚠️ Request failed: ${String(e)}` },
      ]);
    } finally {
      setBusy(false);
      onAction(); // refresh the boards after any action
    }
  };

  return (
    <div className="card chat">
      <div className="chat-head">
        <span className="dot" />
        <strong>FinTechCo Assistant</strong>
        <span className="small muted">concierge</span>
      </div>

      <div className="chat-log" ref={logRef}>
        {messages.length === 0 && (
          <div className="chat-empty">
            Ask me to brief you, prep a meeting, book a room, create Jira tasks, or log
            Salesforce activity.
            <div className="chat-suggests">
              {STARTERS.map((s) => (
                <button key={s} onClick={() => send(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            {renderRich(m.text)}
          </div>
        ))}
        {busy && <div className="msg assistant typing">Working…</div>}
      </div>

      <div className="chat-input">
        <input
          value={input}
          placeholder="Message the assistant…"
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send(input)}
          disabled={busy}
        />
        <button className="btn" onClick={() => send(input)} disabled={busy}>
          Send
        </button>
      </div>
    </div>
  );
}
