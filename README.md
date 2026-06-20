# 🐍 Python Data Toolkit

**Free, open-source Data Analysis API + Automation Scripts**

[![Live API](https://img.shields.io/badge/API-Live-brightgreen)](#api-endpoints)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

## 🚀 Live API (Free to Use!)

No API key required. No rate limits. Just `curl` and go.

### Analyze any CSV/Excel file
```bash
curl -X POST https://checklist-regions-joyce-percent.trycloudflare.com/api/analyze -F "file=@your_data.csv"
```

### Scrape any website
```bash
curl -X POST https://checklist-regions-joyce-percent.trycloudflare.com/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "extract": "tables"}'
```

### Convert between formats
```bash
curl -X POST https://checklist-regions-joyce-percent.trycloudflare.com/api/convert -F "file=@data.csv" -F "to=excel"
```

### Try the demo
```bash
curl https://checklist-regions-joyce-percent.trycloudflare.com/api/demo
```

## 📦 What's Included

### API Service (`app.py`)
- **POST /api/analyze** — Upload CSV/Excel/JSON → instant stats, distributions, missing values
- **POST /api/scrape** — Scrape any URL → tables, links, or text
- **POST /api/convert** — Convert CSV ↔ Excel ↔ JSON
- **GET /api/demo** — See a demo analysis

### Automation Scripts
- `web_scraper.py` — Command-line web scraper
- `excel_automator.py` — Merge, clean, pivot, format Excel files
- `report_generator.py` — Auto-generate reports from data
- `batch_rename.py` — Batch file renamer

### Excel Templates (8 professional templates)
Budget Tracker, Sales Dashboard, Invoice, Project Tracker, Data Cleaning, KPI Dashboard, Inventory Tracker, Employee Schedule

## 🛠️ Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
python app.py

# Or with gunicorn for production
gunicorn app:app -b 0.0.0.0:5000
```

## ⭐ Star this repo if you find it useful!

## 📄 License
MIT
