from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database.db import init_db, SessionLocal
from database.models import TelemetryFrame, SessionParticipant, TrackMap
from api import websocket
import json
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
        time_map[t][f"world_pos_x_{idx}"] = frame.world_pos_x
        time_map[t][f"world_pos_z_{idx}"] = frame.world_pos_z

    data = sorted(list(time_map.values()), key=lambda x: x["session_time"])
    
    # Decimate the grouped rows
    return {"data": data[::10]}

@app.get("/api/sessions/{session_uid}/track")
def get_session_track_map(session_uid: str):
    db = SessionLocal()
    frame = db.query(TelemetryFrame).filter_by(session_uid=session_uid).first()
    tracks = db.query(TrackMap).all()
    db.close()
    
    if not frame or not tracks:
        return {"path": None}
        
    # Find the matching track map by checking if the session's first frame is near the track path
    for t in tracks:
        path = json.loads(t.path_data)
        if not path: continue
        
        # Check a few points in the path to see if any are close to the frame
        for p in path[::50]:
            dist = ((p['x'] - frame.world_pos_x)**2 + (p['z'] - frame.world_pos_z)**2)**0.5
            if dist < 200: # Within 200 meters of any point on the track
                return {"path": path}
                
    return {"path": None}

class TrackMapRequest(BaseModel):
    path: list

@app.get("/api/tracks/{track_id}")
def get_track_map(track_id: int):
    db = SessionLocal()
    track = db.query(TrackMap).filter_by(track_id=track_id).first()
    db.close()
    if track:
        return {"path": json.loads(track.path_data)}
    return {"path": None}

@app.post("/api/tracks/{track_id}")
def save_track_map(track_id: int, req: TrackMapRequest):
    db = SessionLocal()
    track = db.query(TrackMap).filter_by(track_id=track_id).first()
    if track:
        track.path_data = json.dumps(req.path)
    else:
        track = TrackMap(track_id=track_id, path_data=json.dumps(req.path))
        db.add(track)
    db.commit()
    db.close()
    return {"status": "ok"}
