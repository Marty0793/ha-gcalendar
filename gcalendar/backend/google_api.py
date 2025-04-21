import os
import datetime
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_PATH = '/config/credentials.json'
TOKEN_PATH = '/config/token.json'

# 🔁 Přidáno: cache pro barvy událostí
_cached_colors = None

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
    import time
    start_debug = time.time()

    service = get_service()
    if not service:
        return []

    calendar_ids = config.get("calendars", [])
    now = datetime.datetime.utcnow().isoformat() + 'Z'

    # 🔁 Použijeme cache pro barvy
    global _cached_colors
    if not _cached_colors:
        print("[DEBUG] Načítám barvy událostí z Google API...")
        color_data = service.colors().get().execute()
        _cached_colors = color_data.get("event", {})
    event_colors = _cached_colors

    events_result = []

    for calendar_id in calendar_ids:
        events = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=20,  # 🔽 Původně 100 – pro rychlejší načítání
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        for e in events.get('items', []):
            color_id = e.get("colorId")
            background = event_colors.get(color_id, {}).get("background", "#3788d8")

            # 🧠 Korektní handlování celodenních událostí
            start = e["start"].get("dateTime", e["start"].get("date"))
            end = e["end"].get("dateTime", e["end"].get("date"))
            if "date" in e["start"] and end == start:
                end_date = datetime.datetime.strptime(end, "%Y-%m-%d") + datetime.timedelta(days=1)
                end = end_date.strftime("%Y-%m-%d")

            events_result.append({
                "id": e.get("id"),
                "title": e.get("summary", "(bez názvu)"),
                "start": start,
                "end": end,
                "allDay": "date" in e["start"],
                "calendar": calendar_id,
                "color": background
            })

    print(f"[DEBUG] get_events hotovo za {time.time() - start_debug:.2f} s")
    return events_result

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
