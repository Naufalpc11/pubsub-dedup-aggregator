from fastapi import APIRouter
from typing import List, Union
from src.models.event import Event
from src.services.queue import event_queue
from src.storage.db import get_connection
from src.services.stats import increment_received
from src.services.stats import get_stats
import json

router = APIRouter()


@router.post("/publish")
async def publish(events: Union[Event, List[Event]]):
    if not isinstance(events, list):
        events = [events]

    increment_received(len(events))

    for event in events:
        await event_queue.put(event)

    return {
        "status": "queued",
        "received": len(events)
    }

@router.get("/events")
def get_events(topic: str = None):
    conn = get_connection()
    cursor = conn.cursor()

    if topic:
        cursor.execute("SELECT * FROM processed_events WHERE topic=?", (topic,))
    else:
        cursor.execute("SELECT * FROM processed_events")

    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "topic": row[0],
            "event_id": row[1],
            "timestamp": row[2],
            "source": row[3],
            "payload": json.loads(row[4])
        })

    return result

@router.get("/stats")
def stats():
    return get_stats()