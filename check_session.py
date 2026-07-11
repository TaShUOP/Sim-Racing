import struct
from udp.packets import parse_header

def main():
    with open("raw_telemetry.bin", "rb") as f:
        data = f.read()

    offset = 0
    while offset < len(data):
        if offset + 4 > len(data):
            break
        length = int.from_bytes(data[offset:offset+4], byteorder='little')
        offset += 4
        packet_data = data[offset:offset+length]
        offset += length
        
        if len(packet_data) < 29:
            continue
            
        header = parse_header(packet_data)
        
        if header.packet_id == 1:
            if len(packet_data) >= 29 + 8:
                track_id = struct.unpack_from('<b', packet_data, 29 + 7)[0]
                print(f"Found Session Packet! Track ID: {track_id}")
                break

if __name__ == "__main__":
    main()
