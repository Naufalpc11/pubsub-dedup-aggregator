from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_publish():
    response = client.post("/publish", json={
        "topic": "sensor",
        "event_id": "999",
        "timestamp": "2026-01-01T10:00:00",
        "source": "device-1",
        "payload": {}
    })

    assert response.status_code == 200