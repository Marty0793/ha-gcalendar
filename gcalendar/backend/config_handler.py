import os
import json

CONFIG_PATH = "/config/addons_config/gcalendar/google_calendar_config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"calendars": []}
    with open(CONFIG_PATH, "r") as file:
        return json.load(file)

def save_config(data):
    with open(CONFIG_PATH, "w") as file:
        json.dump(data, file, indent=2)
