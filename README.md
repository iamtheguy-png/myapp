# Expense Receipt Manager

Flask app for managing expense receipts: upload PDF/images, custom tags, OCR search, export and reports. Runs on Ubuntu/Debian (e.g. LXC on Proxmox); local network only, no auth.

## Stack

- **Backend:** Flask 3, SQLAlchemy, SQLite
- **UI:** Server-rendered templates, CSS variables, dark mode (localStorage)
- **Deploy:** Gunicorn behind your existing Nginx; systemd unit for boot.

## LXC / Proxmox

- **Resources:** 512 MB–1 GB RAM is enough; single Gunicorn worker.
- **Nginx:** Use your existing Nginx; add a reverse proxy to the app (see Production below). No Nginx config is shipped.

## Dependencies

- **Python 3.10+**, venv, `pip install -r requirements.txt`
- **OCR (optional):** `apt install tesseract-ocr poppler-utils` (Debian/Ubuntu). If missing, uploads still work; text/merchant/date from OCR will be empty.

## Quick start (development)

```bash
cd expense-receipts-app
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export FLASK_APP=wsgi
export FLASK_ENV=development
flask run --host=0.0.0.0
```

Open `http://<your-ip>:5000`. Use the header button to toggle dark mode.

## Production (LXC, Nginx already running)

1. **Secrets:** Set `SECRET_KEY` in the environment (required). Optional: `DATABASE_URI`, `UPLOAD_FOLDER`. Do not use the default dev secret.

2. **Gunicorn:** Run the app (e.g. via systemd):
   ```bash
   gunicorn -w 1 -b 127.0.0.1:8000 --timeout 120 wsgi:app
   ```

3. **Nginx:** Point your existing Nginx at the app. Example (app on port 8000):
   ```nginx
   location / {
     proxy_pass http://127.0.0.1:8000;
     proxy_set_header Host $host;
     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
     proxy_set_header X-Forwarded-Proto $scheme;
   }
   ```
   Reload Nginx after editing.

4. **Systemd:** Copy and adapt `deploy/expense-receipts.service`, then enable/start. See `deploy/README.md` for full steps.

## Logging and errors

- **Logging:** INFO-level, timestamp + level + message. No secrets or request bodies. OCR failures are logged by receipt id only.
- **413 (file too large):** Shown when upload exceeds 20 MB; user gets a clear message and link back to upload.
- **OCR failure:** Receipt is still saved; user sees a message that text extraction failed and can still use tags and date.

## Project layout

- `app/` — Flask package: `config`, `models`, `routes`, `templates`, `static`, `services`
- `instance/` — SQLite DB and uploads (created at first run)
- `deploy/` — systemd unit and deployment notes
- `PLAN.md` — Requirements and phased execution plan

## Phases

- **Phase 1–4 (done):** Foundation, upload/tags, OCR/search, export/reports
- **Phase 5 (done):** Systemd, error handling, logging, docs (Nginx not included; use your existing setup)
