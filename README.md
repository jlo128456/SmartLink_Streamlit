# SmartLink CRM v1.00 — Web Demo

> A cloud-hosted demo of the SmartLink CRM system, converted from a desktop Windows `.exe` to a Streamlit web application so testers can access it instantly in their browser — no installation required.

---

## Why We Converted from .exe to Web App

The original SmartLink CRM was built as a **Python/Tkinter desktop application** compiled into a Windows `.exe` using PyInstaller. While this works well for production use on a local machine connected to MySQL, it created several challenges when we wanted people to **test drive** the system:

| Challenge (Desktop .exe) | Solution (Web App) |
|---|---|
| Testers had to download and install a file | Open a URL — nothing to install |
| Windows SmartScreen warning on every download | No security warnings, runs in browser |
| Only works on Windows | Works on any OS — Windows, Mac, Linux, phone |
| Testers needed to be sent a new file for every update | Update the code once, everyone sees it instantly |
| File could be blocked by corporate antivirus | No file, no block |
| Required sharing via Google Drive / WeTransfer | Single public URL to share |

In short — **a web app removes every barrier between a tester and the software**. They click a link and they're in.

---

## What Is SmartLink CRM?

SmartLink CRM is a job and customer management system built for **professional audio (PA) companies**. It helps manage:

- 📋 **PA Work Orders** — create, track, and manage service jobs
- 👥 **Customers** — customer accounts and contact details
- 📦 **Inventory** — parts and product stock management
- 🧾 **Invoices** — invoicing with line items and GST
- 🔧 **Regular Service** — preventive maintenance scheduling across machines and months
- 📊 **Dashboard** — live stats, charts, and a to-do list

---

## Tech Stack

| Layer | Original (.exe) | Web Demo |
|---|---|---|
| UI | Tkinter (desktop) | Streamlit |
| Database | MySQL (production) / SQLite (demo) | SQLite (auto-seeded) |
| Charts | Matplotlib + TkAgg | Plotly |
| Hosting | Local machine | Streamlit Community Cloud |
| Access | Windows only | Any browser, any device |

---

## Demo Mode

This web app runs in **Demo Mode** — it uses a local SQLite database that is automatically created and seeded with realistic sample data on first launch. No MySQL connection or credentials are needed.

Sample data includes:
- 7 customer accounts
- 141 work orders across Jan–Apr 2025
- 12 inventory products
- 8 machines with PM schedules
- 5 demo invoices

All data is **persistent within a session** and resets on redeploy.

---

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## Deploying to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select this repo
4. Set main file path to `app.py`
5. Click **Deploy**

Your app will be live at a public URL within minutes.

---

## Project Structure

```
smartlink-demo/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── demo.db             # Auto-created SQLite database (on first run)
```

---

## Future Plans

- Reconnect to live MySQL database for production use
- Add user login and role-based access
- PDF invoice export
- Email notifications for overdue services
- Mobile-optimised layout

---

## About

SmartLink CRM v1.00 was built to streamline job management for professional audio service companies.  
This web demo was created to allow stakeholders and testers to evaluate the system without any setup friction.
