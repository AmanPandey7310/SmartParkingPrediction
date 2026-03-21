from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# ---------------- Database Initialization ----------------
def init_db():
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS slots (
        id TEXT PRIMARY KEY,
        status INTEGER
    )
    """)

    # Default slots insert karo
    cursor.execute("INSERT OR REPLACE INTO slots VALUES ('A1',0)")
    cursor.execute("INSERT OR REPLACE INTO slots VALUES ('A2',1)")
    cursor.execute("INSERT OR REPLACE INTO slots VALUES ('A3',0)")
    cursor.execute("INSERT OR REPLACE INTO slots VALUES ('A4',1)")

    conn.commit()
    conn.close()

# ✅ Call init_db before server starts
init_db()
# ----------------API-----------------
@app.route("/")
def home():
    return "Smart Parking Backend Running 🚗"

@app.route("/slots", methods=["GET"])
def get_slots():
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM slots")
    data = cursor.fetchall()
    conn.close()
    slots = {row[0]: row[1] for row in data}
    return jsonify(slots)

@app.route("/update", methods=["POST"])
def update_slot():
    data = request.json
    slot = data["slot"]
    status = data["status"]

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE slots SET status=? WHERE id=?", (status, slot))
    conn.commit()
    conn.close()

    return jsonify({"message": f"Slot {slot} updated successfully"})

# ---------------- Run Server ----------------
if __name__ == "__main__":
    app.run(debug=True)
