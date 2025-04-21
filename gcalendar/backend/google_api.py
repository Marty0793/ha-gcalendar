import os
import datetime
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_PATH = '/config/credentials.json'
TOKEN_PATH = '/config/token.json'

def init_auth():
    if not os.path.exists(TOKEN_PATH):
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        flow.redirect_uri = 'http://localhost'
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        print(f"👉 Navštiv tuto adresu pro přihlášení:\n{auth_url}")
        return {"auth_url": auth_url}
    return {"status": "already_authenticated"}

def exchange_code(code):
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        flow.redirect_uri = 'http://localhost'
        flow.fetch_token(code=code)
        creds = flow.credentials
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
        print("✅ Token uložen.")
        return True
    except Exception as e:
        print(f"[Token Exchange Error] {e}")
        return False

def get_service():
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        return build('calendar', 'v3', credentials=creds)
    return None

def list_calendars():
    service = get_service()
    if not service:
        return {"error": "No valid credentials"}
    result = []
    calendars = service.calendarList().list().execute()
    for cal in calendars.get('items', []):
        result.append({
            "id": cal["id"],
            "summary": cal["summary"],
            "backgroundColor": cal.get("backgroundColor", "#3366cc")
        })
    return result

def get_events(config):
    service = get_service()
    if not service:
        return []
    calendar_ids = config.get("calendars", [])
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    result = []

    for cal_id in calendar_ids:
        events = service.events().list(
            calendarId=cal_id,
            timeMin=now,
            maxResults=100,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        for e in events.get('items', []):
            result.append({
                "id": e["id"],
                "title": e.get("summary", "(bez názvu)"),
                "start": e["start"].get("dateTime", e["start"].get("date")),
                "end": e["end"].get("dateTime", e["end"].get("date")),
                "calendar": cal_id,
                "color": e.get("colorId")  # volitelné, pro barevné události
            })
    return result

def create_event(data):
    service = get_service()
    if not service:
        return {"error": "not authenticated"}
    calendar_id = data["calendar"]
    event = {
        "summary": data["title"],
        "start": {"dateTime": data["start"]},
        "end": {"dateTime": data["end"]}
    }
    if data.get("color"):
        event["colorId"] = data["color"]
    created = service.events().insert(calendarId=calendar_id, body=event).execute()
    return {"id": created["id"], "status": "created"}

def update_event(event_id, data):
    service = get_service()
    if not service:
        return {"error": "not authenticated"}
    calendar_id = data["calendar"]
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    event["summary"] = data["title"]
    event["start"]["dateTime"] = data["start"]
    event["end"]["dateTime"] = data["end"]
    if data.get("color"):
        event["colorId"] = data["color"]
    updated = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
    return {"id": updated["id"], "status": "updated"}

def delete_event(event_id):
    service = get_service()
    if not service:
        return {"error": "not authenticated"}
    calendar_id = service.calendarList().list().execute()["items"][0]["id"]
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    return {"status": "deleted"}
