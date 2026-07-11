from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
from udp.decoder import register_callback
from udp.packets import CarTelemetryPacket, MotionPacket, LapPacket, ParticipantsPacket

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_data(self, data: dict):
        if not self.active_connections:
            return
            
        for connection in list(self.active_connections):
            try:
                await connection.send_json(data)
            except WebSocketDisconnect:
                self.disconnect(connection)
            except Exception as e:
                print(f"Error sending websocket data: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

async def on_new_packet(packet):
    if isinstance(packet, CarTelemetryPacket):
        payload = {
            "type": "telemetry",
            "player_index": packet.header.player_car_index,
            "cars": []
        }
        for i in range(22):
            data = packet.car_telemetry_data[i]
            payload["cars"].append({
                "speed": data.speed,
                "throttle": data.throttle,
                "brake": data.brake,
                "gear": data.gear,
                "rpm": data.engine_rpm,
                "drs": data.drs,
                "brakes_temp": data.brakes_temperature,
                "tyres_surface_temp": data.tyres_surface_temperature,
                "engine_temp": data.engine_temperature
            })
        await manager.broadcast_data(payload)
        
    elif isinstance(packet, MotionPacket):
        payload = {
            "type": "motion",
            "player_index": packet.header.player_car_index,
            "cars": []
        }
        for i in range(22):
            motion = packet.car_motion_data[i]
            payload["cars"].append({
                "x": motion.world_position_x,
                "z": motion.world_position_z
            })
        await manager.broadcast_data(payload)
        
    elif isinstance(packet, LapPacket):
        payload = {
            "type": "lap_data",
            "cars": [{"position": data.car_position} for data in packet.lap_data]
        }
        await manager.broadcast_data(payload)
        
    elif isinstance(packet, ParticipantsPacket):
        payload = {
            "type": "participants",
            "cars": [{"name": p.name, "number": p.race_number} for p in packet.participants]
        }
        await manager.broadcast_data(payload)

register_callback(on_new_packet)

@router.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
