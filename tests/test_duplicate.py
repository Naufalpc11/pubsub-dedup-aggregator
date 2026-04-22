def test_duplicate_event_is_dropped(client, wait_until_fn):
    data = {
        "topic": "sensor",
        "event_id": "dup1",
        "timestamp": "2026-01-01T10:00:00",
        "source": "device-1",
        "payload": {},
    }

    client.post("/publish", json=data)
    client.post("/publish", json=data)

    def assert_duplicate_accounted():
        stats = client.get("/stats").json()
        assert stats["unique_processed"] == 1
        assert stats["duplicate_dropped"] == 1

    wait_until_fn(assert_duplicate_accounted)

    events = client.get("/events").json()
    assert len(events) == 1
    assert events[0]["event_id"] == "dup1"


def test_small_stress_with_20_percent_duplicates(client, wait_until_fn):
    total_unique = 100
    duplicates = 20

    unique_events = [
        {
            "topic": "stress",
            "event_id": f"stress-{i}",
            "timestamp": "2026-01-01T10:00:00",
            "source": "loadgen",
            "payload": {"idx": i},
        }
        for i in range(total_unique)
    ]

    duplicated_events = [
        {
            "topic": "stress",
            "event_id": f"stress-{i}",
            "timestamp": "2026-01-01T10:00:00",
            "source": "loadgen",
            "payload": {"idx": i},
        }
        for i in range(duplicates)
    ]

    response = client.post("/publish", json=unique_events + duplicated_events)
    assert response.status_code == 200
    assert response.json()["received"] == total_unique + duplicates

    def assert_counts_match():
        stats = client.get("/stats").json()
        assert stats["received"] == total_unique + duplicates
        assert stats["unique_processed"] == total_unique
        assert stats["duplicate_dropped"] == duplicates

    wait_until_fn(assert_counts_match, timeout=8.0)

    events = client.get("/events", params={"topic": "stress"}).json()
    assert len(events) == total_unique