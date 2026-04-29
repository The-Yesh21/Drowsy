from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from bson import ObjectId
from datetime import datetime
from typing import List
import logging

from database import get_database
from models.event import EventCreate, EventResponse
from services.websocket_manager import manager

log = logging.getLogger("uvicorn")
router = APIRouter()

async def update_session_stats(db, session_id: str, event_state: str, score: float):
    # Running average and tracking logic
    session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        return
        
    old_total = session.get("total_events", 0)
    old_avg = session.get("avg_drowsiness_score", 0.0)
    
    new_total = old_total + 1
    new_avg = old_avg + ((score - old_avg) / new_total)
    
    inc_updates = {"total_events": 1}
    if event_state == "CRITICAL":
        inc_updates["critical_events"] = 1
        
    await db.sessions.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$inc": inc_updates,
            "$set": {"avg_drowsiness_score": new_avg}
        }
    )

@router.post("", response_model=dict)
async def ingest_event(event: EventCreate, background_tasks: BackgroundTasks):
    db = get_database()
    
    # Store Event
    event_dict = event.model_dump()
    event_dict["timestamp"] = datetime.utcnow()
    
    result = await db.events.insert_one(event_dict)
    event_dict["_id"] = str(result.inserted_id)
    event_dict["timestamp"] = event_dict["timestamp"].isoformat()
    
    # Background task to update session counters so response isn't delayed
    background_tasks.add_task(update_session_stats, db, event.session_id, event.state, event.drowsiness_score)
    
    # Broadcast to websocket
    await manager.broadcast(event.session_id, event_dict)
    
    return {"status": "ingested", "event_id": str(result.inserted_id)}

@router.get("/session/{session_id}", response_model=List[EventResponse])
async def get_session_events(session_id: str):
    db = get_database()
    cursor = db.events.find({"session_id": session_id}).sort("timestamp", 1)
    return await cursor.to_list(length=1000)

@router.get("/session/{session_id}/summary")
async def get_session_summary(session_id: str):
    db = get_database()
    pipeline = [
        {"$match": {"session_id": session_id}},
        {"$group": {
            "_id": "$state",
            "count": {"$sum": 1},
            "avg_score": {"$avg": "$drowsiness_score"},
            "avg_ear": {"$avg": "$ear"}
        }}
    ]
    
    cursor = db.events.aggregate(pipeline)
    summary = {}
    async for doc in cursor:
        summary[doc["_id"]] = {
            "count": doc["count"],
            "avg_score": doc["avg_score"],
            "avg_ear": doc["avg_ear"]
        }
        
    return summary
