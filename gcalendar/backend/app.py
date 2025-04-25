from flask import Flask, request, jsonify, send_from_directory
from google_api import get_events, list_calendars, init_auth, exchange_code, create_event, update_event, delete_event
from config_handler import load_config, save_config

import os
import json

app = Flask(__name__, static_folder="../calendar")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/auth", methods=["GET"])
def auth():
    return jsonify(init_auth())

@app.route("/api/calendars", methods=["GET"])
def calendars():
    return jsonify(list_calendars())

@app.route("/api/events", methods=["GET"])
def events():
    config = load_config()
    return jsonify(get_events(config))

@app.route("/api/token", methods=["GET"])
def token():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "missing code"}), 400
    success = exchange_code(code)
    if success:
        return jsonify({"status": "authenticated"})
    else:
        return jsonify({"error": "failed to exchange code"}), 500

@app.route("/api/config", methods=["GET", "POST"])
def config():
    if request.method == "GET":
        return jsonify(load_config())
    if request.method == "POST":
        new_config = request.get_json()
        save_config(new_config)
        return jsonify({"status": "saved"})

@app.route("/api/event", methods=["POST"])
def add_event():
    data = request.get_json()
    return jsonify(create_event(data))

@app.route("/api/event/<event_id>", methods=["PUT"])
def edit_event(event_id):
    data = request.get_json()
    return jsonify(update_event(event_id, data))

@app.route("/api/event/<event_id>", methods=["DELETE"])
def remove_event(event_id):
    return jsonify(delete_event(event_id))

if __name__ == "__main__":
    print("✅ Flask HTTPS backend starting")

    try:
        with open("/data/options.json") as f:
            config = json.load(f)
    except Exception as e:
        print("❌ ERROR: Unable to load /data/options.json:", str(e))
        exit(1)

    cert = config.get("certfile", "/config/addons_config/gcalendar/cert.pem")
    key = config.get("keyfile", "/config/addons_config/gcalendar/privkey.pem")

    print("📄 Loaded options.json:")
    print(json.dumps(config, indent=2))

    print(f"🔍 Cert path: {cert}")
    print(f"🔍 Key path:  {key}")

    print("📁 Contents of /data:")
    try:
        print(os.listdir("/data"))
    except Exception as e:
        print("❌ Unable to list /data:", str(e))

    print("📁 Contents of /data/gcalendar:")
    try:
        print(os.listdir("/data/gcalendar"))
    except Exception as e:
        print("❌ Unable to list /data/gcalendar:", str(e))

    if not os.path.exists(cert):
        print(f"❌ Cert file does NOT exist: {cert}")
    else:
        print(f"✅ Cert file found: {cert}")

    if not os.path.exists(key):
        print(f"❌ Key file does NOT exist: {key}")
    else:
        print(f"✅ Key file found: {key}")

    print("🚀 Starting Flask with SSL")
    app.run(
        host="0.0.0.0",
        port=8000,
        ssl_context=(cert, key)
    )
