from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId

from database import get_database
from models.driver import DriverResponse, DriverUpdate
from routers.auth import get_current_driver

router = APIRouter()

@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(driver_id: str, current_driver: dict = Depends(get_current_driver)):
    if str(current_driver["_id"]) != driver_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this profile")
        
    return current_driver

@router.put("/{driver_id}", response_model=DriverResponse)
async def update_driver(driver_id: str, update_data: DriverUpdate, current_driver: dict = Depends(get_current_driver)):
    if str(current_driver["_id"]) != driver_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
        
    db = get_database()
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    if not update_dict:
        return current_driver
        
    await db.drivers.update_one(
        {"_id": ObjectId(driver_id)},
        {"$set": update_dict}
    )
    
    updated_driver = await db.drivers.find_one({"_id": ObjectId(driver_id)})
    return updated_driver
