import socket
import struct

UDP_IP = "0.0.0.0"
UDP_PORT = 20777

def main():
    print(f"Binding to {UDP_IP}:{UDP_PORT}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind((UDP_IP, UDP_PORT))
    except Exception as e:
        print(f"Failed to bind: {e}")
        print("Make sure your Docker container is stopped so the port is free!")
        return

    import time
    print("Waiting for F1 25 game telemetry... Capturing for 3 minutes.")
    
    packets = []
    start_time = time.time()
    last_print = start_time
    
    # Capture for 3 minutes (180 seconds)
    while time.time() - start_time < 180:
        # Set a timeout so we don't hang forever if game stops sending
        sock.settimeout(1.0)
        try:
            data, addr = sock.recvfrom(2048)
            packets.append(data)
        except socket.timeout:
            continue
            
        current_time = time.time()
        if current_time - last_print >= 10:
            print(f"Captured {len(packets)} packets so far... ({int(current_time - start_time)}/180 seconds)")
            last_print = current_time
            
    print("Capture complete! Saving to raw_telemetry.bin...")
    
    with open("raw_telemetry.bin", "wb") as f:
        for p in packets:
            # Prefix with 4-byte length so we can split it easily
            f.write(len(p).to_bytes(4, byteorder='little'))
            f.write(p)
            
    print("Saved to raw_telemetry.bin successfully.")

if __name__ == "__main__":
    main()
