import { useEffect, useRef, useState } from 'react';

const RADIUS = 80;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;
const GAP_DEGREES = 60; // degrees cut from bottom
const ARC_DEGREES = 360 - GAP_DEGREES;
const ARC_LENGTH = (ARC_DEGREES / 360) * CIRCUMFERENCE;

function getScoreColor(score) {
  if (score <= 40) return { stroke: '#00ff88', text: 'text-green-400', glow: '#00ff8844' };
  if (score <= 70) return { stroke: '#ffcc00', text: 'text-yellow-400', glow: '#ffcc0044' };
  return { stroke: '#ff2244', text: 'text-red-400', glow: '#ff224444' };
}

function getStatusConfig(status) {
  switch (status) {
    case 'SECURE': return { color: 'text-green-400', bg: 'bg-green-900/30', border: 'border-green-600' };
    case 'CAUTION': return { color: 'text-yellow-400', bg: 'bg-yellow-900/30', border: 'border-yellow-600' };
    case 'CRITICAL': return { color: 'text-red-400', bg: 'bg-red-900/30', border: 'border-red-600' };
    default: return { color: 'text-gray-400', bg: 'bg-gray-900/30', border: 'border-gray-600' };
  }
}

export default function NexusScore({ crisisScore, status, networkScore, emotionScore }) {
  const [displayScore, setDisplayScore] = useState(crisisScore);
  const animRef = useRef(null);
  const prevScore = useRef(crisisScore);

  // Animate score changes
  useEffect(() => {
    const start = prevScore.current;
    const end = crisisScore;
    if (start === end) return;

    const duration = 800;
    const startTime = performance.now();

    const animate = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = start + (end - start) * eased;
      setDisplayScore(Math.round(current * 10) / 10);

      if (progress < 1) {
        animRef.current = requestAnimationFrame(animate);
      } else {
        prevScore.current = end;
      }
    };

    animRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animRef.current);
  }, [crisisScore]);

  const colors = getScoreColor(displayScore);
  const statusCfg = getStatusConfig(status);

  // Calculate arc offset (0 score = full arc, 100 = no arc)
  const rotation = 90 + GAP_DEGREES / 2; // start from bottom-left
  const fillRatio = displayScore / 100;
  const dashOffset = ARC_LENGTH * (1 - fillRatio);

  const isCritical = status === 'CRITICAL';

  return (
    <div className={`cyber-panel h-full flex flex-col items-center justify-center p-4 ${
      isCritical ? 'glow-red' : status === 'CAUTION' ? 'glow-yellow' : 'glow-green'
    }`}>
      {/* Title */}
      <div className="text-xs font-bold tracking-widest text-cyan-300 mb-4">NEXUS SCORE</div>

      {/* Circular gauge */}
      <div className="relative" style={{ width: 200, height: 200 }}>
        <svg width="200" height="200" viewBox="0 0 200 200">
          {/* Glow filter */}
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Background track */}
          <circle
            cx="100" cy="100" r={RADIUS}
            fill="none"
            stroke="#0e2a3a"
            strokeWidth="12"
            strokeDasharray={`${ARC_LENGTH} ${CIRCUMFERENCE}`}
            strokeDashoffset={0}
            strokeLinecap="round"
            transform={`rotate(${rotation} 100 100)`}
          />

          {/* Score arc */}
          <circle
            cx="100" cy="100" r={RADIUS}
            fill="none"
            stroke={colors.stroke}
            strokeWidth="12"
            strokeDasharray={`${ARC_LENGTH} ${CIRCUMFERENCE}`}
            strokeDashoffset={dashOffset}
            strokeLinecap="round"
            transform={`rotate(${rotation} 100 100)`}
            filter="url(#glow)"
            className="score-transition"
          />

          {/* Tick marks */}
          {[0, 25, 50, 75, 100].map((tick) => {
            const angle = (rotation + (tick / 100) * ARC_DEGREES) * (Math.PI / 180);
            const innerR = RADIUS - 10;
            const outerR = RADIUS + 4;
            const x1 = 100 + innerR * Math.cos(angle);
            const y1 = 100 + innerR * Math.sin(angle);
            const x2 = 100 + outerR * Math.cos(angle);
            const y2 = 100 + outerR * Math.sin(angle);
            return (
              <line key={tick} x1={x1} y1={y1} x2={x2} y2={y2}
                stroke="#1a3a4a" strokeWidth="2" />
            );
          })}
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className={`text-5xl font-bold ${colors.text} transition-all duration-300`}
            style={{ textShadow: `0 0 20px ${colors.glow}` }}>
            {Math.round(displayScore)}
          </div>
          <div className="text-xs text-gray-500 mt-1">/ 100</div>
        </div>
      </div>

      {/* Status badge */}
      <div className={`mt-3 px-4 py-1.5 rounded border text-sm font-bold tracking-widest ${statusCfg.color} ${statusCfg.bg} ${statusCfg.border} ${
        isCritical ? 'attack-badge' : ''
      }`}>
        {status}
      </div>

      {/* Sub-scores */}
      <div className="w-full mt-4 space-y-2">
        <div className="flex justify-between items-center text-xs">
          <span className="text-gray-500">Network Threat</span>
          <div className="flex items-center gap-2">
            <div className="w-20 h-1.5 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-cyan-500 rounded-full transition-all duration-700"
                style={{ width: `${networkScore}%` }}
              />
            </div>
            <span className="text-cyan-400 w-8 text-right">{networkScore.toFixed(0)}%</span>
          </div>
        </div>
        <div className="flex justify-between items-center text-xs">
          <span className="text-gray-500">Social Anger</span>
          <div className="flex items-center gap-2">
            <div className="w-20 h-1.5 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-orange-500 rounded-full transition-all duration-700"
                style={{ width: `${emotionScore}%` }}
              />
            </div>
            <span className="text-orange-400 w-8 text-right">{emotionScore.toFixed(0)}%</span>
          </div>
        </div>
      </div>

      {/* Score formula hint */}
      <div className="mt-4 text-center">
        <div className="text-xs text-gray-600 leading-relaxed">
          <div>0.40 × Network</div>
          <div>+ 0.35 × Emotion</div>
          <div>+ 0.25 × FakeNews</div>
        </div>
      </div>
    </div>
  );
}
