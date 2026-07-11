import struct
from udp.packets import parse_header, LAP_DATA_FORMAT, LAP_DATA_SIZE

def main():
    with open("raw_telemetry.bin", "rb") as f:
        data = f.read()

    offset = 0
    lap_data_found = False
    
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
        
        if header.packet_id == 2: # Lap Data
            lap_offset = 29
            # Let's just look at car 19 (AI) or car 0 (player)
            # Player is usually car 0, let's just look at the first 3 cars
            for i in range(3):
                unpacked = struct.unpack(LAP_DATA_FORMAT, packet_data[lap_offset + i*LAP_DATA_SIZE : lap_offset + (i+1)*LAP_DATA_SIZE])
                print(f"Car {i}:")
                for j, val in enumerate(unpacked):
                    print(f"  [{j}]: {val} ({type(val)})")
                print("-------------")
            break

if __name__ == "__main__":
    main()
