import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Analysis() {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState('');
  const [telemetryData, setTelemetryData] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/sessions')
      .then(res => res.json())
      .then(data => {
        setSessions(data.sessions);
        if (data.sessions.length > 0) {
          setSelectedSession(data.sessions[0]);
        }
      });
  }, []);

  useEffect(() => {
    if (!selectedSession) return;
    fetch(`http://localhost:8000/api/sessions/${selectedSession}?car_index=0`)
      .then(res => res.json())
      .then(data => setTelemetryData(data.data));
  }, [selectedSession]);

  return (
    <div className="dashboard-container" style={{ display: 'block', maxWidth: '1200px', margin: '0 auto' }}>
      <div className="header-banner" style={{ marginBottom: '24px' }}>
        <Link to="/" style={{ color: '#fff', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ArrowLeft size={24} /> Back to Live Dashboard
        </Link>
        <h2>Post-Session Analysis</h2>
      </div>

      <div className="glass-panel" style={{ marginBottom: '24px' }}>
        <div className="stat-label">Select Session</div>
        <select 
          value={selectedSession} 
          onChange={(e) => setSelectedSession(e.target.value)}
          style={{ padding: '8px', marginTop: '8px', background: 'rgba(0,0,0,0.5)', color: '#fff', border: '1px solid #333', borderRadius: '4px', width: '100%', fontFamily: 'Outfit' }}
        >
          {sessions.length === 0 && <option>No sessions found</option>}
          {sessions.map(s => <option key={s} value={s}>Session UID: {s}</option>)}
        </select>
      </div>

      {telemetryData.length > 0 ? (
        <>
          <div className="glass-panel" style={{ marginBottom: '24px' }}>
            <div className="stat-label" style={{ marginBottom: '16px' }}>Speed trace (km/h)</div>
            <div style={{ height: '300px', width: '100%' }}>
              <ResponsiveContainer>
                <LineChart data={telemetryData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="session_time" stroke="#888" tickFormatter={(val) => val.toFixed(1) + 's'} />
                  <YAxis stroke="#888" />
                  <Tooltip contentStyle={{ background: 'rgba(0,0,0,0.8)', border: '1px solid #333', borderRadius: '8px' }} />
                  <Line type="monotone" dataKey="speed" stroke="#2979ff" dot={false} strokeWidth={2} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-panel">
            <div className="stat-label" style={{ marginBottom: '16px' }}>Inputs (Throttle & Brake)</div>
            <div style={{ height: '300px', width: '100%' }}>
              <ResponsiveContainer>
                <LineChart data={telemetryData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="session_time" stroke="#888" tickFormatter={(val) => val.toFixed(1) + 's'} />
                  <YAxis stroke="#888" />
                  <Tooltip contentStyle={{ background: 'rgba(0,0,0,0.8)', border: '1px solid #333', borderRadius: '8px' }} />
                  <Legend />
                  <Line type="step" dataKey="throttle" stroke="#00c853" dot={false} strokeWidth={2} isAnimationActive={false} />
                  <Line type="step" dataKey="brake" stroke="#e10600" dot={false} strokeWidth={2} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      ) : (
        <div className="glass-panel">No telemetry data recorded for this session. Use the Live Dashboard to start recording a session first!</div>
      )}
    </div>
  );
}
