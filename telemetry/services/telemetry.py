from database.db import SessionLocal
from database.models import TelemetryFrame
from udp.packets import CarTelemetryPacket, MotionPacket
from udp.decoder import register_callback
import asyncio

_frame_buffer = []
BUFFER_LIMIT = 22 * 60 # 60 frames per second for 22 cars
is_recording = False

# Store the last known position for all 22 cars
_last_known_positions = [{'x': 0.0, 'y': 0.0, 'z': 0.0} for _ in range(22)]

def set_recording(state: bool):
    global is_recording, _frame_buffer
    is_recording = state
    if not state:
        # Flush the buffer when stopping
        if _frame_buffer:
            asyncio.create_task(save_telemetry_batch())

async def save_telemetry_batch():
    global _frame_buffer
    if not _frame_buffer:
        return
        
    frames_to_save = _frame_buffer[:]
    _frame_buffer = []
    
    def _save():
        db = SessionLocal()
        try:
            db.add_all(frames_to_save)
            db.commit()
        except Exception as e:
            print(f"Error saving to DB: {e}")
            db.rollback()
        finally:
            db.close()
            
    await asyncio.to_thread(_save)

async def queue_telemetry_frame(packet):
    global _frame_buffer, _last_known_positions, is_recording
    
    if isinstance(packet, MotionPacket):
        for i in range(22):
            motion = packet.car_motion_data[i]
            _last_known_positions[i] = {
                'x': motion.world_position_x,
                'y': motion.world_position_y,
                'z': motion.world_position_z
            }
            
    elif isinstance(packet, CarTelemetryPacket):
        if not is_recording:
            return
            
        for i in range(22):
            car_data = packet.car_telemetry_data[i]
            pos = _last_known_positions[i]
            
            frame = TelemetryFrame(
                session_uid=str(packet.header.session_uid),
                car_index=i,
                lap_number=1,
                session_time=packet.header.session_time,
                speed=car_data.speed,
                throttle=car_data.throttle,
                brake=car_data.brake,
                gear=car_data.gear,
                rpm=car_data.engine_rpm,
                world_pos_x=pos['x'],
                world_pos_y=pos['y'],
                world_pos_z=pos['z']
            )
            _frame_buffer.append(frame)
            
        if len(_frame_buffer) >= BUFFER_LIMIT:
            asyncio.create_task(save_telemetry_batch())

register_callback(queue_telemetry_frame)
