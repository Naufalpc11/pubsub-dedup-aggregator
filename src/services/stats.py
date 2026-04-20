from src.storage.db import get_connection

stats_data = {
    "received": 0,
    "processed": 0,
    "duplicate": 0
}


def increment_received(n):
    stats_data["received"] += n


def increment_processed():
    stats_data["processed"] += 1


def increment_duplicate():
    stats_data["duplicate"] += 1


def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM processed_events")
    total_events = cursor.fetchone()[0]

    conn.close()

    return {
        "received": stats_data["received"],
        "processed": stats_data["processed"],
        "duplicate": stats_data["duplicate"],
        "stored_events": total_events
    }