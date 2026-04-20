import requests
import time

URL = "http://aggregator:8000/publish"

event = {
    "topic": "sensor",
    "event_id": "compose-1",
    "timestamp": "2026-01-01T10:00:00",
    "source": "publisher-service",
    "payload": {"temperature": 30}
}

time.sleep(5)  # penting!

print("Sending event...")
res = requests.post(URL, json=event)
print(res.json())

time.sleep(1)

print("Sending duplicate...")
res = requests.post(URL, json=event)
print(res.json())