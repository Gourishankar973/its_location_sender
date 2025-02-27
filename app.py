from flask import Flask, render_template, request, jsonify
import neonpost
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Route to serve the main page.
@app.route('/')
def index():
    return render_template("index.html")

# Route that receives bus location updates.
@app.route('/update_bus_location', methods=['POST'])
def update_bus_location():
    data = request.get_json()
    user_id = data.get("user_id")
    bus_id = data.get("bus_id")
    lat = data.get("lat")
    lon = data.get("lon")
    
    if not all([user_id, bus_id, lat, lon]):
        return jsonify({"error": "Missing data"}), 400

    try:
        neonpost.insert_bus_location(bus_id, user_id, lon, lat)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to stop tracking and delete records for a bus_id.
@app.route('/stop_tracking', methods=['POST'])
def stop_tracking():
    data = request.get_json()
    bus_id = data.get("bus_id")
    print(bus_id, 'pk')
    if not bus_id:
        return jsonify({"error": "Missing bus_id"}), 400
    try:
        neonpost.delete_bus_location_by_id(bus_id)
        return jsonify({"status": "stopped"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
