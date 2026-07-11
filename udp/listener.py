import asyncio
import socket
from .decoder import decode_packet

UDP_IP = "0.0.0.0"
UDP_PORT = 20777

async def start_udp_listener():
    loop = asyncio.get_running_loop()
    
    # Use standard python socket with asyncio
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(False)
    
    print(f"Listening for F1 telemetry on UDP {UDP_IP}:{UDP_PORT}")
    
    while True:
        try:
            # We wait until the socket is readable
            data, addr = await loop.sock_recvfrom(sock, 2048)
            asyncio.create_task(decode_packet(data))
        except Exception as e:
            print(f"UDP Listener error: {e}")
            await asyncio.sleep(1)
