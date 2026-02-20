# Deployment (LXC / Proxmox)

## 1. Install app and venv

```bash
# Example: app at /var/lib/expense-receipts-app
sudo mkdir -p /var/lib/expense-receipts-app
sudo cp -r . /var/lib/expense-receipts-app/
cd /var/lib/expense-receipts-app
sudo python3 -m venv .venv
sudo .venv/bin/pip install -r requirements.txt
sudo chown -R www-data:www-data /var/lib/expense-receipts-app
```

## 2. Environment (secrets)

Create `/etc/expense-receipts/env` (or skip and set in the unit):

```bash
sudo mkdir -p /etc/expense-receipts
echo 'SECRET_KEY=your-generated-secret-key' | sudo tee /etc/expense-receipts/env
# Optional: DATABASE_URI=..., UPLOAD_FOLDER=...
sudo chown root:root /etc/expense-receipts/env
sudo chmod 600 /etc/expense-receipts/env
```

Edit the systemd unit: set `WorkingDirectory` and paths to your actual app path, then:

```bash
sudo cp deploy/expense-receipts.service /etc/systemd/system/
# Edit /etc/systemd/system/expense-receipts.service if your path is not /var/lib/expense-receipts-app
sudo systemctl daemon-reload
sudo systemctl enable expense-receipts
sudo systemctl start expense-receipts
sudo systemctl status expense-receipts
```

## 3. Nginx (you already have it)

Point your existing Nginx to the app. Example server block:

```nginx
location /receipts-app/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Prefix /receipts-app;
}
```

Or if the app is the only site on a server/port:

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Reload Nginx after changes.
