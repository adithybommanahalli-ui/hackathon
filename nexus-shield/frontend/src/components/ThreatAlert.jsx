import { useEffect, useRef, useState } from 'react';
import { X, AlertTriangle, Shield, Wifi, Zap, Globe } from 'lucide-react';

// ── Web Audio beep generator (no external files needed) ──────────────────────
function playBeep(type = 'attack') {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();

    const configs = {
      attack: [
        { freq: 880, duration: 0.12, delay: 0.00 },
        { freq: 660, duration: 0.12, delay: 0.14 },
        { freq: 880, duration: 0.12, delay: 0.28 },
        { freq: 440, duration: 0.30, delay: 0.42 },
      ],
      convergence: [
        { freq: 1200, duration: 0.10, delay: 0.00 },
        { freq: 1000, duration: 0.10, delay: 0.12 },
        { freq: 1200, duration: 0.10, delay: 0.24 },
        { freq: 1000, duration: 0.10, delay: 0.36 },
        { freq: 800,  duration: 0.40, delay: 0.48 },
      ],
      warning: [
        { freq: 660, duration: 0.15, delay: 0.00 },
        { freq: 550, duration: 0.25, delay: 0.18 },
      ],
    };

    const notes = configs[type] || configs.attack;

    notes.forEach(({ freq, duration, delay }) => {
      const osc    = ctx.createOscillator();
      const gain   = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.type      = 'square';
      osc.frequency.setValueAtTime(freq, ctx.currentTime + delay);

      gain.gain.setValueAtTime(0.18, ctx.currentTime + delay);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + delay + duration);

      osc.start(ctx.currentTime + delay);
      osc.stop(ctx.currentTime + delay + duration + 0.05);
    });
  } catch (e) {
    // AudioContext blocked — silently ignore
  }
}

// ── Alert config per type ─────────────────────────────────────────────────────
const ALERT_CONFIG = {
  dos: {
    icon: Zap,
    title: '⚡ DoS ATTACK DETECTED',
    color: 'border-red-500 bg-red-950/90',
    titleColor: 'text-red-400',
    badge: 'bg-red-500/20 text-red-300 border-red-500',
    beep: 'attack',
    detail: 'Denial-of-Service flood detected. Packet rate spiked abnormally. IDS model flagged malicious traffic.',
  },
  portscan: {
    icon: Wifi,
    title: '🔍 PORT SCAN DETECTED',
    color: 'border-orange-500 bg-orange-950/90',
    titleColor: 'text-orange-400',
    badge: 'bg-orange-500/20 text-orange-300 border-orange-500',
    beep: 'attack',
    detail: 'Sequential port scanning detected. Attacker is mapping open services on this host.',
  },
  bruteforce: {
    icon: Shield,
    title: '🔐 BRUTE FORCE DETECTED',
    color: 'border-yellow-500 bg-yellow-950/90',
    titleColor: 'text-yellow-400',
    badge: 'bg-yellow-500/20 text-yellow-300 border-yellow-500',
    beep: 'attack',
    detail: 'Repeated authentication attempts detected on a single port. Credential stuffing in progress.',
  },
  social: {
    icon: Globe,
    title: '📢 SOCIAL PANIC SURGE',
    color: 'border-orange-500 bg-orange-950/90',
    titleColor: 'text-orange-400',
    badge: 'bg-orange-500/20 text-orange-300 border-orange-500',
    beep: 'warning',
    detail: 'Public anger and fear levels spiked. High volume of negative sentiment and disinformation detected.',
  },
  convergence: {
    icon: AlertTriangle,
    title: '⚠️ COORDINATED THREAT',
    color: 'border-red-500 bg-red-950/95',
    titleColor: 'text-red-300',
    badge: 'bg-red-500/30 text-red-200 border-red-400',
    beep: 'convergence',
    detail: 'SIMULTANEOUS cyber attack AND social panic surge detected. This is a coordinated multi-vector threat.',
  },
  critical: {
    icon: AlertTriangle,
    title: '🔴 SYSTEM CRITICAL',
    color: 'border-red-600 bg-red-950/95',
    titleColor: 'text-red-300',
    badge: 'bg-red-600/30 text-red-200 border-red-500',
    beep: 'convergence',
    detail: 'Crisis score exceeded critical threshold. Immediate response required.',
  },
};

// ── Single popup card ─────────────────────────────────────────────────────────
function AlertCard({ alert, onDismiss }) {
  const cfg = ALERT_CONFIG[alert.type] || ALERT_CONFIG.dos;
  const Icon = cfg.icon;

  return (
    <div className={`
      relative flex flex-col gap-2 p-4 rounded-lg border-2 shadow-2xl
      backdrop-blur-md w-80 animate-slide-in
      ${cfg.color}
    `}>
      {/* Dismiss button */}
      <button
        onClick={() => onDismiss(alert.id)}
        className="absolute top-2 right-2 text-gray-500 hover:text-white transition-colors"
      >
        <X size={14} />
      </button>

      {/* Header */}
      <div className="flex items-center gap-2">
        <div className={`p-1.5 rounded border ${cfg.badge}`}>
          <Icon size={16} />
        </div>
        <span className={`font-bold text-sm tracking-wide ${cfg.titleColor}`}>
          {cfg.title}
        </span>
      </div>

      {/* Detail */}
      <p className="text-xs text-gray-300 leading-relaxed">
        {alert.detail || cfg.detail}
      </p>

      {/* Meta row */}
      <div className="flex items-center justify-between text-xs text-gray-500 border-t border-white/10 pt-2 mt-1">
        <span>{new Date(alert.timestamp).toLocaleTimeString()}</span>
        {alert.score !== undefined && (
          <span className={`font-bold ${cfg.titleColor}`}>
            Crisis: {alert.score.toFixed(1)}/100
          </span>
        )}
      </div>

      {/* Progress bar (auto-dismiss timer) */}
      <div className="h-0.5 bg-white/10 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${alert.type === 'convergence' || alert.type === 'critical' ? 'bg-red-500' : 'bg-orange-500'}`}
          style={{
            animation: `shrink ${alert.duration || 6000}ms linear forwards`,
          }}
        />
      </div>
    </div>
  );
}

// ── Main hook + renderer ──────────────────────────────────────────────────────
export function useThreatAlerts() {
  const [alerts, setAlerts] = useState([]);
  const prevDataRef = useRef({});
  const beepCooldown = useRef({});

  const dismiss = (id) => setAlerts((a) => a.filter((x) => x.id !== id));

  const addAlert = (type, extra = {}) => {
    const now = Date.now();
    // Cooldown: same type can't fire more than once per 8 seconds
    if (beepCooldown.current[type] && now - beepCooldown.current[type] < 8000) return;
    beepCooldown.current[type] = now;

    const cfg = ALERT_CONFIG[type] || ALERT_CONFIG.dos;
    playBeep(cfg.beep);

    const id = `${type}_${now}`;
    const duration = (type === 'convergence' || type === 'critical') ? 10000 : 6000;

    setAlerts((prev) => [
      { id, type, timestamp: now, duration, ...extra },
      ...prev.slice(0, 4), // max 5 alerts
    ]);

    // Auto-dismiss
    setTimeout(() => dismiss(id), duration);
  };

  const checkForAlerts = (data) => {
    const prev = prevDataRef.current;

    // Attack type changed → new attack detected
    if (data.activeAttack && data.activeAttack !== prev.activeAttack) {
      addAlert(data.activeAttack, {
        score: data.crisisScore,
        detail: `IDS model detected ${data.activeAttack.toUpperCase()} attack. ${
          data.packetCounter?.malicious || 0
        } malicious packets flagged.`,
      });
    }

    // Convergence alert fired
    if (data.convergenceAlert && !prev.convergenceAlert) {
      addAlert('convergence', {
        score: data.crisisScore,
      });
    }

    // Status changed to CRITICAL
    if (data.status === 'CRITICAL' && prev.status !== 'CRITICAL') {
      if (!data.convergenceAlert) { // avoid double alert
        addAlert('critical', { score: data.crisisScore });
      }
    }

    // Status changed to CAUTION (first time)
    if (data.status === 'CAUTION' && prev.status === 'SECURE') {
      addAlert('warning', {
        score: data.crisisScore,
        detail: 'Threat levels rising. Network or social signals elevated above baseline.',
      });
    }

    // Social spike
    if (
      data.emotionScore > 60 &&
      (prev.emotionScore || 0) <= 60 &&
      !data.activeAttack
    ) {
      addAlert('social', { score: data.crisisScore });
    }

    prevDataRef.current = { ...data };
  };

  return { alerts, dismiss, checkForAlerts };
}

// ── Alert container (renders in top-right corner) ─────────────────────────────
export default function ThreatAlertContainer({ alerts, onDismiss }) {
  if (!alerts.length) return null;

  return (
    <div className="fixed top-16 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
      {alerts.map((alert) => (
        <div key={alert.id} className="pointer-events-auto">
          <AlertCard alert={alert} onDismiss={onDismiss} />
        </div>
      ))}
    </div>
  );
}
