from pydantic import BaseModel, Field
from typing import Any, Dict
from datetime import datetime


class Event(BaseModel):
    topic: str
    event_id: str = Field(..., description="Unique ID")
    timestamp: datetime
    source: str
    payload: Dict[str, Any]