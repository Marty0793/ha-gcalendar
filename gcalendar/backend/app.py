from flask import Flask, request, jsonify, send_from_directory
from backend.google_api import get_events, list_calendars, init_auth
from backend.config_handler import load_config

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
