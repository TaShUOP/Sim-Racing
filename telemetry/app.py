from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database.db import init_db, SessionLocal
from database.models import TelemetryFrame, SessionParticipant
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

@app.get("/api/sessions/{session_uid}/participants")
def get_session_participants(session_uid: str):
    db = SessionLocal()
    participants = db.query(SessionParticipant).filter_by(session_uid=session_uid).all()
    db.close()
    
    res = {p.car_index: p.name for p in participants}
    return {"participants": res}

@app.get("/api/sessions/{session_uid}")
def get_session_data(session_uid: str, car_index: str = "0"):
    db = SessionLocal()
    try:
        car_indices = [int(x) for x in car_index.split(",")]
    except:
        car_indices = [0]
        
    frames = db.query(TelemetryFrame).filter(
        TelemetryFrame.session_uid == session_uid,
        TelemetryFrame.car_index.in_(car_indices)
    ).order_by(TelemetryFrame.session_time).all()
    db.close()
    
    time_map = {}
    for frame in frames:
        t = frame.session_time
        if t not in time_map:
            time_map[t] = {"session_time": t}
        
        idx = frame.car_index
        time_map[t][f"speed_{idx}"] = frame.speed
        time_map[t][f"throttle_{idx}"] = frame.throttle
        time_map[t][f"brake_{idx}"] = frame.brake

    data = sorted(list(time_map.values()), key=lambda x: x["session_time"])
    
    # Decimate the grouped rows
    return {"data": data[::10]}
