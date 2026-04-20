from src.services.dedup import is_duplicate, save_event

def test_dedup_basic():
    topic = "test"
    event_id = "1"

    # pertama harus false
    assert not is_duplicate(topic, event_id)

    # simpan
    save_event(topic, event_id)

    # sekarang harus true
    assert is_duplicate(topic, event_id)