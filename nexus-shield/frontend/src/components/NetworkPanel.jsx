import { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { Shield, Activity, AlertTriangle, Wifi } from 'lucide-react';

const ATTACK_COLORS = {
  dos: { bg: 'bg-red-900/40', border: 'border-red-500', text: 'text-red-400', label: 'DoS ATTACK' },
  portscan: { bg: 'bg-orange-900/40', border: 'border-orange-500', text: 'text-orange-400', label: 'PORT SCAN' },
  bruteforce: { bg: 'bg-yellow-900/40', border: 'border-yellow-500', text: 'text-yellow-400', label: 'BRUTE FORCE' },
};

function AttackBadge({ type }) {
  const cfg = ATTACK_COLORS[type] || ATTACK_COLORS.dos;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold border attack-badge ${cfg.bg} ${cfg.border} ${cfg.text}`}>
      <span className="pulse-dot" style={{ background: 'currentColor', width: 6, height: 6 }} />
      {cfg.label}
    </span>
  );
}

function StatBox({ label, value, color = 'text-cyan-400' }) {
  return (
    <div className="cyber-panel p-3 flex flex-col items-center">
      <div className={`text-xl font-bold ${color} count-animate`}>{value.toLocaleString()}</div>
      <div className="text-xs text-gray-500 mt-0.5">{label}</div>
    </div>
  );
}

const CustomTooltip = ({ active, payload }) => {
  if (active && payload?.length) {
    return (
      <div className="bg-gray-900 border border-cyan-800 rounded px-2 py-1 text-xs">
        <span className="text-cyan-400">{Math.round(payload[0].value).toLocaleString()} pkt/s</span>
      </div>
    );
  }
  return null;
};

export default function NetworkPanel({ data, onSimulateDoS, onSimulatePortScan, loading }) {
  const { packetRateHistory, packetCounter, activeAttack, recentEvents, networkScore } = data;

  const networkEvents = recentEvents.filter((e) => e.source === 'network').slice(0, 8);
  const isUnderAttack = activeAttack !== null;

  const chartColor = isUnderAttack ? '#ff2244' : '#00d4ff';
  const maxRate = Math.max(...packetRateHistory.map((d) => d.rate), 200);

  return (
    <div className={`cyber-panel h-full flex flex-col scan-line ${isUnderAttack ? 'glow-red' : 'glow-cyan'}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-cyber-border">
        <div className="flex items-center gap-2">
          <Shield size={16} className={isUnderAttack ? 'text-red-400' : 'text-cyan-400'} />
          <span className="text-xs font-bold tracking-widest text-cyan-300">NETWORK THREAT MONITOR</span>
        </div>
        <div className="flex items-center gap-2">
          {isUnderAttack && <AttackBadge type={activeAttack} />}
          <div className={`text-xs font-bold px-2 py-0.5 rounded ${
            networkScore > 70 ? 'bg-red-900/50 text-red-400' :
            networkScore > 40 ? 'bg-yellow-900/50 text-yellow-400' :
            'bg-green-900/50 text-green-400'
          }`}>
            {networkScore.toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Packet counters */}
      <div className="grid grid-cols-3 gap-2 p-3">
        <StatBox label="TOTAL" value={packetCounter.total} color="text-cyan-400" />
        <StatBox label="MALICIOUS" value={packetCounter.malicious} color="text-red-400" />
        <StatBox label="SAFE" value={packetCounter.safe} color="text-green-400" />
      </div>

      {/* Live packet rate chart */}
      <div className="px-3 pb-1">
        <div className="flex items-center gap-2 mb-1">
          <Activity size={12} className="text-cyan-500" />
          <span className="text-xs text-gray-400">PACKET RATE (pkt/s)</span>
          <span className={`ml-auto text-xs font-bold ${isUnderAttack ? 'text-red-400' : 'text-cyan-400'}`}>
            {Math.round(packetRateHistory[packetRateHistory.length - 1]?.rate ?? 0).toLocaleString()} pkt/s
          </span>
        </div>
        <div className="h-28">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={packetRateHistory} margin={{ top: 2, right: 4, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#0e2a3a" />
              <XAxis dataKey="time" hide />
              <YAxis domain={[0, maxRate * 1.1]} tick={{ fontSize: 9, fill: '#4a6a7a' }} />
              <Tooltip content={<CustomTooltip />} />
              {isUnderAttack && (
                <ReferenceLine y={1000} stroke="#ff224444" strokeDasharray="4 4" />
              )}
              <Line
                type="monotone"
                dataKey="rate"
                stroke={chartColor}
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Traffic classification */}
      <div className="px-3 pb-2">
        <div className="flex gap-2">
          <div className="flex-1 bg-green-900/20 border border-green-800/50 rounded p-2 text-center">
            <div className="text-xs text-green-400 font-bold">BENIGN</div>
            <div className="text-lg font-bold text-green-300">
              {packetCounter.total > 0
                ? Math.round((packetCounter.safe / packetCounter.total) * 100)
                : 95}%
            </div>
          </div>
          <div className="flex-1 bg-red-900/20 border border-red-800/50 rounded p-2 text-center">
            <div className="text-xs text-red-400 font-bold">ATTACK</div>
            <div className="text-lg font-bold text-red-300">
              {packetCounter.total > 0
                ? Math.round((packetCounter.malicious / packetCounter.total) * 100)
                : 5}%
            </div>
          </div>
        </div>
      </div>

      {/* Simulation buttons */}
      <div className="px-3 pb-2 grid grid-cols-2 gap-2">
        <button
          onClick={onSimulateDoS}
          disabled={loading}
          className="flex items-center justify-center gap-1.5 py-2 px-3 rounded text-xs font-bold
            bg-red-900/40 border border-red-600 text-red-300 hover:bg-red-800/60 hover:text-red-200
            transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
            hover:glow-red active:scale-95"
        >
          <AlertTriangle size={12} />
          SIMULATE DoS
        </button>
        <button
          onClick={onSimulatePortScan}
          disabled={loading}
          className="flex items-center justify-center gap-1.5 py-2 px-3 rounded text-xs font-bold
            bg-orange-900/40 border border-orange-600 text-orange-300 hover:bg-orange-800/60 hover:text-orange-200
            transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
            active:scale-95"
        >
          <Wifi size={12} />
          SIMULATE PORT SCAN
        </button>
      </div>

      {/* Recent events log */}
      <div className="flex-1 px-3 pb-3 overflow-hidden">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="pulse-dot bg-cyan-400" />
          <span className="text-xs text-gray-400 tracking-wider">RECENT EVENTS</span>
        </div>
        <div className="space-y-1 overflow-y-auto max-h-36">
          {networkEvents.length === 0 ? (
            <div className="text-xs text-gray-600 italic">No events — system nominal</div>
          ) : (
            networkEvents.map((evt, i) => (
              <div
                key={evt.id || i}
                className={`timeline-entry flex items-start gap-2 text-xs py-1 px-2 rounded border-l-2 ${
                  evt.severity === 'attack' ? 'border-red-500 bg-red-900/10 text-red-300' :
                  evt.severity === 'warning' ? 'border-yellow-500 bg-yellow-900/10 text-yellow-300' :
                  'border-green-500 bg-green-900/10 text-green-300'
                }`}
              >
                <span className="text-gray-500 shrink-0">
                  {new Date(evt.timestamp * 1000).toLocaleTimeString()}
                </span>
                <span className="truncate">{evt.description}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
