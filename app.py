from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import datetime
import pickle

app = Flask(__name__)
CORS(app)

# ---------------- Load ML Model ----------------
model = pickle.load(open("model.pkl", "rb"))

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

    default_slots = [("A1", 0), ("A2", 1), ("A3", 0), ("A4", 1)]
    cursor.executemany("INSERT OR REPLACE INTO slots VALUES (?, ?)", default_slots)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slot TEXT,
        status INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        day TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- Routes ----------------

# ✅ Now frontend will load
@app.route("/")
def home():
    return render_template("index.html")

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

    day = datetime.datetime.now().strftime("%A")
    cursor.execute(
        "INSERT INTO history (slot, status, day) VALUES (?, ?, ?)",
        (slot, status, day)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": f"Slot {slot} updated successfully"})

# ---------------- ML Prediction API ----------------
@app.route("/predict", methods=["GET"])
def predict():
    # Example input (you can later make dynamic)
    day_map = {
        "Monday": 0, "Tuesday": 1, "Wednesday": 2,
        "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
    }

    current_day = datetime.datetime.now().strftime("%A")
    current_hour = datetime.datetime.now().hour

    # Convert time into slot (same logic as training)
    if 0 <= current_hour < 6:
        time_num = 0
    elif 6 <= current_hour < 12:
        time_num = 1
    elif 12 <= current_hour < 18:
        time_num = 2
    else:
        time_num = 3

    day_num = day_map[current_day]

    prediction = model.predict([[day_num, time_num]])

    return jsonify({
        "day": current_day,
        "time_slot": time_num,
        "prediction": int(prediction[0])  # 0 = free, 1 = occupied
    })


# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True)