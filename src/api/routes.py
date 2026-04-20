from fastapi import APIRouter
from typing import List, Union
from src.models.event import Event
from src.services.queue import event_queue

router = APIRouter()


@router.post("/publish")
async def publish(events: Union[Event, List[Event]]):
    if not isinstance(events, list):
        events = [events]

    for event in events:
        await event_queue.put(event)

    return {
        "status": "queued",
        "received": len(events)
    }