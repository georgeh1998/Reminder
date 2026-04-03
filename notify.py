import sys
import json
import os
import calendar
from datetime import datetime, timezone, timedelta

import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

JST = timezone(timedelta(hours=9))

MODE_CONFIG = {
    "monthly": {"sheet": "Monthly", "header": "【月次共有】"},
    "weekly":  {"sheet": "Weekly",  "header": "【週次共有】"},
    "daily":   {"sheet": "Daily",   "header": "【日次共有】"},
}


def is_last_day_of_month() -> bool:
    today = datetime.now(JST)
    last_day = calendar.monthrange(today.year, today.month)[1]
    return today.day == last_day


def fetch_sheet(sheet_name: str) -> list:
    service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )
    service = build("sheets", "v4", credentials=creds)

    spreadsheet_id = os.environ["SPREADSHEET_ID"]
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A2:A")
        .execute()
    )

    values = result.get("values", [])
    return [row[0] for row in values if row and row[0].strip()]


def build_message(header: str, items: list) -> str:
    lines = [header] + [f"・{item}" for item in items]
    return "\n".join(lines)


def send_line_message(text: str):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {os.environ['LINE_CHANNEL_ACCESS_TOKEN']}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": os.environ["LINE_USER_ID"],
        "messages": [{"type": "text", "text": text}],
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in MODE_CONFIG:
        print(f"Usage: python notify.py [monthly|weekly|daily]")
        sys.exit(1)

    mode = sys.argv[1]
    config = MODE_CONFIG[mode]

    if mode == "monthly" and not is_last_day_of_month():
        print("Today is not the last day of the month. Skipping.")
        return

    items = fetch_sheet(config["sheet"])
    if not items:
        print("No items found. Skipping.")
        return

    msg = build_message(config["header"], items)
    send_line_message(msg)
    print(f"Sent {mode} reminder ({len(items)} items).")


if __name__ == "__main__":
    main()
