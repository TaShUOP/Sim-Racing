import asyncio
from .decoder import decode_packet

UDP_IP = "0.0.0.0"
UDP_PORT = 20777

class TelemetryProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport
        print(f"Listening for F1 telemetry on UDP {UDP_IP}:{UDP_PORT}")

    def datagram_received(self, data, addr):
        # Process the packet asynchronously without blocking the UDP listener
        asyncio.create_task(decode_packet(data))
        
    def error_received(self, exc):
        print(f"UDP Protocol error: {exc}")

async def start_udp_listener():
    loop = asyncio.get_running_loop()
    
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: TelemetryProtocol(),
        local_addr=(UDP_IP, UDP_PORT)
    )
    
    try:
        # Keep the listener alive
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        transport.close()
