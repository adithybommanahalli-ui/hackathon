import { useEffect, useRef } from 'react';
import { Clock, Shield, Globe } from 'lucide-react';

const SEVERITY_CONFIG = {
  safe: {
    dot: 'bg-green-400',
    border: 'border-green-800',
    bg: 'bg-green-900/10',
    text: 'text-green-300',
    label: 'SAFE',
  },
  warning: {
    dot: 'bg-yellow-400',
    border: 'border-yellow-800',
    bg: 'bg-yellow-900/10',
    text: 'text-yellow-300',
    label: 'WARN',
  },
  attack: {
    dot: 'bg-red-400',
    border: 'border-red-800',
    bg: 'bg-red-900/10',
    text: 'text-red-300',
    label: 'ATTACK',
  },
};

function TimelineEntry({ event }) {
  const cfg = SEVERITY_CONFIG[event.severity] || SEVERITY_CONFIG.safe;
  const time = new Date(event.timestamp * 1000).toLocaleTimeString();
  const isNetwork = event.source === 'network';

  return (
    <div className={`timeline-entry flex items-center gap-3 px-3 py-2 rounded border ${cfg.border} ${cfg.bg} shrink-0`}
      style={{ minWidth: 280 }}>
      {/* Source icon */}
      <div className="shrink-0">
        {isNetwork
          ? <Shield size={12} className={cfg.text} />
          : <Globe size={12} className={cfg.text} />
        }
      </div>

      {/* Dot */}
      <div className={`pulse-dot ${cfg.dot} shrink-0`} />

      {/* Severity badge */}
      <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${cfg.text} bg-black/30 shrink-0`}>
        {cfg.label}
      </span>

      {/* Description */}
      <span className={`text-xs ${cfg.text} truncate flex-1`}>
        {event.description}
      </span>

      {/* Time */}
      <span className="text-xs text-gray-600 shrink-0 flex items-center gap-1">
        <Clock size={10} />
        {time}
      </span>
    </div>
  );
}

export default function Timeline({ events }) {
  const scrollRef = useRef(null);
  const prevLengthRef = useRef(0);

  // Auto-scroll when new events arrive
  useEffect(() => {
    if (events.length > prevLengthRef.current && scrollRef.current) {
      scrollRef.current.scrollLeft = 0;
    }
    prevLengthRef.current = events.length;
  }, [events.length]);

  return (
    <div className="cyber-panel p-3">
      <div className="flex items-center gap-2 mb-2">
        <Clock size={14} className="text-cyan-400" />
        <span className="text-xs font-bold tracking-widest text-cyan-300">THREAT TIMELINE</span>
        <span className="text-xs text-gray-600 ml-auto">{events.length} events</span>
        <div className="flex items-center gap-3 ml-4">
          <span className="flex items-center gap-1 text-xs text-green-400">
            <span className="w-2 h-2 rounded-full bg-green-400 inline-block" /> SAFE
          </span>
          <span className="flex items-center gap-1 text-xs text-yellow-400">
            <span className="w-2 h-2 rounded-full bg-yellow-400 inline-block" /> WARNING
          </span>
          <span className="flex items-center gap-1 text-xs text-red-400">
            <span className="w-2 h-2 rounded-full bg-red-400 inline-block" /> ATTACK
          </span>
        </div>
      </div>

      {/* Horizontal scrolling timeline */}
      <div
        ref={scrollRef}
        className="flex gap-2 overflow-x-auto pb-1"
        style={{ scrollBehavior: 'smooth' }}
      >
        {events.length === 0 ? (
          <div className="text-xs text-gray-600 italic py-2 px-3">
            No events recorded — system monitoring active
          </div>
        ) : (
          events.map((evt, i) => (
            <TimelineEntry key={evt.id || i} event={evt} />
          ))
        )}
      </div>
    </div>
  );
}
