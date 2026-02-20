# Expense Receipt Manager — Requirements & Execution Plan

## 1. Requirements List

### 1.1 Functional Requirements

| ID | Requirement | Notes |
|----|-------------|--------|
| **FR-1** | Manual upload of receipts | Support PDF and image files (JPG, PNG). Drag-and-drop or file picker. |
| **FR-2** | Custom tags only | No predefined categories; user creates all tags. |
| **FR-3** | Multiple tags per receipt | One receipt can have many tags (many-to-many). |
| **FR-4** | OCR on upload | Extract text from each receipt (PDF and images) for search. |
| **FR-5** | Search by tags | Filter receipts by one or more tags. |
| **FR-6** | Search by date range | Filter by receipt date (stored or inferred from OCR). |
| **FR-7** | Search by merchant | Merchant from OCR text; search/filter by merchant name. |
| **FR-8** | Export data | Export filtered list (e.g. CSV) for external use. |
| **FR-9** | Reports | Generate reports (e.g. by tag, by month, by merchant) — view and/or export (PDF/CSV). |

### 1.2 Non-Functional Requirements

| ID | Requirement | Notes |
|----|-------------|--------|
| **NFR-1** | Modern UI | Clean, responsive layout; works on desktop browsers. |
| **NFR-2** | Dark mode | Toggle or system preference; persist user choice (e.g. localStorage). |
| **NFR-3** | Lightweight stack | Low CPU/RAM; suitable for small LXC (e.g. 512MB–1GB RAM). |
| **NFR-4** | Run on Ubuntu/Debian LXC | No Docker; app + reverse proxy directly on the VM. |
| **NFR-5** | Local network only | No authentication; not exposed to the internet. |
| **NFR-6** | Personal data only | Design for single user; no multi-tenant or sensitive compliance burden. |
| **NFR-7** | Scale | ~10 receipts/month; SQLite and local file storage are sufficient. |

### 1.3 Out of Scope (Confirmed)

- Multi-user or roles
- Authentication / SSO / LDAP
- Mobile app (web-only)
- Integration with accounting software or bank feeds
- Cloud backup (can be added later via cron/scripts)

---

## 2. Recommended Stack (Lightweight)

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Backend** | Python 3 + Flask or FastAPI | Light, easy to deploy; Python needed for OCR (Tesseract). |
| **OCR** | Tesseract + `pytesseract`; PDFs via `pdf2image` + Tesseract or `pymupdf` for text | Free, local, no API keys. |
| **Database** | SQLite | No separate server; one file; ideal for single user. |
| **Frontend** | Server-rendered HTML + minimal CSS/JS | Dark mode + upload UX without heavy frameworks. |
| **Storage** | Local filesystem | Receipt files in a dedicated directory; paths in DB. |
| **Server** | Gunicorn (WSGI) + Nginx (reverse proxy) | Standard, light, easy on Debian/Ubuntu. |

Alternatives: **FastAPI** instead of Flask if you prefer async and automatic OpenAPI docs.

---

## 3. Execution Plan

### Phase 1 — Foundation (Week 1)

**Goal:** Run a minimal web app on the LXC with a modern UI and dark mode.

- [ ] **1.1** Set up project structure (backend app, static/templates, config).
- [ ] **1.2** Implement minimal Flask/FastAPI app with one “home” page.
- [ ] **1.3** Add modern CSS (layout, typography, spacing) and dark mode toggle (CSS variables + JS; persist in `localStorage`).
- [ ] **1.4** Document and run deployment steps: Python venv, Gunicorn, Nginx on Ubuntu/Debian LXC.
- [ ] **1.5** Create SQLite schema: `receipts` (id, file_path, original_filename, created_at, receipt_date, merchant, extracted_text), `tags` (id, name), `receipt_tags` (receipt_id, tag_id). Add migrations or init script.

**Deliverable:** App is reachable on the local network; homepage shows UI with dark mode working.

---

### Phase 2 — Upload, Storage & Tags (Week 2) ✅

**Goal:** Upload receipts (PDF + images), store files and metadata, assign multiple custom tags.

- [x] **2.1** File upload endpoint: accept PDF, JPG, PNG; validate type/size; save to local storage; store path and metadata in DB.
- [x] **2.2** Tag model: create/rename/delete tags (custom only).
- [x] **2.3** Receipt–tag association: UI to assign/remove multiple tags per receipt.
- [x] **2.4** List view: show receipts with thumbnails (or icons), date, merchant placeholder, tags.
- [x] **2.5** Secure file handling: allowlist extensions, size limits, safe filenames (e.g. UUID + original extension), store outside web root; serve via app controller if needed.

**Deliverable:** User can upload receipts and manage tags; receipts list shows tags and basic metadata.

---

### Phase 3 — OCR & Search (Week 3) ✅

**Goal:** Extract text from receipts; search by tags, date range, and merchant.

- [x] **3.1** OCR pipeline: on upload (or background job), run Tesseract on images; for PDFs, extract pages as images or text (e.g. PyMuPDF) and run Tesseract where needed. Store `extracted_text` and optional `receipt_date`/`merchant` if parsed.
- [x] **3.2** Optional: simple heuristics or regex to infer receipt date and merchant from `extracted_text`; update DB.
- [x] **3.3** Search API/page: filter by tags (AND/OR), date range, and merchant (substring match on `extracted_text` or stored `merchant`).
- [x] **3.4** Search UI: form with tag multi-select, date range picker, merchant field; results list with same layout as Phase 2.

**Deliverable:** New receipts get OCR text; user can find receipts by tags, date range, and merchant.

---

### Phase 4 — Export & Reports (Week 4) ✅

**Goal:** Export data and generate simple reports.

- [x] **4.1** Export: CSV of receipts (columns: date, merchant, tags, file path/link, etc.) for current search results or “all”.
- [x] **4.2** Reports: at least one report (e.g. “by month” or “by tag”) with totals/counts; output as HTML view and optional CSV/PDF.
- [x] **4.3** Report UI: choose report type, date range, format; show or download.

**Deliverable:** User can export receipt lists and run basic reports (view + download).

---

### Phase 5 — Polish & Deployment (Week 5) ✅

**Goal:** Harden deployment and UX for daily use on LXC.

- [x] **5.1** Nginx: skipped (user already has Nginx on Proxmox); docs show how to proxy to the app.
- [x] **5.2** Systemd unit for the app so it starts on boot (`deploy/expense-receipts.service`).
- [x] **5.3** Error handling and user-facing messages for upload/OCR failures (413 page, OCR failure flash).
- [x] **5.4** Basic logging (no secrets in logs); INFO format, OCR failures logged by receipt id only.
- [x] **5.5** README and `deploy/README.md`: dependencies, venv, env vars, LXC guidance (512MB–1GB), proxy example.

**Deliverable:** App runs reliably on LXC; one-command or few-step restart; docs for future you or others.

---

## 4. Suggested File Layout

```
expense-receipts-app/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── routes/
│   │   ├── receipts.py
│   │   ├── tags.py
│   │   ├── search.py
│   │   └── export_reports.py
│   ├── services/
│   │   ├── ocr.py
│   │   └── storage.py
│   └── templates/
├── static/
│   ├── css/
│   ├── js/
│   └── ...
├── uploads/          # receipt files (or under /var/lib/... in prod)
├── instance/         # SQLite DB, config overrides
├── requirements.txt
├── PLAN.md          # this file
└── README.md
```

---

## 5. Risk & Mitigation

| Risk | Mitigation |
|------|-------------|
| OCR quality on photos/PDFs | Use Tesseract with image preprocessing (deskew, contrast); optional: allow manual edit of merchant/date. |
| Large PDFs | Enforce max file size (e.g. 10–20 MB); process first N pages if needed. |
| LXC underpowered | Keep Gunicorn workers low (1–2); run OCR synchronously or with a single background worker. |

---

## 6. Success Criteria

- Upload PDF and images; assign multiple custom tags.
- OCR runs and text is searchable.
- Search works by tags, date range, and merchant.
- Export (CSV) and at least one report (view + download) work.
- UI is modern with working dark mode; app runs on Ubuntu/Debian LXC with a light footprint.

If you want, next step can be a **detailed technical spec** (API endpoints, DB schema SQL, and exact UI flows) or **scaffolding code** (Flask/FastAPI project skeleton and first routes).
