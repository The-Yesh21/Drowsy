from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime
from typing import List

from database import get_database
from models.session import SessionResponse
from routers.auth import get_current_driver
from services.gemini import generate_risk_analysis

router = APIRouter()

@router.post("/start", response_model=dict)
async def start_session(current_driver: dict = Depends(get_current_driver)):
    db = get_database()
    
    # Optional: check if there's already an active session and close it
    await db.sessions.update_many(
        {"driver_id": current_driver["_id"], "status": "active"},
        {"$set": {"status": "completed", "end_time": datetime.utcnow()}}
    )
    
    session_doc = {
        "driver_id": current_driver["_id"],
        "start_time": datetime.utcnow(),
        "end_time": None,
        "status": "active",
        "total_events": 0,
        "critical_events": 0,
        "avg_drowsiness_score": 0.0,
        "gemini_risk_summary": None
    }
    
    result = await db.sessions.insert_one(session_doc)
    return {"session_id": str(result.inserted_id), "status": "active"}

@router.post("/{session_id}/end", response_model=dict)
async def end_session(session_id: str, current_driver: dict = Depends(get_current_driver)):
    db = get_database()
    session = await db.sessions.find_one({"_id": ObjectId(session_id), "driver_id": current_driver["_id"]})
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if session["status"] == "completed":
        return {"message": "Session already completed", "gemini_risk_summary": session.get("gemini_risk_summary")}
        
    # Mark completed
    await db.sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"status": "completed", "end_time": datetime.utcnow()}}
    )
    
    # Reload session for Gemini analysis
    session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    
    # Aggregate event stats for Gemini
    pipeline = [
        {"$match": {"session_id": str(session_id)}},
        {"$group": {
            "_id": "$state",
            "count": {"$sum": 1},
            "avg_ear": {"$avg": "$ear"},
            "avg_blink": {"$avg": "$blink_rate"}
        }}
    ]
    
    cursor = db.events.aggregate(pipeline)
    events_summary = {"ALERT": 0, "MILD": 0, "DROWSY": 0, "CRITICAL": 0, "avg_ear": 0.0, "avg_blink_rate": 0.0}
    
    sum_ear, sum_blink, total_events = 0, 0, 0
    async for doc in cursor:
        state = doc["_id"]
        count = doc["count"]
        events_summary[state] = count
        sum_ear += (doc.get("avg_ear", 0) * count)
        sum_blink += (doc.get("avg_blink", 0) * count)
        total_events += count
        
    if total_events > 0:
        events_summary["avg_ear"] = sum_ear / total_events
        events_summary["avg_blink_rate"] = sum_blink / total_events
        
    # Trigger Gemini Analysis
    summary = await generate_risk_analysis(session, events_summary)
    
    # Optional: Save back to db
    await db.sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"gemini_risk_summary": summary}}
    )
    
    return {"message": "Session ended", "gemini_risk_summary": summary}
    
@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, current_driver: dict = Depends(get_current_driver)):
    db = get_database()
    session = await db.sessions.find_one({"_id": ObjectId(session_id), "driver_id": current_driver["_id"]})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/driver/{driver_id}", response_model=List[SessionResponse])
async def get_driver_sessions(driver_id: str, current_driver: dict = Depends(get_current_driver)):
    if str(current_driver["_id"]) != driver_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db = get_database()
    cursor = db.sessions.find({"driver_id": ObjectId(driver_id)}).sort("start_time", -1).limit(20)
    return await cursor.to_list(length=20)
