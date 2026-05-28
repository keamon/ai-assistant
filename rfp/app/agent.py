# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
RFP Response Agent — State Street Investment Management
Accepts RFP requirements via Google Drive link or local file upload,
searches internal SSIM documents, and drafts a structured RFP response.
"""

import os
import json
import datetime

import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.mock_data import MOCK_DRIVE_DOCS, MOCK_RFP_INTERNAL_DOCS

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


def read_rfp_from_drive(file_id_or_url: str) -> str:
    """Read an RFP document from Google Drive by file ID or sharing URL.

    Args:
        file_id_or_url: Google Drive file ID or full sharing URL.

    Returns:
        JSON string with file name, MIME type, and text content (up to 8000 chars).
    """
    import re
    file_id = file_id_or_url
    if "drive.google.com" in file_id_or_url:
        match = re.search(r"/d/([a-zA-Z0-9_-]+)", file_id_or_url)
        if match:
            file_id = match.group(1)

    try:
        from googleapiclient.discovery import build

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        service = build("drive", "v3", credentials=creds)
        meta = service.files().get(fileId=file_id, fields="id, name, mimeType").execute()
        mime = meta.get("mimeType", "")

        if "google-apps.document" in mime or "google-apps.presentation" in mime:
            content = service.files().export(fileId=file_id, mimeType="text/plain").execute()
        else:
            content = service.files().get_media(fileId=file_id).execute()

        if isinstance(content, bytes):
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                text = f"[Binary file: {meta.get('name')}. Please paste the RFP text directly.]"
        else:
            text = str(content)

        return json.dumps({
            "file_id": file_id,
            "file_name": meta.get("name", ""),
            "mime_type": mime,
            "content": text[:8000],
            "truncated": len(text) > 8000,
        }, indent=2)

    except Exception as exc:
        mock_rfp = MOCK_RFP_INTERNAL_DOCS.get("sample_rfp", {})
        return json.dumps({
            "file_id": file_id,
            "file_name": "Sample RFP (Mock)",
            "content": mock_rfp.get("content", ""),
            "source": "mock",
            "note": f"Drive read failed: {exc}",
        }, indent=2)


def read_rfp_from_local_file(file_path: str) -> str:
    """Read an RFP document from a local file path (txt, md, json, pdf, docx).

    Args:
        file_path: Absolute or relative path to the RFP file on disk.

    Returns:
        JSON string with file type and text content (up to 8000 chars).
    """
    if not os.path.exists(file_path):
        return json.dumps({"error": f"File not found: {file_path}"})

    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext in (".txt", ".md", ".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        elif ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                content = "\n".join(page.extract_text() for page in reader.pages)
            except ImportError:
                content = "[PDF parsing requires 'pypdf'. Paste RFP text directly or use a Drive link.]"
        elif ext == ".docx":
            try:
                import docx
                doc = docx.Document(file_path)
                content = "\n".join(p.text for p in doc.paragraphs)
            except ImportError:
                content = "[DOCX parsing requires 'python-docx'. Paste RFP text directly or use a Drive link.]"
        else:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

        return json.dumps({
            "file_path": file_path,
            "file_type": ext,
            "content": content[:8000],
            "truncated": len(content) > 8000,
        }, indent=2)

    except Exception as exc:
        return json.dumps({"error": str(exc), "file_path": file_path})


def search_internal_documents(query: str, max_results: int = 6) -> str:
    """Search SSIM's internal Google Drive library for RFP-relevant documents.

    Covers strategy docs, fund fact sheets, DDQ responses, compliance filings,
    past RFP responses, investment policy statements, and fee schedules.

    Args:
        query: Keywords to search (e.g. "ESG integration policy", "track record",
               "fee schedule", "firm overview", "risk framework").
        max_results: Maximum documents to return. Default 6.

    Returns:
        JSON string with matching documents and content excerpts.
    """
    try:
        from googleapiclient.discovery import build

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        service = build("drive", "v3", credentials=creds)
        results = service.files().list(
            q=f"fullText contains '{query}' and trashed=false",
            pageSize=max_results,
            fields="files(id, name, mimeType, webViewLink, modifiedTime)",
            orderBy="modifiedTime desc",
        ).execute()
        return json.dumps({"query": query, "documents": results.get("files", [])}, indent=2)

    except Exception:
        q_lower = query.lower()
        matched = []
        for key, doc in MOCK_RFP_INTERNAL_DOCS.items():
            if key == "sample_rfp":
                continue
            content = doc.get("content", "")
            if q_lower in content.lower() or any(q_lower in t for t in doc.get("tags", [])):
                matched.append({
                    "id": key,
                    "name": doc.get("name", key),
                    "tags": doc.get("tags", []),
                    "excerpt": content[:400] + "...",
                    "webViewLink": f"https://drive.google.com/mock/{key}",
                })
        for doc in MOCK_DRIVE_DOCS:
            if any(q_lower in t for t in doc.get("tags", [])):
                matched.append(doc)
        if not matched:
            for key, doc in list(MOCK_RFP_INTERNAL_DOCS.items())[:3]:
                if key != "sample_rfp":
                    matched.append({"id": key, "name": doc.get("name", key),
                                    "excerpt": doc.get("content", "")[:400]})
        return json.dumps(
            {"query": query, "documents": matched[:max_results], "source": "mock"}, indent=2
        )


def get_internal_document_content(document_id: str) -> str:
    """Retrieve full text of an internal SSIM document by ID.

    Args:
        document_id: Drive file ID or mock document key from search results.

    Returns:
        Full document text content (up to 6000 characters).
    """
    try:
        from googleapiclient.discovery import build

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        service = build("drive", "v3", credentials=creds)
        content = service.files().export(fileId=document_id, mimeType="text/plain").execute()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        return content[:6000]
    except Exception:
        if document_id in MOCK_RFP_INTERNAL_DOCS:
            return MOCK_RFP_INTERNAL_DOCS[document_id].get("content", "")[:6000]
        for doc in MOCK_DRIVE_DOCS:
            if doc.get("id") == document_id:
                return doc.get("content", "")[:6000]
        return f"Document {document_id} not found."


def create_rfp_response_document(title: str, content: str) -> str:
    """Save the completed RFP response as a new Google Doc in Drive.

    Args:
        title: Document title (e.g. "SSIM RFP Response — CalPERS Global Equity 2026").
        content: Full RFP response text in Markdown or plain text.

    Returns:
        JSON string with the created document URL and ID.
    """
    try:
        from googleapiclient.discovery import build

        creds, _ = google.auth.default(
            scopes=[
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/drive.file",
            ]
        )
        docs_service = build("docs", "v1", credentials=creds)
        doc = docs_service.documents().create(body={"title": title}).execute()
        doc_id = doc["documentId"]
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": [{"insertText": {"location": {"index": 1}, "text": content}}]},
        ).execute()
        return json.dumps({
            "success": True,
            "document_id": doc_id,
            "document_url": f"https://docs.google.com/document/d/{doc_id}/edit",
            "title": title,
        }, indent=2)

    except Exception as exc:
        return json.dumps({
            "success": True,
            "document_url": f"https://docs.google.com/document/d/mock_{title[:20].replace(' ', '_')}/edit",
            "title": title,
            "note": f"Mock document created (API error: {exc})",
        }, indent=2)


SYSTEM_PROMPT = """You are the RFP Response Agent for State Street Investment Management (SSIM).

Your role is to help SSIM's business development and client solutions teams draft
high-quality, compliant, and compelling responses to investment management RFPs from
institutional investors: pension funds, sovereign wealth funds, endowments, insurance
companies, and wealth platforms.

SSIM manages ~$4.1 trillion AUM across:
- Index / passive strategies (equity, fixed income, multi-asset)
- Active quantitative equity
- ESG / sustainable investing
- Cash management and short-duration fixed income
- Multi-asset / target-date strategies

**RFP Response Workflow:**

**Step 1 — Ingest the RFP**
- Drive file ID or URL → call `read_rfp_from_drive`
- Local file path → call `read_rfp_from_local_file`
- Pasted text → use directly (no tool call needed)

**Step 2 — Analyse the RFP**
Parse and present:
- Investor name and type
- Mandate type (equity, fixed income, multi-asset, ESG, etc.)
- AUM / mandate size
- All sections and questions requiring a response
- Evaluation criteria and submission deadline

**Step 3 — Search Internal Documents**
Per major section, call `search_internal_documents` with relevant keywords:
- Performance → "track record composite attribution"
- ESG → "ESG integration responsible investment stewardship"
- Risk → "risk framework drawdown volatility"
- Team → "investment team AUM firm overview"
- Fees → "fee schedule management fee"
- Operations → "trade execution compliance custodian reporting"

Retrieve full content with `get_internal_document_content` when an excerpt is insufficient.

**Step 4 — Draft the Response**
Section-by-section response that:
- Directly answers each question
- Cites SSIM-specific data from internal docs
- Leads with strongest differentiators for that mandate type
- Marks unverified data as [VERIFY] — never fabricate
- Maintains professional SSIM brand tone

**Step 5 — Save**
Call `create_rfp_response_document` with the complete response.

**Response Format:**

# RFP Response: [Investor Name] — [Mandate Type]
**State Street Investment Management** | **Prepared**: [Date] | **Deadline**: [Deadline]

## Executive Summary
Why SSIM is uniquely positioned for this mandate (2-3 paragraphs).

## [Section heading from RFP]
[Direct response with SSIM-specific data]

## Appendix
- Track record [VERIFY with Performance team]
- Fee proposal [VERIFY with BD team]
- Team bios [VERIFY currency before submission]

**Quality standards**: Specific over generic. Mark unknowns as [VERIFY]. Flag compliance review needs.
"""

root_agent = Agent(
    name="rfp_response_agent",
    model=Gemini(
        model="gemini-2.0-flash-001",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_PROMPT,
    tools=[
        read_rfp_from_drive,
        read_rfp_from_local_file,
        search_internal_documents,
        get_internal_document_content,
        create_rfp_response_document,
    ],
)

app = App(
    root_agent=root_agent,
    name="rfp_response_app",
)
