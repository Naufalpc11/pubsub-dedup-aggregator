import sqlite3

DB_PATH = "events.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # dedup table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events_seen (
        topic TEXT,
        event_id TEXT,
        PRIMARY KEY (topic, event_id)
    )
    """)

    # processed events table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processed_events (
        topic TEXT,
        event_id TEXT,
        timestamp TEXT,
        source TEXT,
        payload TEXT
    )
    """)

    conn.commit()
    conn.close()