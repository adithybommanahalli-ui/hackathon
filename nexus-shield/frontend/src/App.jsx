import { useState, useEffect, useCallback, useRef } from 'react';
import { Shield, Zap, RotateCcw, Play, Square, Wifi } from 'lucide-react';
import NetworkPanel from './components/NetworkPanel';
import SocialPanel from './components/SocialPanel';
import NexusScore from './components/NexusScore';
import Timeline from './components/Timeline';
import ConvergenceAlert from './components/ConvergenceAlert';
import ThreatAlertContainer, { useThreatAlerts } from './components/ThreatAlert';
import RealTimePanel from './components/RealTimePanel';
import { useWebSocket } from './hooks/useWebSocket';
import { useThreatData } from './hooks/useThreatData';

// Live clock component
function LiveClock() {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return (
    <span className="text-cyan-500 font-mono text-xs">
      {time.toLocaleString('en-US', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: false,
      })}
    </span>
  );
}

// Auto-refresh social analysis every 30 seconds
function useAutoRefresh(callback, interval = 30000, enabled = true) {
  const callbackRef = useRef(callback);
  useEffect(() => { callbackRef.current = callback; }, [callback]);

  useEffect(() => {
    if (!enabled) return;
    const t = setInterval(() => callbackRef.current(), interval);
    return () => clearInterval(t);
  }, [interval, enabled]);
}

export default function App() {
  const [alertDismissed, setAlertDismissed] = useState(false);
  const [currentTopic, setCurrentTopic] = useState('cybersecurity');

  const {
    data,
    updateFromWS,
    simulateDoS,
    simulatePortScan,
    analyzeSocial,
    resetSystem,
    toggleDemo,
  } = useThreatData();

  const { connected, send } = useWebSocket(updateFromWS);
  const { alerts, dismiss, checkForAlerts } = useThreatAlerts();

  // Check for alerts every time data updates
  useEffect(() => {
    checkForAlerts(data);
  }, [data]);

  // Reset dismissed state when convergence alert becomes active
  useEffect(() => {
    if (data.convergenceAlert) setAlertDismissed(false);
  }, [data.convergenceAlert]);

  const handleAnalyzeSocial = useCallback(async (topic) => {
    setCurrentTopic(topic);
    await analyzeSocial(topic);
  }, [analyzeSocial]);

  // Auto-refresh social every 30s
  useAutoRefresh(() => handleAnalyzeSocial(currentTopic), 30000, true);

  const handleReset = useCallback(() => {
    resetSystem(send);
    setAlertDismissed(false);
  }, [resetSystem, send]);

  const handleToggleDemo = useCallback(() => {
    toggleDemo(!data.demoMode, send);
  }, [data.demoMode, toggleDemo, send]);

  const showConvergence = data.convergenceAlert && !alertDismissed;

  const systemStatus = connected
    ? (data.status === 'CRITICAL' ? 'ALERT' : 'ONLINE')
    : 'OFFLINE';

  const statusColor = !connected
    ? 'text-gray-500 bg-gray-900/50 border-gray-700'
    : data.status === 'CRITICAL'
    ? 'text-red-400 bg-red-900/30 border-red-600 attack-badge'
    : data.status === 'CAUTION'
    ? 'text-yellow-400 bg-yellow-900/30 border-yellow-600'
    : 'text-green-400 bg-green-900/30 border-green-600';

  return (
    <div className="min-h-screen grid-bg text-gray-200 flex flex-col" style={{ fontFamily: "'JetBrains Mono', monospace" }}>

      {/* ── TOP NAVBAR ── */}
      <nav className="border-b border-cyber-border bg-black/60 backdrop-blur-sm sticky top-0 z-50">
        <div className="flex items-center justify-between px-4 py-2.5">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <Shield size={28} className="text-cyan-400" style={{ filter: 'drop-shadow(0 0 8px #00d4ff)' }} />
              <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
            </div>
            <div>
              <div className="text-lg font-bold tracking-widest text-white"
                style={{ textShadow: '0 0 20px rgba(0,212,255,0.5)' }}>
                NEXUS <span className="text-cyan-400">SHIELD</span>
              </div>
              <div className="text-xs text-gray-500 tracking-widest -mt-0.5">
                CYBER-SOCIAL INTELLIGENCE PLATFORM
              </div>
            </div>
          </div>

          {/* Center status */}
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 px-3 py-1 rounded border text-xs font-bold ${statusColor}`}>
              <span className={`pulse-dot ${connected ? (data.status === 'CRITICAL' ? 'bg-red-400' : 'bg-green-400') : 'bg-gray-500'}`} />
              {systemStatus}
            </div>
            {data.activeAttack && (
              <div className="flex items-center gap-1.5 px-3 py-1 rounded border border-red-600 bg-red-900/30 text-red-400 text-xs font-bold attack-badge">
                <Zap size={12} />
                {data.activeAttack.toUpperCase()} DETECTED
              </div>
            )}
          </div>

          {/* Right controls */}
          <div className="flex items-center gap-3">
            <LiveClock />

            {/* Demo mode toggle */}
            <button
              onClick={handleToggleDemo}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded border text-xs font-bold transition-all duration-200 active:scale-95 ${
                data.demoMode
                  ? 'bg-purple-900/40 border-purple-500 text-purple-300 hover:bg-purple-800/60'
                  : 'bg-gray-900/40 border-gray-600 text-gray-400 hover:border-purple-600 hover:text-purple-400'
              }`}
            >
              {data.demoMode ? <Square size={11} /> : <Play size={11} />}
              DEMO {data.demoMode ? 'ON' : 'OFF'}
            </button>

            {/* Reset button */}
            <button
              onClick={handleReset}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-gray-600 text-gray-400
                hover:border-cyan-600 hover:text-cyan-400 text-xs font-bold transition-all duration-200 active:scale-95"
            >
              <RotateCcw size={11} />
              RESET
            </button>

            {/* Connection indicator */}
            <div className="flex items-center gap-1.5 text-xs text-gray-500">
              <Wifi size={12} className={connected ? 'text-cyan-500' : 'text-gray-600'} />
              <span>{connected ? 'WS LIVE' : 'RECONNECTING'}</span>
            </div>
          </div>
        </div>
      </nav>

      {/* ── MAIN CONTENT ── */}
      <main className="flex-1 flex flex-col p-3 gap-3 min-h-0">

        {/* Convergence Alert Banner */}
        <ConvergenceAlert
          active={showConvergence}
          onDismiss={() => setAlertDismissed(true)}
        />

        {/* Four-column main panels */}
        <div className="flex gap-3 flex-1 min-h-0" style={{ minHeight: 520 }}>

          {/* LEFT: Network Panel (30%) */}
          <div className="flex-none" style={{ width: '30%' }}>
            <NetworkPanel
              data={data}
              onSimulateDoS={simulateDoS}
              onSimulatePortScan={simulatePortScan}
              loading={data.loading}
            />
          </div>

          {/* CENTER-LEFT: Real-Time Live Data (20%) */}
          <div className="flex-none" style={{ width: '20%' }}>
            <RealTimePanel />
          </div>

          {/* CENTER-RIGHT: Nexus Score (15%) */}
          <div className="flex-none" style={{ width: '15%' }}>
            <NexusScore
              crisisScore={data.crisisScore}
              status={data.status}
              networkScore={data.networkScore}
              emotionScore={data.emotionScore}
            />
          </div>

          {/* RIGHT: Social Panel (35%) */}
          <div className="flex-none" style={{ width: '35%' }}>
            <SocialPanel
              data={data}
              onAnalyze={handleAnalyzeSocial}
              loading={data.loading}
            />
          </div>
        </div>

        {/* BOTTOM: Threat Timeline */}
        <div className="shrink-0">
          <Timeline events={data.recentEvents} />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-cyber-border px-4 py-1.5 flex items-center justify-between text-xs text-gray-600">
        <span>NEXUS SHIELD v1.0 — Real-Time Cybersecurity & Social Intelligence</span>
        <span className="flex items-center gap-2">
          <span className="pulse-dot bg-cyan-500" />
          ML Models: RandomForest IDS + HuggingFace Sentiment
        </span>
        <span>Crisis Score = 0.40×Network + 0.35×Emotion + 0.25×FakeNews</span>
      </footer>

      {/* ── THREAT ALERT POPUPS (top-right, with beep) ── */}
      <ThreatAlertContainer alerts={alerts} onDismiss={dismiss} />
    </div>
  );
}
