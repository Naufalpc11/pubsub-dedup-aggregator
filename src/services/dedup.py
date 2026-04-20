from src.storage.db import get_connection
import json

def is_duplicate(topic: str, event_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM events_seen WHERE topic=? AND event_id=?",
        (topic, event_id)
    )

    result = cursor.fetchone()
    conn.close()

    return result is not None


def save_event(topic: str, event_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO events_seen (topic, event_id) VALUES (?, ?)",
            (topic, event_id)
        )
        conn.commit()
    except:
        pass

    conn.close()

def save_processed_event(event):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO processed_events (topic, event_id, timestamp, source, payload)
    VALUES (?, ?, ?, ?, ?)
    """, (
        event.topic,
        event.event_id,
        str(event.timestamp),
        event.source,
        json.dumps(event.payload)
    ))

    conn.commit()
    conn.close()
