import React, { useRef, useEffect, useState } from 'react';

export default function TrackMap({ motionData, participants, trackId }) {
  const canvasRef = useRef(null);
  const pathRef = useRef([]); 
  const [staticMap, setStaticMap] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (trackId === -1) return;
    
    // Fetch static map for this track if available
    fetch(`http://${window.location.hostname}:1224/api/tracks/${trackId}`)
      .then(res => res.json())
      .then(data => {
        if (data.path && data.path.length > 0) {
          setStaticMap(data.path);
        } else {
          setStaticMap(null);
          pathRef.current = [];
        }
      })
      .catch(err => console.error(err));
  }, [trackId]);

  useEffect(() => {
    if (!motionData || !motionData.cars) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    const { cars, playerIndex } = motionData;
    const playerCar = cars[playerIndex];
    
    // Trace if no static map
    if (!staticMap && playerCar && playerCar.x !== 0 && playerCar.z !== 0) {
      const lastPoint = pathRef.current[pathRef.current.length - 1];
      if (!lastPoint || Math.abs(lastPoint.x - playerCar.x) > 1 || Math.abs(lastPoint.z - playerCar.z) > 1) {
        pathRef.current.push({ x: playerCar.x, z: playerCar.z });
        
        // Auto-save the map once we have a decent chunk of data (approx a full lap)
        if (pathRef.current.length > 800 && !isSaving && trackId !== -1) {
          setIsSaving(true);
          fetch(`http://${window.location.hostname}:1224/api/tracks/${trackId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: pathRef.current })
          })
          .then(() => setStaticMap([...pathRef.current]))
          .catch(err => console.error(err));
        }
      }
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const scale = 0.2; 
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    // Draw pristine static map or trace
    const pathToDraw = staticMap || pathRef.current;
    if (pathToDraw.length > 0) {
        ctx.beginPath();
        ctx.strokeStyle = staticMap ? 'rgba(255, 255, 255, 0.4)' : 'rgba(255, 255, 255, 0.2)';
        ctx.lineWidth = staticMap ? 10 : 3;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';
        if (staticMap) {
            ctx.shadowBlur = 10;
            ctx.shadowColor = 'rgba(255, 255, 255, 0.2)';
        }
        
        for (let i = 0; i < pathToDraw.length; i++) {
          const p = pathToDraw[i];
          const px = centerX + p.x * scale;
          const py = centerY + p.z * scale;
          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.stroke();
        ctx.shadowBlur = 0; // reset
    }

    // Draw all cars
    for (let i = 0; i < cars.length; i++) {
        const car = cars[i];
        if (car.x === 0 && car.z === 0) continue;
        
        const px = centerX + car.x * scale;
        const py = centerY + car.z * scale;
        
        const isPlayer = i === playerIndex;
        const raceNumber = (participants && participants[i]) ? participants[i].number : '';
        
        // Glow effect
        ctx.shadowBlur = isPlayer ? 10 : 4;
        ctx.shadowColor = isPlayer ? '#e10600' : '#000';
        
        ctx.beginPath();
        ctx.arc(px, py, isPlayer ? 10 : 8, 0, Math.PI * 2);
        ctx.fillStyle = isPlayer ? '#e10600' : 'rgba(30,30,40,0.9)';
        ctx.strokeStyle = isPlayer ? '#fff' : '#666';
        ctx.lineWidth = isPlayer ? 2 : 1;
        ctx.fill();
        ctx.stroke();
        
        ctx.shadowBlur = 0; // Reset for text
        
        if (raceNumber) {
            ctx.fillStyle = '#fff';
            ctx.font = isPlayer ? 'bold 10px Outfit' : 'bold 9px Outfit';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(raceNumber, px, py + 1); 
        }
    }
    
  }, [motionData, participants, staticMap, trackId]);

  return (
    <div className="glass-panel" style={{ gridColumn: 'span 2', minHeight: '300px' }}>
      <div className="stat-label" style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
        <span>Track Map (Driver Tracking)</span>
        <span style={{ color: staticMap ? '#00c853' : '#ffb300' }}>
            {staticMap ? 'Static Map Cached' : (trackId !== -1 ? 'Tracing Lap...' : 'Waiting for Data')}
        </span>
      </div>
      <canvas 
        ref={canvasRef} 
        width={750} 
        height={350} 
        style={{ width: '100%', height: '350px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}
      />
    </div>
  );
}
