import React, { useState, useEffect, useRef } from 'react';
import { Activity, Gauge, Zap, Play, Square, BarChart2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import TrackMap from './TrackMap';
import Leaderboard from './Leaderboard';
import './index.css';

const INITIAL_TELEMETRY = {
  speed: 0, throttle: 0, brake: 0, gear: 0, rpm: 0, drs: 0,
  brakes_temp: [0, 0, 0, 0], tyres_surface_temp: [0, 0, 0, 0], engine_temp: 0
};

export default function Dashboard() {
  const [telemetry, setTelemetry] = useState(INITIAL_TELEMETRY);
  const [motionData, setMotionData] = useState({ cars: [], playerIndex: 0 });
  const [participants, setParticipants] = useState([]);
  const [lapData, setLapData] = useState([]);
  const [connected, setConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isRecordingLoading, setIsRecordingLoading] = useState(false);
  const [recordingError, setRecordingError] = useState('');
  const wsRef = useRef(null);

  const toggleRecording = () => {
    setIsRecordingLoading(true);
    setRecordingError('');
    const newState = !isRecording;
    fetch('http://' + window.location.hostname + ':1224/api/recording', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_recording: newState })
    })
    .then(res => {
        if (!res.ok) throw new Error('Server error');
        return res.json();
    })
    .then(data => {
        setIsRecording(data.is_recording);
        setIsRecordingLoading(false);
    })
    .catch(err => {
        setRecordingError('Failed to start');
        setIsRecordingLoading(false);
    });
  };

  useEffect(() => {
    wsRef.current = new WebSocket('ws://' + window.location.hostname + ':1224/ws/telemetry');
    wsRef.current.onopen = () => setConnected(true);
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'telemetry') {
        const playerIndex = data.player_index;
        if (data.cars && data.cars[playerIndex]) {
            setTelemetry(data.cars[playerIndex]);
        }
      } else if (data.type === 'motion') {
        setMotionData({ cars: data.cars, playerIndex: data.player_index });
      } else if (data.type === 'participants') {
        setParticipants(data.cars);
      } else if (data.type === 'lap_data') {
        setLapData(data.cars);
      }
    };
    
    wsRef.current.onclose = () => setConnected(false);
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, []);

  const getGearDisplay = (gear) => gear === 0 ? 'N' : gear === -1 ? 'R' : gear;
  const getTyreColor = (temp) => temp < 80 ? '#2979ff' : temp > 105 ? '#e10600' : '#00c853';

  const maxRpm = 12000;
  const rpmPercent = Math.min((telemetry.rpm / maxRpm) * 100, 100);
  const leds = Array.from({ length: 15 }).map((_, i) => {
    const threshold = (i / 15) * 100;
    let colorClass = rpmPercent > threshold ? (i < 5 ? 'green' : i < 10 ? 'red' : 'blue') : '';
    return <div key={i} className={`rpm-led ${colorClass}`} />;
  });

  return (
    <div className="dashboard-container" style={{ gridTemplateColumns: 'minmax(280px, 320px) 1fr 1fr' }}>
      <div className="header-banner">
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={24} style={{ color: 'var(--accent)' }} />
          F1 25 LIVE TELEMETRY
        </h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', position: 'relative' }}>
            <button 
              onClick={toggleRecording}
              disabled={isRecordingLoading}
              style={{ 
                display: 'flex', alignItems: 'center', gap: '6px', 
                padding: '6px 16px', borderRadius: '20px', 
                border: 'none', cursor: isRecordingLoading ? 'wait' : 'pointer', fontWeight: 'bold', fontFamily: 'Outfit',
                background: isRecording ? '#e10600' : '#333', 
                color: '#fff', transition: 'all 0.3s ease',
                boxShadow: isRecording ? '0 0 15px rgba(225,6,0,0.5)' : 'none',
                opacity: isRecordingLoading ? 0.7 : 1
              }}
            >
              {isRecordingLoading ? null : (isRecording ? <Square size={14} fill="#fff" /> : <Play size={14} fill="#fff" />)}
              {isRecordingLoading ? 'PLEASE WAIT...' : (isRecording ? 'RECORDING' : 'START RECORDING')}
            </button>
            {recordingError && <span style={{ position: 'absolute', top: '100%', right: '0', color: '#ff5252', fontSize: '0.75rem', marginTop: '4px', fontWeight: 'bold' }}>{recordingError}</span>}
          </div>
          
          <Link to="/analysis" style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#fff', textDecoration: 'none', padding: '6px 16px', background: 'rgba(255,255,255,0.1)', borderRadius: '20px', fontFamily: 'Outfit', fontWeight: '600' }}>
            <BarChart2 size={16} /> ANALYSIS
          </Link>

          <div className={`status-indicator ${connected ? '' : 'disconnected'}`}>
            <div className="status-dot"></div>
            {connected ? '60Hz' : 'DISCONNECTED'}
          </div>
        </div>
      </div>
      
      {/* Left Column: Leaderboard */}
      <Leaderboard participants={participants} lapData={lapData} playerIndex={motionData.playerIndex} />

      {/* Right Area: Track Map & Dials spanning 2 columns */}
      <TrackMap motionData={motionData} participants={participants} />

      <div className="glass-panel">
        <div className="stat-label">Speed</div>
        <div className="stat-value">{telemetry.speed} <span style={{ fontSize: '1.5rem', color: 'var(--text-muted)' }}>km/h</span></div>
        <div className="rpm-bar">{leds}</div>
        <div className="stat-label" style={{ marginTop: '8px', textAlign: 'center' }}>{telemetry.rpm} RPM</div>
      </div>

      <div className="glass-panel">
        <div className="stat-label">Current Gear</div>
        <div className="gear-display">{getGearDisplay(telemetry.gear)}</div>
      </div>

      <div className="glass-panel">
        <div className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Zap size={16} /> Pedals</div>
        <div style={{ marginTop: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
            <span>Throttle</span><span style={{ fontWeight: 'bold' }}>{Math.round(telemetry.throttle * 100)}%</span>
          </div>
          <div className="bar-container"><div className="bar-fill bar-throttle" style={{ width: `${telemetry.throttle * 100}%` }}></div></div>
        </div>
        <div style={{ marginTop: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
            <span>Brake</span><span style={{ fontWeight: 'bold' }}>{Math.round(telemetry.brake * 100)}%</span>
          </div>
          <div className="bar-container"><div className="bar-fill bar-brake" style={{ width: `${telemetry.brake * 100}%` }}></div></div>
        </div>
      </div>

      <div className="glass-panel">
        <div className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Gauge size={16} /> Tyre Surface Temp</div>
        <div className="tyre-grid">
          {['Front Left', 'Front Right', 'Rear Left', 'Rear Right'].map((label, i) => (
            <div className="tyre" key={label}>
              <span className="tyre-label">{label}</span>
              <span className="tyre-temp" style={{ color: getTyreColor(telemetry.tyres_surface_temp[i]) }}>
                {telemetry.tyres_surface_temp[i]}°C
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
