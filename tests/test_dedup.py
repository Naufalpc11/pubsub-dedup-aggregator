from src.services.dedup import is_duplicate, save_event
from src.storage.db import init_db


def test_dedup_basic():
    topic = "test"
    event_id = "1"

    # pertama harus false
    assert not is_duplicate(topic, event_id)

    # simpan
    save_event(topic, event_id)

    # sekarang harus true
    assert is_duplicate(topic, event_id)


def test_dedup_persists_after_restart_simulation():
    topic = "sensor"
    event_id = "persist-1"

    save_event(topic, event_id)

    # simulasi restart: db init ulang tanpa menghapus data existing
    init_db()

    assert is_duplicate(topic, event_id)