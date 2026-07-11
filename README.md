# F1 25 Real-Time Telemetry Dashboard

A full-stack, real-time telemetry dashboard for F1 25 (and backwards compatible with F1 24/23). It captures UDP packets broadcasted by the game, parses the binary data using Python, saves every frame into a SQLite database for post-session analysis, and streams it at 60Hz to a premium React glassmorphism dashboard.

## Features
- **Real-Time Glass Dashboard:** Beautiful UI with live speed, gear, RPM LEDs, pedal inputs, and tyre temperatures.
- **Multiplayer Track Map:** Live HTML5 Canvas rendering of your car and all 21 opponents simultaneously on track.
- **Data Persistence:** Records every frame of telemetry for all 22 cars to a SQLite database.
- **Mock Data Generator:** Built-in script to simulate F1 telemetry so you can test the dashboard without running the game.

## Tech Stack
- **Backend:** Python, FastAPI, WebSockets, SQLAlchemy, SQLite
- **Frontend:** React, Vite, HTML5 Canvas, Vanilla CSS

## Setup & Deployment (Docker)

This application is fully containerized into a single Docker image containing both the Nginx React frontend and the Uvicorn Python backend.

### 1. Build and Run the Docker Container
Open a terminal in the `telemetry` folder and build the image:
```bash
docker build -t f1-telemetry:latest .
```

Run the container, making sure to expose the necessary ports:
```bash
docker run -d \
    --restart unless-stopped \
    --name f1-telemetry \
    -p 1223:1223 \
    -p 1224:1224 \
    -p 20777:20777/udp \
    f1-telemetry:latest
```

### 2. Access the Dashboard
Visit `http://localhost:1223` (or replace `localhost` with your machine's IP address to view it on any device on your network).

### 3. Send Telemetry Data
If you are playing F1 25:
- Go to **Settings > Telemetry Settings**
- Enable **UDP Telemetry**
- Set **UDP IP Address** to `127.0.0.1` and **Port** to `20777`

If you want to test without the game, run the mock generator in a third terminal:
```powershell
python mock_generator.py
```
