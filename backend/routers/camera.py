from fastapi import APIRouter, HTTPException, Depends
from services.detector_manager import manager
from routers.auth import get_current_driver

router = APIRouter()

@router.post("/start", status_code=200)
async def start_camera(session_id: str, driver_id: str, current_user=Depends(get_current_driver)):
    """Automatically spawn the computer webcam subprocess using the provided IDs"""
    success = manager.start_detector(session_id=session_id, driver_id=driver_id)
    if not success:
        if manager.is_running():
            raise HTTPException(status_code=400, detail="Camera is already running.")
        else:
            raise HTTPException(status_code=500, detail="Failed to start camera process. Check server logs.")
            
    return {"message": "Camera automated initialization started successfully"}

@router.post("/stop", status_code=200)
async def stop_camera(current_user=Depends(get_current_driver)):
    """Gracefully terminate the webcam subprocess"""
    success = manager.stop_detector()
    if not success:
        # It's fine if it was already closed manually by user pressing 'q'
        return {"message": "Camera was already stopped.", "status": "no_action"}
        
    return {"message": "Camera gracefully terminated."}
