import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('telemetry.db')
        cursor = conn.cursor()
        
        # Check if lap_distance exists
        cursor.execute("PRAGMA table_info(telemetry_frames)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'lap_distance' not in columns:
            print("Adding lap_distance column...")
            cursor.execute("ALTER TABLE telemetry_frames ADD COLUMN lap_distance FLOAT DEFAULT 0.0")
            conn.commit()
            print("Migration successful.")
        else:
            print("Column already exists.")
            
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
