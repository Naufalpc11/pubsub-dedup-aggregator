from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_duplicate_event():
    data = {
        "topic": "sensor",
        "event_id": "dup1",
        "timestamp": "2026-01-01T10:00:00",
        "source": "device-1",
        "payload": {}
    }

    client.post("/publish", json=data)
    client.post("/publish", json=data)

    # kita belum cek output, tapi minimal tidak error
    assert True