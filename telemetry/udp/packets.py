import struct
from pydantic import BaseModel
from typing import List

class PacketHeader(BaseModel):
    packet_format: int
    game_year: int
    game_major_version: int
    game_minor_version: int
    packet_version: int
    packet_id: int
    session_uid: int
    session_time: float
    frame_identifier: int
    overall_frame_identifier: int
    player_car_index: int
    secondary_player_car_index: int

class CarTelemetryData(BaseModel):
    speed: int
    throttle: float
    steer: float
    brake: float
    clutch: int
    gear: int
    engine_rpm: int
    drs: int
    rev_lights_percent: int
    rev_lights_bit_value: int
    brakes_temperature: List[int]
    tyres_surface_temperature: List[int]
    tyres_inner_temperature: List[int]
    engine_temperature: int
    tyres_pressure: List[float]
    surface_type: List[int]

class CarTelemetryPacket(BaseModel):
    header: PacketHeader
    car_telemetry_data: List[CarTelemetryData]
    mfd_panel_index: int
    mfd_panel_index_secondary_player: int
    suggested_gear: int

class CarMotionData(BaseModel):
    world_position_x: float
    world_position_y: float
    world_position_z: float

class MotionPacket(BaseModel):
    header: PacketHeader
    car_motion_data: List[CarMotionData]

HEADER_FORMAT = "<HBBBBBQfIIBB"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

CAR_TELEMETRY_DATA_FORMAT = "<HfffBbHBBH4H4B4BH4f4B"
CAR_TELEMETRY_DATA_SIZE = struct.calcsize(CAR_TELEMETRY_DATA_FORMAT)

# Format for one car's motion data: 6 floats, 6 shorts, 6 floats (60 bytes)
CAR_MOTION_DATA_FORMAT = "<ffffffhhhhhhffffff"
CAR_MOTION_DATA_SIZE = struct.calcsize(CAR_MOTION_DATA_FORMAT)

def parse_header(data: bytes) -> PacketHeader:
    unpacked = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
    return PacketHeader(
        packet_format=unpacked[0],
        game_year=unpacked[1],
        game_major_version=unpacked[2],
        game_minor_version=unpacked[3],
        packet_version=unpacked[4],
        packet_id=unpacked[5],
        session_uid=unpacked[6],
        session_time=unpacked[7],
        frame_identifier=unpacked[8],
        overall_frame_identifier=unpacked[9],
        player_car_index=unpacked[10],
        secondary_player_car_index=unpacked[11]
    )

def parse_car_telemetry(data: bytes, header: PacketHeader) -> CarTelemetryPacket:
    offset = HEADER_SIZE
    car_data_list = []
    
    for _ in range(22):
        unpacked = struct.unpack(CAR_TELEMETRY_DATA_FORMAT, data[offset:offset+CAR_TELEMETRY_DATA_SIZE])
        car_data = CarTelemetryData(
            speed=unpacked[0], throttle=unpacked[1], steer=unpacked[2], brake=unpacked[3],
            clutch=unpacked[4], gear=unpacked[5], engine_rpm=unpacked[6], drs=unpacked[7],
            rev_lights_percent=unpacked[8], rev_lights_bit_value=unpacked[9],
            brakes_temperature=list(unpacked[10:14]), tyres_surface_temperature=list(unpacked[14:18]),
            tyres_inner_temperature=list(unpacked[18:22]), engine_temperature=unpacked[22],
            tyres_pressure=list(unpacked[23:27]), surface_type=list(unpacked[27:31])
        )
        car_data_list.append(car_data)
        offset += CAR_TELEMETRY_DATA_SIZE

    mfd, mfd_sec, gear = struct.unpack("<BBB", data[offset:offset+3])
    
    return CarTelemetryPacket(
        header=header, car_telemetry_data=car_data_list,
        mfd_panel_index=mfd, mfd_panel_index_secondary_player=mfd_sec, suggested_gear=gear
    )

def parse_motion(data: bytes, header: PacketHeader) -> MotionPacket:
    offset = HEADER_SIZE
    car_motion_list = []
    
    for _ in range(22):
        unpacked = struct.unpack(CAR_MOTION_DATA_FORMAT, data[offset:offset+CAR_MOTION_DATA_SIZE])
        car_motion = CarMotionData(
            world_position_x=unpacked[0],
            world_position_y=unpacked[1],
            world_position_z=unpacked[2]
        )
        car_motion_list.append(car_motion)
        offset += CAR_MOTION_DATA_SIZE
        
    return MotionPacket(header=header, car_motion_data=car_motion_list)
