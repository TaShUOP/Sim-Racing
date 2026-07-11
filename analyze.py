import asyncio
from udp.decoder import decode_packet

async def main():
    try:
        with open("raw_telemetry.bin", "rb") as f:
            data = f.read()
    except Exception as e:
        print(f"Error reading raw_telemetry.bin: {e}")
        return

    offset = 0
    packet_count = 0
    while offset < len(data):
        if offset + 4 > len(data):
            break
        length = int.from_bytes(data[offset:offset+4], byteorder='little')
        offset += 4
        
        packet_data = data[offset:offset+length]
        offset += length
        packet_count += 1
        
        await decode_packet(packet_data)

    print(f"Processed {packet_count} packets through decoder.py")

if __name__ == "__main__":
    asyncio.run(main())
