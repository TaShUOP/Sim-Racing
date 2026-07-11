import React, { useEffect, useState, useRef } from 'react';

export default function Leaderboard({ participants, lapData, playerIndex }) {
  const [animations, setAnimations] = useState({}); // { index: 'up' | 'down' }
  const prevPositions = useRef({});

  useEffect(() => {
    if (!lapData || lapData.length === 0) return;
    
    const newAnimations = { ...animations };
    let changed = false;

    lapData.forEach((data, index) => {
      const currentPos = data.position;
      const prevPos = prevPositions.current[index];

      if (prevPos && prevPos !== currentPos && currentPos > 0) {
        if (currentPos < prevPos) {
          // Moved UP the board (lower number = better position)
          newAnimations[index] = 'up';
          changed = true;
          // Clear after 5 seconds
          setTimeout(() => {
            setAnimations(prev => ({ ...prev, [index]: null }));
          }, 5000);
        } else if (currentPos > prevPos) {
          // Moved DOWN
          newAnimations[index] = 'down';
          changed = true;
          setTimeout(() => {
            setAnimations(prev => ({ ...prev, [index]: null }));
          }, 5000);
        }
      }
      prevPositions.current[index] = currentPos;
    });

    if (changed) {
      setAnimations(newAnimations);
    }
  }, [lapData]);

  if (!participants || participants.length === 0) return (
    <div className="glass-panel" style={{ gridRow: 'span 4' }}>
      <div className="stat-label">LEADER BOARD</div>
      <div style={{ marginTop: '20px', color: 'var(--text-muted)' }}>Waiting for participant data...</div>
    </div>
  );

  const board = participants.map((p, i) => ({
    index: i,
    name: p.name,
    number: p.number,
    position: lapData[i] ? lapData[i].position : 0
  }))
  .filter(p => p.position > 0 && p.name !== "Unknown")
  .sort((a, b) => a.position - b.position);

  return (
    <div className="glass-panel leaderboard-panel" style={{ display: 'flex', flexDirection: 'column', gap: '8px', gridRow: 'span 4' }}>
      <div className="stat-label" style={{ marginBottom: '8px', color: 'var(--accent)' }}>LEADER BOARD</div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {board.map((driver) => {
          const isPlayer = driver.index === playerIndex;
          const anim = animations[driver.index];
          
          return (
            <div key={driver.index} style={{
              display: 'flex', alignItems: 'center', padding: '8px 12px',
              background: isPlayer ? 'rgba(225, 6, 0, 0.15)' : 'rgba(0,0,0,0.4)',
              borderRadius: '6px', 
              borderLeft: isPlayer ? '4px solid var(--accent)' : '4px solid #555',
              border: isPlayer ? '1px solid rgba(225,6,0,0.3)' : '1px solid transparent',
              borderLeftWidth: '4px',
              transition: 'transform 0.1s ease',
              transform: isPlayer ? 'scale(1.02)' : 'none'
            }}>
              <span style={{ width: '28px', color: 'var(--text-muted)', fontSize: '0.9rem', fontWeight: 600 }}>
                {driver.position}
              </span>
              <span style={{ width: '20px', display: 'flex', justifyContent: 'center' }}>
                {anim === 'up' && <span style={{ color: '#00c853', fontSize: '0.8rem' }}>▲</span>}
                {anim === 'down' && <span style={{ color: '#e10600', fontSize: '0.8rem' }}>▼</span>}
              </span>
              <span style={{ width: '36px', fontFamily: 'Outfit', fontWeight: '800', color: isPlayer ? '#fff' : '#ccc' }}>
                {driver.number}
              </span>
              <span style={{ flexGrow: 1, textTransform: 'uppercase', fontSize: '0.85rem', fontWeight: isPlayer ? 700 : 500, letterSpacing: '0.5px' }}>
                {driver.name}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
