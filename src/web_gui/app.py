from flask import Flask, render_template, jsonify, request
import threading
import time

app = Flask(__name__)
alerts = []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/alert")
def get_alerts():
    return jsonify(alerts[-10:])


@app.route("/api/alert", methods=["POST"])
def add_alert():
    payload = request.get_json(force=True, silent=True)
    if not payload:
        return "Bad Request", 400
    alerts.append(payload)
    return "OK", 200


def cleaner():
    while True:
        time.sleep(60)
        cutoff = time.time() - 300
        alerts[:] = [a for a in alerts if a.get("time", 0) >= cutoff]


def start_cleaner() -> None:
    thread = threading.Thread(target=cleaner, daemon=True)
    thread.start()


start_cleaner()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
