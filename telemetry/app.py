from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database.db import init_db, SessionLocal
from database.models import TelemetryFrame
from api import websocket
from services import telemetry
import asyncio
from udp.listener import start_udp_listener

app = FastAPI(title="F1 25 Telemetry Backend")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(websocket.router)

@app.on_event("startup")
async def startup_event():
    # Initialize SQLite database
    init_db()
    # Start UDP listener in background
    asyncio.create_task(start_udp_listener())

class RecordRequest(BaseModel):
    is_recording: bool

@app.post("/api/recording")
async def toggle_recording(req: RecordRequest):
    telemetry.set_recording(req.is_recording)
    return {"status": "ok", "is_recording": telemetry.is_recording}

@app.get("/api/sessions")
def get_sessions():
    db = SessionLocal()
    sessions = db.query(TelemetryFrame.session_uid).distinct().all()
    db.close()
    return {"sessions": [s[0] for s in sessions]}

@app.get("/api/sessions/{session_uid}")
def get_session_data(session_uid: str, car_index: int = 0):
    db = SessionLocal()
    frames = db.query(TelemetryFrame).filter(
        TelemetryFrame.session_uid == session_uid,
        TelemetryFrame.car_index == car_index
    ).order_by(TelemetryFrame.session_time).all()
    db.close()
    
    # Decimate data (take 1 every 10 frames) to prevent freezing the frontend chart
    # 60Hz / 10 = 6Hz (plenty for high-level graphing)
    return {"data": frames[::10]}
