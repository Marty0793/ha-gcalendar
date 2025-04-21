from flask import Flask, request, jsonify, send_from_directory
from google_api import get_events, list_calendars, init_auth, exchange_code
from config_handler import load_config, save_config

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

if __name__ == "__main__":
    print("✅ Flask HTTPS backend started!")
    app.run(
        host="0.0.0.0",
        port=8000,
        ssl_context=("/ssl/fullchain.pem", "/ssl/privkey.pem")
    )
