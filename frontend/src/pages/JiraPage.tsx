import { useEffect, useState } from "react";
import type { JiraBoard, JiraIssue } from "../types";
import { api } from "../api";
import { useFreshTracker } from "../hooks/useFreshTracker";
import "../styles/jira.css";

const NAV = [
  { icon: "📋", label: "Summary" },
  { icon: "🗓️", label: "Timeline" },
  { icon: "📥", label: "Backlog" },
  { icon: "🗂️", label: "Board", active: true },
  { icon: "📈", label: "Reports" },
  { icon: "🎫", label: "Issues" },
];

function issueType(i: JiraIssue): { key: string; label: string; color: string; glyph: string } {
  const t = (i.title || "").toLowerCase();
  if (/(bug|fix|error|incident|breach)/.test(t)) return { key: "bug", label: "Bug", color: "#E5493A", glyph: "●" };
  if (/(prepare|draft|update|review|send|build|coordinate|follow)/.test(t))
    return { key: "task", label: "Task", color: "#4BADE8", glyph: "✔" };
  return { key: "story", label: "Story", color: "#65BA43", glyph: "▮" };
}

function points(i: JiraIssue): number {
  const n = parseInt((i.key.match(/\d+/) || ["3"])[0], 10);
  return [2, 3, 5, 8, 1][n % 5];
}

function initials(name: string): string {
  return name.split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase();
}

function avatarColor(name: string): string {
  const colors = ["#5243AA", "#0052CC", "#00857A", "#C9372C", "#974F0C", "#206A83"];
  let h = 0;
  for (const c of name) h = (h * 31 + c.charCodeAt(0)) % colors.length;
  return colors[h];
}

const PRIORITY_ICON: Record<string, { c: string; g: string }> = {
  High: { c: "#CD1317", g: "⏫" },
  Medium: { c: "#E9730C", g: "🟧" },
  Low: { c: "#2D8738", g: "🔽" },
};

export default function JiraPage() {
  const [board, setBoard] = useState<JiraBoard | null>(null);

  useEffect(() => {
    const load = () => api.jira().then(setBoard).catch(() => {});
    load();
    const t = setInterval(load, 4000);
    return () => clearInterval(t);
  }, []);

  const issues = board?.issues ?? [];
  const fresh = useFreshTracker(issues.map((i) => i.id));
  const members = Array.from(new Set(issues.map((i) => i.assignee))).slice(0, 5);

  return (
    <div className="jira">
      {/* top bar */}
      <div className="jira-topbar">
        <span className="jira-logo">
          <span className="jira-logo-mark">✦</span> Jira
        </span>
        <span className="jira-top-nav">Your work</span>
        <span className="jira-top-nav">Projects</span>
        <span className="jira-top-nav">Filters</span>
        <span className="jira-top-nav">Dashboards</span>
        <div className="jira-search">🔍 Search</div>
        <div className="jira-top-spacer" />
        <span className="jira-avatar" style={{ background: "#0052CC" }}>DV</span>
      </div>

      <div className="jira-shell">
        {/* project sidebar */}
        <aside className="jira-side">
          <div className="jira-proj">
            <span className="jira-proj-ava">SS</span>
            <div>
              <div className="jira-proj-name">SSIM</div>
              <div className="jira-proj-type">Software project</div>
            </div>
          </div>
          <nav>
            {NAV.map((n) => (
              <div key={n.label} className={`jira-nav ${n.active ? "active" : ""}`}>
                <span className="jira-nav-ico">{n.icon}</span>
                {n.label}
              </div>
            ))}
          </nav>
        </aside>

        {/* board */}
        <main className="jira-main">
          <div className="jira-crumb">Projects / SSIM / Board</div>
          <div className="jira-board-head">
            <h1>SSIM board</h1>
            <div className="jira-avatars">
              {members.map((m) => (
                <span key={m} className="jira-avatar sm" title={m} style={{ background: avatarColor(m) }}>
                  {initials(m)}
                </span>
              ))}
            </div>
          </div>

          <div className="jira-columns">
            {(board?.columns ?? []).map((col) => {
              const colIssues = issues.filter((i) => i.status === col);
              return (
                <section key={col} className="jira-col">
                  <header className="jira-col-head">
                    {col.toUpperCase()} <span className="jira-col-count">{colIssues.length}</span>
                  </header>
                  <div className="jira-col-body">
                    {colIssues.map((i) => {
                      const ty = issueType(i);
                      const pr = PRIORITY_ICON[i.priority] || PRIORITY_ICON.Medium;
                      return (
                        <article key={i.id} className={`jira-card ${fresh.has(i.id) ? "fresh" : ""}`}>
                          <div className="jira-card-title">{i.title}</div>
                          <div className="jira-card-foot">
                            <span className="jira-type" title={ty.label} style={{ color: ty.color }}>
                              {ty.glyph}
                            </span>
                            <span className="jira-key">{i.key}</span>
                            <span className="jira-prio" title={i.priority} style={{ color: pr.c }}>
                              {pr.g}
                            </span>
                            <span className="jira-spacer" />
                            <span className="jira-points" title={`${points(i)} story points`}>
                              {points(i)}
                            </span>
                            <span className="jira-avatar xs" title={i.assignee} style={{ background: avatarColor(i.assignee) }}>
                              {initials(i.assignee)}
                            </span>
                          </div>
                        </article>
                      );
                    })}
                    {colIssues.length === 0 && <div className="jira-empty" />}
                  </div>
                </section>
              );
            })}
          </div>
        </main>
      </div>
    </div>
  );
}
