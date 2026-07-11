import React, { useRef, useEffect } from 'react';

export default function TrackMap({ motionData, participants }) {
  const canvasRef = useRef(null);
  const pathRef = useRef([]); 

  useEffect(() => {
    if (!motionData || !motionData.cars) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    const { cars, playerIndex } = motionData;
    const playerCar = cars[playerIndex];
    
    // Store path
    const lastPoint = pathRef.current[pathRef.current.length - 1];
    if (playerCar && (!lastPoint || Math.abs(lastPoint.x - playerCar.x) > 1 || Math.abs(lastPoint.z - playerCar.z) > 1)) {
      pathRef.current.push({ x: playerCar.x, z: playerCar.z });
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const scale = 0.2; 
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    // Draw racing line trail
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 3;
    for (let i = 0; i < pathRef.current.length; i++) {
      const p = pathRef.current[i];
      const px = centerX + p.x * scale;
      const py = centerY + p.z * scale;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();

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
            // slight y offset for middle baseline alignment in canvas
            ctx.fillText(raceNumber, px, py + 1); 
        }
    }
    
  }, [motionData, participants]);

  return (
    <div className="glass-panel" style={{ gridColumn: 'span 2', minHeight: '300px' }}>
      <div className="stat-label" style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
        <span>Track Map (Driver Tracking)</span>
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
