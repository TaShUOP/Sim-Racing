from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.websocket import router as websocket_router
from udp.listener import start_udp_listener
from database.db import init_db
from services.telemetry import queue_telemetry_frame
from udp.decoder import register_callback
import asyncio

app = FastAPI(title="F1 25 Telemetry Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(websocket_router)

@app.on_event("startup")
async def startup_event():
    init_db()
    
    # Register the DB saving callback
    async def on_new_packet_for_db(packet):
        queue_telemetry_frame(packet)
    
    register_callback(on_new_packet_for_db)
    
    # Start the UDP listener as a background task
    asyncio.create_task(start_udp_listener())
    print("F1 Telemetry backend started and DB initialized.")
