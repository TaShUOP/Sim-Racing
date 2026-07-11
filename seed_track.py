import json
from database.db import SessionLocal, init_db
from database.models import TrackMap

def seed():
    init_db()
    
    with open("frontend/public/track_path.json", "r") as f:
        path = json.load(f)
        
    db = SessionLocal()
    track = db.query(TrackMap).filter_by(track_id=3).first()
    if not track:
        track = TrackMap(track_id=3, path_data=json.dumps(path))
        db.add(track)
    else:
        track.path_data = json.dumps(path)
        
    db.commit()
    db.close()
    print("Seeded track map for Bahrain (ID 3)")

if __name__ == "__main__":
    seed()
