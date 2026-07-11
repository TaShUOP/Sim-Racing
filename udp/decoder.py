from typing import Callable, Awaitable, Any
from .packets import parse_header, parse_car_telemetry, parse_motion, parse_lap_data, parse_participants, parse_session, PacketHeader, CarTelemetryPacket, MotionPacket, LapPacket, ParticipantsPacket, SessionPacket

# Observers for new telemetry data
_callbacks = []

def register_callback(callback: Callable[[Any], Awaitable[None]]):
    _callbacks.append(callback)

async def decode_packet(data: bytes):
    if len(data) < 29:
        return # Packet too small
    
    try:
        header = parse_header(data)
        
        # 6 is Car Telemetry Data
        if header.packet_id == 6:
            if len(data) >= 29 + (22 * 60) + 3: 
                car_telemetry = parse_car_telemetry(data, header)
                for callback in _callbacks:
                    await callback(car_telemetry)
                    
        # 0 is Motion Data
        elif header.packet_id == 0:
            if len(data) >= 29 + (22 * 60):
                motion = parse_motion(data, header)
                for callback in _callbacks:
                    await callback(motion)
                    
        # 2 is Lap Data
        elif header.packet_id == 2:
            if len(data) >= 29 + (22 * 57):
                lap_data = parse_lap_data(data, header)
                for callback in _callbacks:
                    await callback(lap_data)
                    
        # 4 is Participants Data
        elif header.packet_id == 4:
            if len(data) >= 29 + 1 + (22 * 57):
                participants = parse_participants(data, header)
                for callback in _callbacks:
                    await callback(participants)
                    
        # 1 is Session Data
        elif header.packet_id == 1:
            if len(data) >= 29 + 8:
                session = parse_session(data, header)
                for callback in _callbacks:
                    await callback(session)
                    
    except Exception as e:
        print(f"Error decoding packet ID {header.packet_id if 'header' in locals() else 'Unknown'}: {e}")
