import React, { useRef, useEffect } from 'react';

export default function TrackMap({ motionData }) {
  const canvasRef = useRef(null);
  const pathRef = useRef([]); // Store the historical path for the player

  useEffect(() => {
    if (!motionData || !motionData.cars) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    const { cars, playerIndex } = motionData;
    const playerCar = cars[playerIndex];
    
    // Only add point if player moved significantly to save memory
    const lastPoint = pathRef.current[pathRef.current.length - 1];
    if (playerCar && (!lastPoint || Math.abs(lastPoint.x - playerCar.x) > 1 || Math.abs(lastPoint.z - playerCar.z) > 1)) {
      pathRef.current.push({ x: playerCar.x, z: playerCar.z });
    }

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Setup transform (center and scale)
    const scale = 0.2; // Based on F1 track bounds
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    // Draw historical path for player
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 2;
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
        
        // Skip cars at 0,0 (not spawned or not moving)
        if (car.x === 0 && car.z === 0) continue;
        
        const px = centerX + car.x * scale;
        const py = centerY + car.z * scale;
        
        ctx.beginPath();
        if (i === playerIndex) {
            // Player Car
            ctx.arc(px, py, 5, 0, Math.PI * 2);
            ctx.fillStyle = '#e10600'; // F1 Red
            ctx.shadowBlur = 15;
            ctx.shadowColor = '#e10600';
        } else {
            // Opponent Car
            ctx.arc(px, py, 4, 0, Math.PI * 2);
            ctx.fillStyle = '#2979ff'; // Blue
            ctx.shadowBlur = 5;
            ctx.shadowColor = '#2979ff';
        }
        
        ctx.fill();
        ctx.shadowBlur = 0; // Reset for next draw
    }
    
  }, [motionData]);

  return (
    <div className="glass-panel" style={{ gridColumn: '1 / -1', minHeight: '300px' }}>
      <div className="stat-label" style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
        <span>Live Track Map & Racing Line</span>
        <span>
            <span style={{ color: '#e10600', marginRight: '16px' }}>● You</span>
            <span style={{ color: '#2979ff' }}>● Opponents</span>
        </span>
      </div>
      <canvas 
        ref={canvasRef} 
        width={1100} 
        height={350} 
        style={{ width: '100%', height: '350px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}
      />
    </div>
  );
}
