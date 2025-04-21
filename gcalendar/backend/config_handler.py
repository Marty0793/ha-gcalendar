import json
import os

CONFIG_PATH = "/config/google_calendar_config.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {"calendars": []}
