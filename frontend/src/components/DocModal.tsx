import { useEffect, useState } from "react";
import type { DocContent } from "../types";
import { api } from "../api";
import Modal from "./Modal";

export default function DocModal({ docId, onClose }: { docId: string; onClose: () => void }) {
  const [doc, setDoc] = useState<DocContent | null>(null);

  useEffect(() => {
    api.doc(docId).then(setDoc).catch(() => setDoc({ id: docId, name: "", content: "", error: "load failed" }));
  }, [docId]);

  return (
    <Modal title={doc?.name || "Document"} onClose={onClose} width={720}>
      {!doc && <div className="spin">Loading document…</div>}
      {doc?.error && <div className="empty">Could not load this document.</div>}
      {doc && !doc.error && (
        <>
          {doc.category && <span className="chip" style={{ marginBottom: 10, display: "inline-block" }}>{doc.category}</span>}
          <pre className="doc-content">{doc.content}</pre>
          {doc.webViewLink && (
            <a className="doclink" href={doc.webViewLink} target="_blank" rel="noreferrer">
              Open document ↗
            </a>
          )}
        </>
      )}
    </Modal>
  );
}
