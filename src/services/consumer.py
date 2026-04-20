from src.services.queue import event_queue

async def consume_events():
    while True:
        event = await event_queue.get()

        print(f"Processing event: {event.event_id}")

        # nanti di sini kita tambah dedup logic

        event_queue.task_done()