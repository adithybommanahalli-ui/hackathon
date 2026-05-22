import { useEffect, useRef, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, AreaChart, Area,
} from 'recharts';
import { Activity, Cpu, Wifi, AlertCircle, Globe, Server } from 'lucide-react';

const WS_RT = 'ws://localhost:8000/ws/realtime';

function StatCard({ icon: Icon, label, value, unit, color = 'text-cyan-400', alert = false }) {
  return (
    <div className={`cyber-panel p-2 flex flex-col gap-0.5 ${alert ? 'glow-red border-red-700' : ''}`}>
      <div className="flex items-center gap-1.5 text-xs text-gray-500">
        <Icon size={10} />
        <span>{label}</span>
      </div>
      <div className={`text-lg font-bold ${color}`}>
        {value}<span className="text-xs text-gray-500 ml-1">{unit}</span>
      </div>
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload?.length) {
    return (
      <div className="bg-gray-900 border border-cyan-800 rounded px-2 py-1 text-xs">
        <div className="text-cyan-400">{Math.round(payload[0]?.value ?? 0)} pkt/s</div>
      </div>
    );
  }
  return null;
};

export default function RealTimePanel() {
  const [stats, setStats]       = useState(null);
  const [history, setHistory]   = useState([]);
  const [connected, setConnected] = useState(false);
  const [error, setError]       = useState(null);
  const wsRef   = useRef(null);
  const tickRef = useRef(0);

  useEffect(() => {
    let reconnectTimer;

    function connect() {
      try {
        const ws = new WebSocket(WS_RT);
        wsRef.current = ws;

        ws.onopen = () => { setConnected(true); setError(null); };

        ws.onmessage = (e) => {
          const d = JSON.parse(e.data);
          if (d.type !== 'realtime') return;
          tickRef.current += 1;
          setStats(d);
          setHistory(prev => [
            ...prev.slice(-59),
            { t: tickRef.current, rate: d.real_packet_rate ?? 0 },
          ]);
        };

        ws.onclose = () => {
          setConnected(false);
          reconnectTimer = setTimeout(connect, 3000);
        };

        ws.onerror = () => ws.close();
      } catch (e) {
        setError('Cannot connect to backend');
        reconnectTimer = setTimeout(connect, 3000);
      }
    }

    connect();
    return () => {
      clearTimeout(reconnectTimer);
      wsRef.current?.close();
    };
  }, []);

  const threatColor = !stats ? 'text-gray-400'
    : stats.real_threat_level > 70 ? 'text-red-400'
    : stats.real_threat_level > 40 ? 'text-yellow-400'
    : 'text-green-400';

  return (
    <div className="cyber-panel h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-cyber-border">
        <div className="flex items-center gap-2">
          <Activity size={14} className="text-cyan-400" />
          <span className="text-xs font-bold tracking-widest text-cyan-300">
            LIVE SYSTEM MONITOR
          </span>
          <span className="text-xs text-gray-600">— Real Machine Data</span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`pulse-dot ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
          <span className="text-xs text-gray-500">{connected ? 'LIVE' : 'CONNECTING'}</span>
        </div>
      </div>

      {!stats ? (
        <div className="flex-1 flex items-center justify-center text-xs text-gray-600">
          {error ?? 'Connecting to real-time feed...'}
        </div>
      ) : (
        <>
          {/* Stat cards */}
          <div className="grid grid-cols-3 gap-2 p-3">
            <StatCard icon={Activity} label="PACKET RATE"
              value={Math.round(stats.real_packet_rate)} unit="pkt/s"
              color="text-cyan-400" />
            <StatCard icon={Wifi} label="RECV"
              value={stats.bytes_recv_kbps?.toFixed(1)} unit="KB/s"
              color="text-blue-400" />
            <StatCard icon={Wifi} label="SENT"
              value={stats.bytes_sent_kbps?.toFixed(1)} unit="KB/s"
              color="text-purple-400" />
            <StatCard icon={Globe} label="CONNECTIONS"
              value={stats.active_connections} unit="active"
              color="text-teal-400"
              alert={stats.active_connections > 100} />
            <StatCard icon={Cpu} label="CPU"
              value={stats.cpu_percent?.toFixed(0)} unit="%"
              color={stats.cpu_percent > 80 ? 'text-red-400' : 'text-green-400'}
              alert={stats.cpu_percent > 80} />
            <StatCard icon={Server} label="MEMORY"
              value={stats.memory_percent?.toFixed(0)} unit="%"
              color={stats.memory_percent > 85 ? 'text-red-400' : 'text-green-400'} />
          </div>

          {/* Live packet rate chart */}
          <div className="px-3 pb-2">
            <div className="text-xs text-gray-500 mb-1 flex justify-between">
              <span>REAL-TIME PACKET RATE</span>
              <span className={`font-bold ${threatColor}`}>
                THREAT: {stats.real_threat_level?.toFixed(0)}%
              </span>
            </div>
            <div className="h-24">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={history} margin={{ top: 2, right: 4, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="rateGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#00d4ff" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#0e2a3a" />
                  <XAxis dataKey="t" hide />
                  <YAxis tick={{ fontSize: 9, fill: '#4a6a7a' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="rate"
                    stroke="#00d4ff" fill="url(#rateGrad)"
                    strokeWidth={2} dot={false} isAnimationActive={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Suspicious patterns */}
          {stats.suspicious_patterns?.length > 0 && (
            <div className="px-3 pb-2">
              <div className="text-xs text-red-400 font-bold mb-1 flex items-center gap-1">
                <AlertCircle size={11} /> SUSPICIOUS PATTERNS DETECTED
              </div>
              {stats.suspicious_patterns.map((p, i) => (
                <div key={i} className="text-xs bg-red-900/20 border border-red-800 rounded px-2 py-1 mb-1">
                  <span className="text-red-400 font-bold">{p.type}</span>
                  <span className="text-gray-400 ml-2">{p.ip} — {p.connections} connections</span>
                </div>
              ))}
            </div>
          )}

          {/* Active connections */}
          <div className="flex-1 px-3 pb-3 overflow-hidden">
            <div className="text-xs text-gray-500 mb-1.5">TOP ACTIVE CONNECTIONS</div>
            <div className="space-y-1 overflow-y-auto max-h-28">
              {stats.top_connections?.length === 0 ? (
                <div className="text-xs text-gray-700 italic">No active connections</div>
              ) : (
                stats.top_connections?.map((c, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs py-0.5 px-2 rounded bg-gray-900/40 border border-gray-800">
                    <span className="text-cyan-600 w-12 shrink-0">:{c.local_port}</span>
                    <span className="text-gray-500">→</span>
                    <span className="text-gray-300 truncate">{c.remote_ip}:{c.remote_port}</span>
                    <span className="ml-auto text-green-600 text-xs shrink-0">{c.status}</span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Totals footer */}
          <div className="px-3 pb-2 border-t border-cyber-border pt-2 grid grid-cols-2 gap-x-4 text-xs text-gray-600">
            <span>↑ {(stats.total_bytes_sent / 1e6).toFixed(1)} MB sent</span>
            <span>↓ {(stats.total_bytes_recv / 1e6).toFixed(1)} MB recv</span>
            <span>Errors in: {stats.errin}</span>
            <span>Errors out: {stats.errout}</span>
          </div>
        </>
      )}
    </div>
  );
}
