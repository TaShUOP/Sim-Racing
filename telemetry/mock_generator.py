import socket
import struct
import time
import math

UDP_IP = "127.0.0.1"
UDP_PORT = 20777

HEADER_FORMAT = "<HBBBBBQfIIBB"
CAR_TELEMETRY_DATA_FORMAT = "<HfffBbHBBH4H4B4BH4f4B"
CAR_MOTION_DATA_FORMAT = "<ffffffhhhhhhffffff"

def generate_header(packet_id: int, tick: int) -> bytes:
    return struct.pack(
        HEADER_FORMAT, 2024, 24, 1, 0, 1, packet_id,
        1234567890, tick * 0.05, tick, tick, 0, 255
    )

def generate_mock_telemetry(tick: int) -> bytes:
    header = generate_header(6, tick)
    cars_data = b""
    for i in range(22):
        if i == 0:
            speed = int(150 + math.sin(tick * 0.05) * 100)
            throttle = (math.sin(tick * 0.05) + 1) / 2
            brake = (math.cos(tick * 0.05) + 1) / 2 if throttle < 0.1 else 0
            gear = 4 + int(speed / 60)
            rpm = 10000 + int(math.sin(tick * 0.2) * 2000)
            engine_temp = 95 + int(math.sin(tick * 0.01) * 10)
        else:
            speed, throttle, brake, gear, rpm, engine_temp = 100, 0.5, 0.0, 3, 8000, 90
            
        car_bytes = struct.pack(
            CAR_TELEMETRY_DATA_FORMAT, speed, throttle, 0.0, brake, 0, gear, rpm, 0, 0, 0,
            200, 200, 200, 200, 90, 90, 90, 90, 100, 100, 100, 100, engine_temp,
            22.5, 22.5, 22.5, 22.5, 0, 0, 0, 0
        )
        cars_data += car_bytes
    trailer = struct.pack("<BBB", 255, 255, gear)
    return header + cars_data + trailer

def generate_mock_motion(tick: int) -> bytes:
    header = generate_header(0, tick)
    cars_data = b""
    for i in range(22):
        # All cars move in circles, staggered
        radius = 500
        # Give each car a different starting angle based on index
        angle = (tick * 0.005) - (i * 0.15)
        
        # If it's a "ghost/opponent" car, maybe add some variance
        if i != 0:
            radius += (i * 2) # Spread them out slightly
            
        x = math.cos(angle) * radius
        y = 0.0
        z = math.sin(angle) * radius
            
        car_bytes = struct.pack(
            CAR_MOTION_DATA_FORMAT,
            x, y, z, 0.0, 0.0, 0.0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        )
        cars_data += car_bytes
    return header + cars_data

def start_generator():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Starting mock UDP telemetry on {UDP_IP}:{UDP_PORT}")
    tick = 0
    try:
        while True:
            sock.sendto(generate_mock_motion(tick), (UDP_IP, UDP_PORT))
            sock.sendto(generate_mock_telemetry(tick), (UDP_IP, UDP_PORT))
            tick += 1
            time.sleep(1/60) # 60Hz
    except KeyboardInterrupt:
        print("Mock generator stopped.")

if __name__ == "__main__":
    start_generator()
