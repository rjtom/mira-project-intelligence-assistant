# MIRA Data Setup Guide

## Google Sheets Risk Matrix

MIRA's Risk Assessor Agent reads live risk data from Google Sheets
via a Service Account. Follow these steps to set it up.

---

## Step 1 — Upload Risk Matrix to Google Sheets

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it: `MIRA Risk Matrix`
4. Click **File** → **Import**
5. Upload `Risks_Master_Updated.csv`
6. Choose **Replace current sheet**
7. Click **Import data**
8. Rename the sheet tab to: `Risks_Master`

---

## Step 2 — Create Google Cloud Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Go to **APIs & Services** → **Enable APIs**
4. Search for **Google Sheets API** → Enable it
5. Go to **APIs & Services** → **Credentials**
6. Click **Create Credentials** → **Service Account**
7. Name: `mira-sheets-reader`
8. Click **Create and Continue** → **Done**
9. Click on the service account → **Keys** tab
10. **Add Key** → **Create new key** → **JSON**
11. Download the JSON file
12. Save as `service_account.json` in `mira-api/` folder

---

## Step 3 — Share Sheet with Service Account

1. Open your Google Sheet
2. Click **Share** button
3. Add the service account email (from JSON file: `client_email`)
4. Set permission to **Viewer**
5. Click **Send**

---

## Step 4 — Configure Environment

Add to `mira-api/.env`:

```
GOOGLE_SERVICE_ACCOUNT=service_account.json
SPREADSHEET_ID=your_spreadsheet_id_from_url
SHEET_RANGE=Risks_Master!A1:Z1000
```

The Spreadsheet ID is in the URL:
```
https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit
```

---

## Step 5 — Test Connection

```bash
cd mira-api
source venv/bin/activate
python3 -c "
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from services.sheets import get_all_risks
risks = get_all_risks()
print(f'Total risks loaded: {len(risks)}')
"
```

Expected output: `Total risks loaded: 26`

---

## Risk Matrix Schema

| Column | Description |
|--------|-------------|
| project_id | Unique project identifier |
| title | Full project name (must match MIRA project names) |
| type | Project type (Manufacturing, Software, etc.) |
| company | Company name (ForgeNova) |
| description | Brief project description |
| timeline | Project timeline |
| major_risks_outcome | Key risks and outcomes |
| lessons_learned | Lessons learned from the project |

---

## Project Names

The `title` column must match exactly:

```
ForgeNova EV Battery Gigafactory Expansion
ForgeNova Autonomous Driving Platform Development
ForgeNova Electric SUV Launch Program
ForgeNova Quantum Secure Software Platform
ForgeNova Hydrogen Fuel Cell Vehicle Program
ForgeNova Connected Car Ecosystem Platform
ForgeNova Battery Recycling & Second-Life Program
ForgeNova AI Driver Assistance System
ForgeNova Global ERP System Migration
ForgeNova Multi-Cloud Infrastructure Modernization
ForgeNova Enterprise Cybersecurity Enhancement Program
ForgeNova Data Analytics & Business Intelligence Platform
ForgeNova DevOps Pipeline Transformation
ForgeNova Digital Twin Factory Initiative
ForgeNova Employee Experience Platform
ForgeNova Global Supply Chain Visibility Platform
ForgeNova Software Defined Vehicle Platform
ForgeNova Next-Generation Battery Technology Program
ForgeNova Urban Air Mobility Initiative
ForgeNova Blockchain-Enabled Supply Chain Transparency
ForgeNova AI-Powered Quality Control System
ForgeNova Enterprise Sustainability Dashboard
ForgeNova Autonomous Logistics Network
ForgeNova Circular Economy Platform
ForgeNova AI Ethics and Governance Framework
ForgeNova Advanced Sustainability Intelligence Platform
```

---

## Disclaimer

All data in `Risks_Master_Updated.csv` is completely fictitious
and fabricated for educational purposes only.
ForgeNova does not exist. This is an AI learning experiment.

---

*MIRA — Project Intelligence Assistant*
*Raju Thomas | Capstone Project Applied Agentic AI | June 2026*