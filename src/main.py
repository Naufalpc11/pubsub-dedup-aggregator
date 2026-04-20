from fastapi import FastAPI
from src.api.routes import router
from src.services.consumer import consume_events
import asyncio
from src.storage.db import init_db

app = FastAPI()

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    init_db()
    asyncio.create_task(consume_events())


@app.get("/")
def root():
    return {"message": "Aggregator is running"}