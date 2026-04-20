from src.services.queue import event_queue
from src.services.dedup import is_duplicate, save_event, save_processed_event
from src.services.stats import increment_processed, increment_duplicate

async def consume_events():
    while True:
        event = await event_queue.get()

        if is_duplicate(event.topic, event.event_id):
            increment_duplicate()
            print(f"[CONSUMER] Duplicate: {event.event_id}")
        else:
            save_event(event.topic, event.event_id)
            save_processed_event(event)
            increment_processed()

            print(f"[CONSUMER] Processed: {event.event_id}")

        event_queue.task_done()