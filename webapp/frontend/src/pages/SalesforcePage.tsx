import { useEffect, useState } from "react";
import type { SalesforceData } from "../types";
import { api } from "../api";
import { useFreshTracker } from "../hooks/useFreshTracker";
import "../styles/salesforce.css";

const TABS = ["Home", "Accounts", "Contacts", "Opportunities", "Reports", "Dashboards"];

const STAGE_ORDER = ["Qualification", "Proposal", "Negotiation", "Closed Won"];

function stageClass(stage: string): string {
  return "sf-stage " + stage.replace(/\s+/g, "");
}

function money(a: string): string {
  return a || "—";
}

export default function SalesforcePage() {
  const [data, setData] = useState<SalesforceData | null>(null);

  useEffect(() => {
    const load = () => api.salesforce().then(setData).catch(() => {});
    load();
    const t = setInterval(load, 4000);
    return () => clearInterval(t);
  }, []);

  const activities = data?.activities ?? [];
  const fresh = useFreshTracker(activities.map((a) => a.id));

  return (
    <div className="sf">
      {/* global header */}
      <header className="sf-global">
        <span className="sf-waffle">▦</span>
        <span className="sf-app">
          <span className="sf-cloud">
            <svg viewBox="0 0 16 16" width="22" height="22" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <path
                fill="currentColor"
                d="M4.406 3.342A5.53 5.53 0 0 1 8 2c2.69 0 4.923 2 5.166 4.579C14.758 6.804 16 8.137 16 9.773 16 11.569 14.502 13 12.687 13H3.781C1.708 13 0 11.366 0 9.318c0-1.763 1.266-3.223 2.942-3.593.143-.863.698-1.723 1.464-2.383"
              />
            </svg>
          </span>
        </span>
        <div className="sf-search">🔍 Search Salesforce</div>
        <div className="sf-spacer" />
        <span className="sf-gicon">★</span>
        <span className="sf-gicon">🔔</span>
        <span className="sf-uava">DV</span>
      </header>

      {/* object nav */}
      <nav className="sf-objnav">
        {TABS.map((t) => (
          <span key={t} className={`sf-obj ${t === "Opportunities" ? "active" : ""}`}>
            {t}
            {t === "Opportunities" && <span className="sf-obj-caret">▾</span>}
          </span>
        ))}
      </nav>

      <div className="sf-body">
        <div className="sf-main">
          {/* Opportunities list view */}
          <section className="sf-listview">
            <div className="sf-lv-head">
              <span className="sf-obj-icon opp">◆</span>
              <div>
                <div className="sf-lv-title">Opportunities</div>
                <div className="sf-lv-sub">
                  {data?.opportunities.length ?? 0} items · Sorted by Stage · Updated just now
                </div>
              </div>
              <div className="sf-spacer" />
              <button className="sf-btn">New</button>
            </div>
            <table className="sf-table">
              <thead>
                <tr>
                  <th>Opportunity Name</th>
                  <th>Account Name</th>
                  <th>Amount</th>
                  <th>Stage</th>
                  <th>Close Date</th>
                </tr>
              </thead>
              <tbody>
                {(data?.opportunities ?? []).map((o) => (
                  <tr key={o.id}>
                    <td><a className="sf-link">{o.name}</a></td>
                    <td><a className="sf-link">{o.account}</a></td>
                    <td>{money(o.amount)}</td>
                    <td><span className={stageClass(o.stage)}>{o.stage}</span></td>
                    <td>{o.close_date || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          {/* Accounts list view */}
          <section className="sf-listview">
            <div className="sf-lv-head">
              <span className="sf-obj-icon acct">▣</span>
              <div>
                <div className="sf-lv-title">Accounts</div>
                <div className="sf-lv-sub">{data?.accounts.length ?? 0} items · All accounts</div>
              </div>
            </div>
            <table className="sf-table">
              <thead>
                <tr>
                  <th>Account Name</th>
                  <th>Type</th>
                  <th>AUM</th>
                  <th>Owner</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {(data?.accounts ?? []).map((a) => (
                  <tr key={a.id}>
                    <td><a className="sf-link">{a.name}</a></td>
                    <td>{a.type}</td>
                    <td>{a.aum}</td>
                    <td>{a.owner}</td>
                    <td>{a.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </div>

        {/* Activity panel */}
        <aside className="sf-activity">
          <div className="sf-act-head">Activity</div>
          <div className="sf-act-tabs">
            <span className="active">Log a Call</span>
            <span>New Task</span>
            <span>New Event</span>
            <span>Email</span>
          </div>
          <div className="sf-timeline">
            {activities.map((a) => (
              <div key={a.id} className={`sf-tl ${fresh.has(a.id) ? "fresh" : ""}`}>
                <span className="sf-tl-icon">{a.type[0]}</span>
                <div className="sf-tl-body">
                  <div className="sf-tl-top">
                    <strong>{a.type}</strong> · <a className="sf-link">{a.account}</a>
                    {fresh.has(a.id) && <span className="sf-new">NEW</span>}
                  </div>
                  <div className="sf-tl-sum">{a.summary}</div>
                  <div className="sf-tl-date">{a.date}</div>
                </div>
              </div>
            ))}
            {activities.length === 0 && <div className="sf-empty">No activity logged.</div>}
          </div>
        </aside>
      </div>
    </div>
  );
}
