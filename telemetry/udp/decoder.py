from typing import Callable, Awaitable, Any
from .packets import parse_header, parse_car_telemetry, parse_motion, PacketHeader, CarTelemetryPacket, MotionPacket

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
    except Exception as e:
        print(f"Error decoding packet: {e}")
