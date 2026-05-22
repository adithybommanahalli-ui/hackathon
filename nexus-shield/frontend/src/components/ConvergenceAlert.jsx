import { AlertTriangle, X } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function ConvergenceAlert({ active, onDismiss }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (active) {
      setVisible(true);
    } else {
      // Fade out after a delay
      const t = setTimeout(() => setVisible(false), 500);
      return () => clearTimeout(t);
    }
  }, [active]);

  if (!visible) return null;

  return (
    <div className={`convergence-flash border-2 border-red-500 rounded-lg mx-0 mb-3 transition-all duration-300 ${
      active ? 'opacity-100' : 'opacity-0'
    }`}>
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-3">
          {/* Flashing icon */}
          <div className="relative">
            <AlertTriangle size={24} className="text-red-400 animate-pulse" />
            <div className="absolute inset-0 rounded-full bg-red-500/20 animate-ping" />
          </div>

          <div>
            <div className="text-red-300 font-bold text-sm tracking-wide">
              ⚠️ COORDINATED THREAT DETECTED
            </div>
            <div className="text-red-400/80 text-xs mt-0.5">
              Simultaneous cyber attack and public panic surge — CONVERGENCE ALERT ACTIVE
            </div>
          </div>
        </div>

        {/* Threat indicators */}
        <div className="flex items-center gap-4 mr-4">
          <div className="text-center">
            <div className="text-xs text-gray-500">CYBER</div>
            <div className="text-red-400 font-bold text-sm">HIGH</div>
          </div>
          <div className="w-px h-8 bg-red-800" />
          <div className="text-center">
            <div className="text-xs text-gray-500">SOCIAL</div>
            <div className="text-red-400 font-bold text-sm">HIGH</div>
          </div>
          <div className="w-px h-8 bg-red-800" />
          <div className="text-center">
            <div className="text-xs text-gray-500">NEXUS</div>
            <div className="text-red-400 font-bold text-sm attack-badge">CRITICAL</div>
          </div>
        </div>

        {/* Dismiss button */}
        <button
          onClick={onDismiss}
          className="p-1.5 rounded hover:bg-red-900/40 text-red-400 hover:text-red-200 transition-colors"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
}
