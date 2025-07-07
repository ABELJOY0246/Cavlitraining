from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/greet', methods=['GET'])
def greet():
    return jsonify({"message": "Hello how are you from your HTTP server!"})

@app.route('/echo', methods=['POST'])
def echo():
    data = request.json
    return jsonify({"you_sent": data})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
