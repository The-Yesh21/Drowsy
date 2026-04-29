from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime, timedelta

from database import get_database
from routers.auth import get_current_driver
from services.gemini import generate_risk_analysis

router = APIRouter()

@router.get("/driver/{driver_id}")
async def get_driver_analytics(driver_id: str, current_driver: dict = Depends(get_current_driver)):
    if str(current_driver["_id"]) != driver_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db = get_database()
    
    # Simple aggregations across all sessions for this driver
    pipeline = [
        {"$match": {"driver_id": ObjectId(driver_id), "status": "completed"}},
        {"$group": {
            "_id": None,
            "total_sessions": {"$sum": 1},
            "total_events": {"$sum": "$total_events"},
            "critical_events": {"$sum": "$critical_events"},
            "avg_drowsiness_score": {"$avg": "$avg_drowsiness_score"}
        }}
    ]
    
    cursor = db.sessions.aggregate(pipeline)
    stats = await cursor.to_list(length=1)
    
    result = {
        "total_sessions": 0,
        "total_events": 0,
        "critical_events": 0,
        "avg_drowsiness_score": 0.0,
        "trend_7_days": []
    }
    
    if stats:
        result.update(stats[0])
        del result["_id"]
        
    # 7-day trend
    week_ago = datetime.utcnow() - timedelta(days=7)
    trend_pipeline = [
        {"$match": {"driver_id": str(driver_id), "timestamp": {"$gte": week_ago}}},
        {"$group": {
            "_id": {
                "year": {"$year": "$timestamp"},
                "month": {"$month": "$timestamp"},
                "day": {"$dayOfMonth": "$timestamp"}
            },
            "events_count": {"$sum": 1}
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}}
    ]
    
    trend_cursor = db.events.aggregate(trend_pipeline)
    async for doc in trend_cursor:
        date_str = f"{doc['_id']['year']}-{doc['_id']['month']:02d}-{doc['_id']['day']:02d}"
        result["trend_7_days"].append({"date": date_str, "events": doc["events_count"]})
        
    return result

@router.post("/session/{session_id}/risk")
async def manual_risk_analysis(session_id: str, current_driver: dict = Depends(get_current_driver)):
    """Manually trigger Gemini analysis if it failed or was skipped during session end."""
    db = get_database()
    session = await db.sessions.find_one({"_id": ObjectId(session_id), "driver_id": current_driver["_id"]})
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
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
        
    summary = await generate_risk_analysis(session, events_summary)
    
    await db.sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"gemini_risk_summary": summary}}
    )
    
    return {"gemini_risk_summary": summary}
