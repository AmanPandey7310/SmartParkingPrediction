from flask import Flask, jsonify, request

app = Flask(__name__)

# Dummy parking slots data
slots = {
    "A1": 0,
    "A2": 1,
    "A3": 0,
    "A4": 1
}

@app.route("/")
def home():
    return "Smart Parking Backend Running 🚗"

# Get all slots
@app.route("/slots", methods=["GET"])
def get_slots():
    return jsonify(slots)

# Update slot
@app.route("/update_slot", methods=["POST"])
def update_slot():
    data = request.json

    slot_id = data.get("slot_id")
    status = data.get("status")

    if slot_id in slots:
        slots[slot_id] = status
        return jsonify({"message": "Slot updated successfully"})
    else:
        return jsonify({"error": "Invalid slot ID"}), 400


if __name__ == "__main__":
    app.run(debug=True)