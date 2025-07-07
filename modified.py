from flask import Flask, request, jsonify

app = Flask(__name__)
sensor_log = []

@app.route('/greet', methods=['GET'])
def greet():
    return jsonify({"message": "Hello from your HTTP server!"})

@app.route('/echo', methods=['POST'])
def echo():
    data = request.json
    return jsonify({"you_sent": data})

@app.route('/log', methods=['POST'])
def log_sensor_data():
    data = request.json
    sensor_log.append(data)
    return jsonify({
        "message": "Data logged successfully!",
        "log_history": sensor_log
    })

# 🔍 New Addon: Return statistics
@app.route('/stats', methods=['GET'])
def sensor_stats():
    if not sensor_log:
        return jsonify({"message": "No data available", "count": 0})

    count = len(sensor_log)
    sensor_sums = {}
    sensor_counts = {}

    for entry in sensor_log:
        sensor = entry.get("sensor")
        value = entry.get("value", 0)
        sensor_sums[sensor] = sensor_sums.get(sensor, 0) + value
        sensor_counts[sensor] = sensor_counts.get(sensor, 0) + 1

    averages = {
        sensor: round(sensor_sums[sensor] / sensor_counts[sensor], 2)
        for sensor in sensor_sums
    }

    return jsonify({
        "count": count,
        "average_per_sensor": averages
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
