import React, { useState, useEffect, useRef } from 'react';
import { Activity, Gauge, Zap } from 'lucide-react';
import TrackMap from './TrackMap';
import './index.css';

const INITIAL_TELEMETRY = {
  speed: 0, throttle: 0, brake: 0, gear: 0, rpm: 0, drs: 0,
  brakes_temp: [0, 0, 0, 0], tyres_surface_temp: [0, 0, 0, 0], engine_temp: 0
};

export default function Dashboard() {
  const [telemetry, setTelemetry] = useState(INITIAL_TELEMETRY);
  const [motionData, setMotionData] = useState({ cars: [], playerIndex: 0 });
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    wsRef.current = new WebSocket('ws://localhost:8000/ws/telemetry');
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
    <div className="dashboard-container">
      <div className="header-banner">
        <h2>
          <Activity size={24} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '8px', color: 'var(--accent)' }} />
          F1 25 LIVE TELEMETRY
        </h2>
        <div className={`status-indicator ${connected ? '' : 'disconnected'}`}>
          <div className="status-dot"></div>
          {connected ? 'CONNECTED (60Hz)' : 'DISCONNECTED'}
        </div>
      </div>
      
      <TrackMap motionData={motionData} />

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
