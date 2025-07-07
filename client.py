import requests

# Send GET
resp = requests.get("http://127.0.0.1:5000/greet")
print("GET Response:", resp.json())

# Send POST
payload = {"sensor": "temperature", "value": 28}
resp = requests.post("http://127.0.0.1:5000/echo", json=payload)
print("POST Response:", resp.json())
