import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import connect_to_mongo, close_mongo_connection

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Drowsiness Detector API",
    description="Real-time ingestion and Gemini AI risk analysis for drowsiness events.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from routers import auth, drivers, sessions, events, analytics, camera
from services.websocket_manager import manager
from fastapi import WebSocket, WebSocketDisconnect

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(drivers.router, prefix="/drivers", tags=["drivers"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(camera.router, prefix="/camera", tags=["camera"])

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            # We keep the connection open to send events to them
            # We don't expect messages from the client in this app
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)

@app.get("/")
async def root():
    return {"status": "running", "version": "1.0"}
