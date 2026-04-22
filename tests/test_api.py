def test_publish_single_event(client):
    event = {
        "topic": "sensor",
        "event_id": "single-1",
        "timestamp": "2026-01-01T10:00:00",
        "source": "device-1",
        "payload": {"v": 1},
    }

    response = client.post("/publish", json=event)

    assert response.status_code == 200
    assert response.json()["received"] == 1


def test_publish_batch_and_get_events_by_topic(client, wait_until_fn):
    initial_processed = client.get("/stats").json()["unique_processed"]

    events = [
        {
            "topic": "sensor-batch",
            "event_id": "batch-1",
            "timestamp": "2026-01-01T10:00:00",
            "source": "device-1",
            "payload": {"v": 10},
        },
        {
            "topic": "audit",
            "event_id": "batch-2",
            "timestamp": "2026-01-01T10:00:01",
            "source": "device-2",
            "payload": {"v": 20},
        },
    ]

    response = client.post("/publish", json=events)

    assert response.status_code == 200
    assert response.json()["received"] == 2

    def assert_processed_two():
        stats = client.get("/stats").json()
        assert stats["unique_processed"] >= initial_processed + 2

    wait_until_fn(assert_processed_two)

    sensor_events = client.get("/events", params={"topic": "sensor-batch"}).json()
    event_ids = {event["event_id"] for event in sensor_events}
    assert "batch-1" in event_ids


def test_invalid_event_schema_returns_422(client):
    invalid_event = {
        "topic": "sensor",
        "event_id": "invalid-1",
        "source": "device-1",
        "payload": {},
    }

    response = client.post("/publish", json=invalid_event)

    assert response.status_code == 422


def test_stats_contract_keys(client):
    response = client.get("/stats")

    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {
        "received",
        "unique_processed",
        "duplicate_dropped",
        "topics",
        "uptime",
    }