import os
import datetime
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_PATH = '/config/credentials.json'
TOKEN_PATH = '/config/token.json'
CONFIG_PATH = '/config/google_calendar_config.json'

def init_auth():
    if not os.path.exists(TOKEN_PATH):
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        auth_url, _ = flow.authorization_url(prompt='consent')
        print(f"👉 Navštiv tuto adresu pro přihlášení:\n{auth_url}")
        return {"auth_url": auth_url}
    return {"status": "already_authenticated"}


def get_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            return None
    return build('calendar', 'v3', credentials=creds)

def list_calendars():
    service = get_service()
    if not service:
        return {"error": "No valid credentials"}

    calendar_list = service.calendarList().list().execute()
    return [{"id": cal["id"], "summary": cal["summary"]} for cal in calendar_list.get('items', [])]

def get_events(config):
    service = get_service()
    if not service:
        return []

    calendar_ids = config.get("calendars", [])
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = []

    for calendar_id in calendar_ids:
        events = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        for e in events.get('items', []):
            events_result.append({
                "title": e.get("summary", "(bez názvu)"),
                "start": e["start"].get("dateTime", e["start"].get("date")),
                "end": e["end"].get("dateTime", e["end"].get("date")),
                "calendar": calendar_id
            })
    return events_result
