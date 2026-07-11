import json
import math
from udp.decoder import decode_packet
import asyncio

class TrackExtractor:
    def __init__(self):
        self.car_paths = [[] for _ in range(22)]
        self.track_id = -1
        
    async def process(self, packet):
        from udp.packets import MotionPacket
        # We don't have SessionPacket parsed yet, so track_id will be unknown.
        # But we can just assume this is Bahrain for now or extract the generic path.
        if isinstance(packet, MotionPacket):
            for i in range(22):
                x = packet.car_motion_data[i].world_position_x
                z = packet.car_motion_data[i].world_position_z
                if x != 0.0 and z != 0.0:
                    # Only add point if it moved a bit to reduce size
                    if len(self.car_paths[i]) == 0:
                        self.car_paths[i].append({'x': round(x, 2), 'z': round(z, 2)})
                    else:
                        last = self.car_paths[i][-1]
                        dist = math.hypot(last['x'] - x, last['z'] - z)
                        if dist > 5.0: # Every 5 meters
                            self.car_paths[i].append({'x': round(x, 2), 'z': round(z, 2)})

async def main():
    from udp.decoder import _callbacks
    _callbacks.clear()
    
    extractor = TrackExtractor()
    _callbacks.append(extractor.process)
    
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
        
        await decode_packet(packet_data)
        
    # Find the car with the longest path (likely completed the most laps)
    best_car = 0
    max_len = 0
    for i in range(22):
        if len(extractor.car_paths[i]) > max_len:
            max_len = len(extractor.car_paths[i])
            best_car = i
            
    print(f"Best car is {best_car} with {max_len} points.")
    
    # Save the path to a JSON file
    with open("frontend/public/track_path.json", "w") as f:
        json.dump(extractor.car_paths[best_car], f)
    print("Saved to track_path.json")

if __name__ == "__main__":
    asyncio.run(main())
