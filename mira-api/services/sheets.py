import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT", "service_account.json")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")
SHEET_RANGE = os.getenv("SHEET_RANGE", "Risks_Master!A1:Z1000")

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('sheets', 'v4', credentials=creds)

def get_all_risks():
    try:
        service = get_sheets_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE
        ).execute()
        values = result.get('values', [])
        if not values:
            return []
        headers = [h.strip().lower().replace(' ', '_') for h in values[0]]
        risks = []
        for row in values[1:]:
            if not any(cell.strip() for cell in row if cell):
                continue
            padded = row + [''] * (len(headers) - len(row))
            risk = dict(zip(headers, padded))
            risks.append(risk)
        return risks
    except Exception as e:
        print(f"Sheets error: {e}")
        return []

def get_risks_for_project(project_name: str):
    all_risks = get_all_risks()
    if not all_risks:
        return []
    project_lower = project_name.lower()
    return [
        risk for risk in all_risks
        if any(project_lower in str(v).lower() for v in risk.values())
    ]

def format_risks_for_display(risks: list):
    if not risks:
        return "No risk data found for this project in the risk matrix."
    lines = []
    for i, risk in enumerate(risks, 1):
        lines.append(f"Risk {i}:")
        for key, val in risk.items():
            if val and str(val).strip():
                lines.append(f"  {key.replace('_', ' ').title()}: {val}")
        lines.append("")
    return "\n".join(lines)