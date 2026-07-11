from sqlalchemy import Column, Integer, Float, String, ForeignKey
from .db import Base

class SessionLap(Base):
    __tablename__ = "session_laps"

    id = Column(Integer, primary_key=True, index=True)
    session_uid = Column(String, index=True)
    lap_number = Column(Integer)
    lap_time = Column(Float, nullable=True)

class SessionParticipant(Base):
    __tablename__ = "session_participants"

    id = Column(Integer, primary_key=True, index=True)
    session_uid = Column(String, index=True)
    car_index = Column(Integer, index=True)
    name = Column(String)

class TelemetryFrame(Base):
    __tablename__ = "telemetry_frames"

    id = Column(Integer, primary_key=True, index=True)
    session_uid = Column(String, index=True)
    car_index = Column(Integer, index=True)
    lap_number = Column(Integer, index=True)
    session_time = Column(Float, index=True)
    
    speed = Column(Integer)
    throttle = Column(Float)
    brake = Column(Float)
    gear = Column(Integer)
    rpm = Column(Integer)
    
    # Position data for Track Map
    world_pos_x = Column(Float, default=0.0)
    world_pos_y = Column(Float, default=0.0)
    world_pos_z = Column(Float, default=0.0)
