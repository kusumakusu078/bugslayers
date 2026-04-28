from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import datetime
import json
import os
import socket

app = Flask(__name__)
CORS(app)

DB_FILE = "reports.json"

# ── Persistence helpers ──────────────────────────────────────────────────────
def load_reports():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_reports(data):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"[WARN] Could not save reports: {e}")

# ── Detect ALL LAN IPs this machine has ──────────────────────────────────────
def get_all_local_ips():
    """Returns a list of all non-loopback IPv4 addresses on this machine."""
    ips = []
    try:
        hostname = socket.gethostname()
        # getaddrinfo gives all IPs including those on multiple interfaces
        results = socket.getaddrinfo(hostname, None)
        for result in results:
            ip = result[4][0]
            if not ip.startswith("127.") and ":" not in ip:  # skip loopback & IPv6
                if ip not in ips:
                    ips.append(ip)
    except Exception:
        pass

    # Fallback: try the outbound-route trick for each common gateway
    for gateway in ("192.168.43.1", "192.168.137.1", "10.0.0.1", "8.8.8.8"):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((gateway, 80))
            ip = s.getsockname()[0]
            s.close()
            if ip not in ips and not ip.startswith("127."):
                ips.append(ip)
        except Exception:
            pass

    return ips if ips else ["127.0.0.1"]

def pick_hotspot_ip(all_ips):
    """
    Prefer the IP that looks like a mobile hotspot address.
    Android hotspot  → 192.168.43.x
    Windows hotspot  → 192.168.137.x
    iPhone hotspot   → 172.20.10.x
    Generic LAN      → any 192.168.x.x / 10.x.x.x
    Falls back to the first IP found.
    """
    priority_prefixes = [
        "192.168.43.",   # Android hotspot (most common)
        "192.168.137.",  # Windows Mobile Hotspot
        "172.20.10.",    # iPhone Personal Hotspot
        "10.",           # corporate / generic
        "192.168.",      # generic home LAN
    ]
    for prefix in priority_prefixes:
        for ip in all_ips:
            if ip.startswith(prefix):
                return ip
    return all_ips[0] if all_ips else "127.0.0.1"

ALL_IPS  = get_all_local_ips()
NODE_IP  = pick_hotspot_ip(ALL_IPS)

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "index.html")

@app.route("/node-info")
def node_info():
    """Let the frontend discover this node's IP dynamically."""
    return jsonify({"ip": NODE_IP, "port": PORT, "all_ips": ALL_IPS})

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    message  = (data.get("message")  or "").strip()
    category = (data.get("category") or "General").strip()
    location = (data.get("location") or "Unknown").strip()
    name     = (data.get("name")     or "Anonymous").strip()

    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    report = {
        "id":        datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "category":  category,
        "msg":       message,
        "location":  location,
        "name":      name,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "date":      datetime.datetime.now().strftime("%d %b %Y"),
        "node":      NODE_IP,
    }

    reports = load_reports()
    reports.insert(0, report)
    reports = reports[:200]
    save_reports(reports)

    return jsonify({"status": "ok", "id": report["id"]})

@app.route("/view")
def view():
    reports = load_reports()
    return jsonify(reports)

@app.route("/clear", methods=["POST"])
def clear():
    save_reports([])
    return jsonify({"status": "cleared"})

@app.route("/ping")
def ping():
    """Quick health-check endpoint."""
    return jsonify({"status": "alive", "node": NODE_IP, "time": datetime.datetime.now().isoformat()})

# ─────────────────────────────────────────────────────────────────────────────
PORT = 5000

if __name__ == "__main__":
    print("=" * 60)
    print("  RESILIENTAID — OFFLINE MESH NODE")
    print("=" * 60)
    print(f"  All detected IPs : {', '.join(ALL_IPS)}")
    print(f"  Primary node IP  : {NODE_IP}  ← use this one")
    print()
    print("  ┌─ SHARE THESE URLs WITH DEVICES ON THE HOTSPOT ─────┐")
    for ip in ALL_IPS:
        print(f"  │  http://{ip}:{PORT}")
    print("  └────────────────────────────────────────────────────┘")
    print()
    print("  Data file: " + os.path.abspath(DB_FILE))
    print()
    print("  If phones can't connect → see FIREWALL FIX note below.")
    print("=" * 60)
    print()

    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
