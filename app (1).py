from flask import Flask, request, jsonify
from flask_cors import CORS  # This is the secret sauce for stability
import sqlite3
import os

app = Flask(__name__)
# Allow all origins so your phone doesn't get blocked by the browser
CORS(app) 

# Ensure the database exists
def init_db():
    conn = sqlite3.connect('emergency.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  type TEXT, 
                  message TEXT, 
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Route to check if the server is actually reachable
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "online"}), 200

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.json
        report_type = data.get('type')
        message = data.get('message')
        
        conn = sqlite3.connect('emergency.db')
        c = conn.cursor()
        c.execute("INSERT INTO reports (type, message) VALUES (?, ?)", (report_type, message))
        conn.commit()
        conn.close()
        
        print(f"✅ Received {report_type}: {message}")
        return jsonify({"status": "success", "message": "Broadcast received"}), 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/reports', methods=['GET'])
def get_reports():
    conn = sqlite3.connect('emergency.db')
    c = conn.cursor()
    c.execute("SELECT * FROM reports ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    
    reports = [{"id": r[0], "type": r[1], "message": r[2], "time": r[3]} for r in rows]
    return jsonify(reports)

if __name__ == '__main__':
    init_db()
    # Host 0.0.0.0 is critical for phone access
    # We use port 5005 to avoid your LibreNMS conflict
    app.run(host='0.0.0.0', port=5005, debug=True)