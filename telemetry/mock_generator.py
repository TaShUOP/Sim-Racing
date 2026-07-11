import socket
import struct
import time
import math

UDP_IP = "127.0.0.1"
UDP_PORT = 20777

# Constants for sizes
HEADER_FORMAT = "<HBBBBBQfIIBB"
CAR_TELEMETRY_DATA_FORMAT = "<HfffBbHBBH4H4B4BH4f4B"
CAR_MOTION_DATA_FORMAT = "<ffffffhhhhhhffffff"

LAP_DATA_FORMAT = "<IIHBHBHBHBfffBBBBBBBBBBBBBBBHHBfB"
PARTICIPANT_DATA_FORMAT = "<BBBBBBB32sBBHBB12s"

NAMES = [
    b"Max Verstappen", b"Sergio Perez", b"Lewis Hamilton", b"George Russell",
    b"Charles Leclerc", b"Carlos Sainz", b"Lando Norris", b"Oscar Piastri",
    b"Fernando Alonso", b"Lance Stroll", b"Esteban Ocon", b"Pierre Gasly",
    b"Alexander Albon", b"Logan Sargeant", b"Yuki Tsunoda", b"Daniel Ricciardo",
    b"Valtteri Bottas", b"Zhou Guanyu", b"Kevin Magnussen", b"Nico Hulkenberg",
    b"Player", b"Rival"
]
NUMBERS = [1, 11, 44, 63, 16, 55, 4, 81, 14, 18, 31, 10, 23, 2, 22, 3, 77, 24, 20, 27, 99, 88]

def generate_header(packet_id, frame_id, session_time):
    # 2025 format, year 25, major 1, minor 0, version 1
    return struct.pack(HEADER_FORMAT, 2025, 25, 1, 0, 1, packet_id, 123456789, session_time, frame_id, frame_id, 0, 255)

def send_participants(sock, frame_id, session_time):
    header = generate_header(4, frame_id, session_time)
    num_active_cars = struct.pack("<B", 22)
    participants_data = b""
    for i in range(22):
        name_bytes = NAMES[i].ljust(32, b'\x00')
        race_number = NUMBERS[i]
        
        # Format: <BBBBBBB32sBBHBB12s
        participant = struct.pack(
            PARTICIPANT_DATA_FORMAT,
            1 if i != 0 else 0, # ai controlled
            i, 255, i % 10, 0, race_number, 1,
            name_bytes,
            1, 1, 0, 1, 1, b'\x00' * 12
        )
        participants_data += participant
    sock.sendto(header + num_active_cars + participants_data, (UDP_IP, UDP_PORT))

def send_lap_data(sock, frame_id, session_time):
    header = generate_header(2, frame_id, session_time)
    laps_data = b""
    for i in range(22):
        # Format: <IIHBHBHBHBfffBBBBBBBBBBBBBBBHHBfB
        # car_position is index 13
        lap = struct.pack(
            LAP_DATA_FORMAT,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0.0, 0.0, 0.0,
            i + 1, # car position! 1 to 22
            1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0,
            0.0, 0
        )
        laps_data += lap
    # +2 bytes for timeTrialPBCarIdx and timeTrialRivalCarIdx
    sock.sendto(header + laps_data + (b'\xff' * 2), (UDP_IP, UDP_PORT)) 

def send_motion(sock, frame_id, session_time):
    header = generate_header(0, frame_id, session_time)
    cars_data = b""
    for i in range(22):
        radius = 500
        angle = (frame_id * 0.005) - (i * 0.15)
        if i != 0:
            radius += (i * 2) 
        x = math.cos(angle) * radius
        y = 0.0
        z = math.sin(angle) * radius
        
        car_bytes = struct.pack(
            CAR_MOTION_DATA_FORMAT,
            x, y, z, 0.0, 0.0, 0.0,
            0, 0, 0, 0, 0, 0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        )
        cars_data += car_bytes
    sock.sendto(header + cars_data, (UDP_IP, UDP_PORT))

def send_telemetry(sock, frame_id, session_time):
    header = generate_header(6, frame_id, session_time)
    cars_data = b""
    for i in range(22):
        speed = 100 + (i * 5)
        throttle = 0.5
        brake = 0.0
        gear = 3
        rpm = 5000 + (i * 100)
        
        car_bytes = struct.pack(
            CAR_TELEMETRY_DATA_FORMAT,
            speed, throttle, 0.0, brake, 0, gear, rpm, 0, 0, 0,
            90, 90, 90, 90, 100, 100, 100, 100, 95, 95, 95, 95, 100,
            22.0, 22.0, 22.0, 22.0, 0, 0, 0, 0
        )
        cars_data += car_bytes
    sock.sendto(header + cars_data + b'\x00\x00\x00', (UDP_IP, UDP_PORT))

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Sending F1 25 Mock Telemetry to {UDP_IP}:{UDP_PORT}")
    
    frame_id = 0
    session_time = 0.0
    
    # Send participants immediately on startup so UI populates instantly
    send_participants(sock, frame_id, session_time)
    
    while True:
        send_motion(sock, frame_id, session_time)
        send_telemetry(sock, frame_id, session_time)
        send_lap_data(sock, frame_id, session_time)
        
        # Participants are sent every 5 seconds (5 * 60 = 300 frames)
        if frame_id % 300 == 0:
            send_participants(sock, frame_id, session_time)
            
        frame_id += 1
        session_time += 0.016 # 60Hz
        time.sleep(0.016)

if __name__ == "__main__":
    main()
