import React, { useRef, useEffect, useState } from 'react';

export default function AnalysisTrackMap({ telemetryData, sessionUid, opponent }) {
  const canvasRef = useRef(null);
  const [staticMap, setStaticMap] = useState(null);

  useEffect(() => {
    if (!sessionUid) return;
    
    fetch(`http://${window.location.hostname}:1224/api/sessions/${sessionUid}/track`)
      .then(res => res.json())
      .then(data => {
        if (data.path && data.path.length > 0) {
          setStaticMap(data.path);
        }
      })
      .catch(err => console.error(err));
  }, [sessionUid]);

  useEffect(() => {
    if (!staticMap) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Scale and center logic
    const scale = 0.2; 
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    // Draw static map
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.lineWidth = 4;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.shadowBlur = 4;
    ctx.shadowColor = 'rgba(255, 255, 255, 0.2)';
    
    for (let i = 0; i < staticMap.length; i++) {
      const p = staticMap[i];
      const px = centerX + p.x * scale;
      const py = centerY + p.z * scale;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();
    ctx.shadowBlur = 0;
    
    // Draw Braking Overlays
    if (!telemetryData || telemetryData.length === 0) return;
    
    // Draw opponent braking first (underneath)
    if (opponent !== 'none') {
        for (let i = 0; i < telemetryData.length; i++) {
            const frame = telemetryData[i];
            const brake = frame[`brake_${opponent}`];
            if (brake > 0.1) {
                const px = centerX + frame[`world_pos_x_${opponent}`] * scale;
                const pz = centerY + frame[`world_pos_z_${opponent}`] * scale;
                
                ctx.beginPath();
                ctx.arc(px, pz, 3, 0, Math.PI * 2);
                ctx.fillStyle = '#aa00ff'; // Purple for opponent
                ctx.fill();
            }
        }
    }
    
    // Draw player braking on top
    for (let i = 0; i < telemetryData.length; i++) {
        const frame = telemetryData[i];
        const brake = frame.brake_0;
        if (brake > 0.1) {
            const px = centerX + frame.world_pos_x_0 * scale;
            const pz = centerY + frame.world_pos_z_0 * scale;
            
            ctx.beginPath();
            ctx.arc(px, pz, 3, 0, Math.PI * 2);
            ctx.fillStyle = '#e10600'; // Red for player
            ctx.fill();
        }
    }
    
  }, [telemetryData, staticMap, opponent]);

  if (!staticMap) return null;

  return (
    <div className="glass-panel" style={{ marginBottom: '24px' }}>
      <div className="stat-label" style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
        <span>Track Map & Braking Zones</span>
        <div style={{ display: 'flex', gap: '16px', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#e10600' }}></div> Your Braking
            </div>
            {opponent !== 'none' && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#aa00ff' }}></div> Opponent Braking
                </div>
            )}
        </div>
      </div>
      <canvas 
        ref={canvasRef} 
        width={1100} 
        height={400} 
        style={{ width: '100%', height: '400px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}
      />
    </div>
  );
}
