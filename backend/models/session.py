from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models import PyObjectId

class SessionResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    driver_id: PyObjectId
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = Field(pattern="^(active|completed)$")
    total_events: int = 0
    critical_events: int = 0
    avg_drowsiness_score: float = 0.0
    gemini_risk_summary: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}
