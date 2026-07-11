from database.db import SessionLocal
from database.models import TelemetryFrame, TrackMap
import json

db = SessionLocal()
tracks = db.query(TrackMap).all()
print(f"Total Tracks in DB: {len(tracks)}")
for t in tracks:
    path = json.loads(t.path_data)
    print(f"Track {t.track_id}: {len(path)} points")

frames = db.query(TelemetryFrame).limit(10).all()
print(f"Total Frames in DB: {db.query(TelemetryFrame).count()}")
if frames:
    f = frames[0]
    print(f"First Frame Pos: ({f.world_pos_x}, {f.world_pos_z})")
    
    # Try distance check
    if tracks:
        t = tracks[0]
        path = json.loads(t.path_data)
        min_dist = float('inf')
        for p in path:
            dist = ((p['x'] - f.world_pos_x)**2 + (p['z'] - f.world_pos_z)**2)**0.5
            if dist < min_dist:
                min_dist = dist
        print(f"Min dist to track: {min_dist}")

db.close()
