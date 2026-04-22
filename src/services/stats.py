import time

from src.storage.db import get_connection

stats_data = {
    "received": 0,
    "unique_processed": 0,
    "duplicate_dropped": 0,
}

start_time = time.time()


def increment_received(n):
    stats_data["received"] += n


def increment_processed():
    stats_data["unique_processed"] += 1


def increment_duplicate():
    stats_data["duplicate_dropped"] += 1


def reset_stats():
    stats_data["received"] = 0
    stats_data["unique_processed"] = 0
    stats_data["duplicate_dropped"] = 0

    global start_time
    start_time = time.time()


def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT topic FROM processed_events ORDER BY topic")
    topic_rows = cursor.fetchall()
    topics = [row[0] for row in topic_rows]

    conn.close()

    return {
        "received": stats_data["received"],
        "unique_processed": stats_data["unique_processed"],
        "duplicate_dropped": stats_data["duplicate_dropped"],
        "topics": topics,
        "uptime": round(time.time() - start_time, 3),
    }