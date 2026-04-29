from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models import PyObjectId

class EventCreate(BaseModel):
    session_id: str
    driver_id: str
    state: str = Field(pattern="^(ALERT|MILD|DROWSY|CRITICAL)$")
    drowsiness_score: float
    ear: float
    mar: float
    pitch: float
    yaw: float
    blink_rate: float

class EventResponse(EventCreate):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}
