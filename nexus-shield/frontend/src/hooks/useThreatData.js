import { useState, useCallback, useRef } from 'react';

const API_BASE = 'http://localhost:8000';

const initialState = {
  networkScore: 5,
  emotionScore: 15,
  crisisScore: 10,
  status: 'SECURE',
  convergenceAlert: false,
  packetCounter: { total: 0, malicious: 0, safe: 0 },
  packetRate: 50,
  packetRateHistory: Array.from({ length: 20 }, (_, i) => ({
    time: i,
    rate: 40 + Math.random() * 40,
  })),
  activeAttack: null,
  recentEvents: [],
  recentSocial: [],
  emotionBreakdown: { angry: 0.08, fear: 0.07, neutral: 0.55, positive: 0.30 },
  fakeNewsRatio: 0.10,
  botActivity: 0.08,
  demoMode: false,
  loading: false,
};

export function useThreatData() {
  const [data, setData] = useState(initialState);
  const tickRef = useRef(0);

  const updateFromWS = useCallback((msg) => {
    tickRef.current += 1;
    const tick = tickRef.current;

    setData((prev) => {
      // Build packet rate history with timestamp
      const newRate = { time: tick, rate: msg.packet_rate ?? prev.packetRate };
      const history = [
        ...(msg.packet_rate_history
          ? msg.packet_rate_history.map((r, i) => ({ time: tick - msg.packet_rate_history.length + i, rate: r }))
          : prev.packetRateHistory),
      ].slice(-60);

      return {
        ...prev,
        networkScore: msg.network_score ?? prev.networkScore,
        emotionScore: msg.emotion_score ?? prev.emotionScore,
        crisisScore: msg.crisis_score ?? prev.crisisScore,
        status: msg.status ?? prev.status,
        convergenceAlert: msg.convergence_alert ?? prev.convergenceAlert,
        packetCounter: msg.packet_counter ?? prev.packetCounter,
        packetRate: msg.packet_rate ?? prev.packetRate,
        packetRateHistory: history,
        activeAttack: msg.active_attack ?? prev.activeAttack,
        recentEvents: msg.recent_events ?? prev.recentEvents,
        recentSocial: msg.recent_social ?? prev.recentSocial,
        emotionBreakdown: msg.emotion_breakdown ?? prev.emotionBreakdown,
        fakeNewsRatio: msg.fake_news_ratio ?? prev.fakeNewsRatio,
        botActivity: msg.bot_activity ?? prev.botActivity,
      };
    });
  }, []);

  const simulateDoS = useCallback(async () => {
    setData((p) => ({ ...p, loading: true }));
    try {
      const res = await fetch(`${API_BASE}/api/simulate/dos`, { method: 'POST' });
      const json = await res.json();
      return json;
    } catch (e) {
      console.error('DoS simulation error:', e);
      return null;
    } finally {
      setData((p) => ({ ...p, loading: false }));
    }
  }, []);

  const simulatePortScan = useCallback(async () => {
    setData((p) => ({ ...p, loading: true }));
    try {
      const res = await fetch(`${API_BASE}/api/simulate/portscan`, { method: 'POST' });
      const json = await res.json();
      return json;
    } catch (e) {
      console.error('Port scan simulation error:', e);
      return null;
    } finally {
      setData((p) => ({ ...p, loading: false }));
    }
  }, []);

  const analyzeSocial = useCallback(async (topic) => {
    setData((p) => ({ ...p, loading: true }));
    try {
      const res = await fetch(`${API_BASE}/api/social/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      });
      const json = await res.json();
      return json;
    } catch (e) {
      console.error('Social analysis error:', e);
      return null;
    } finally {
      setData((p) => ({ ...p, loading: false }));
    }
  }, []);

  const resetSystem = useCallback(async (send) => {
    try {
      await fetch(`${API_BASE}/api/reset`, { method: 'POST' });
      send?.({ type: 'reset' });
      setData(initialState);
    } catch (e) {
      console.error('Reset error:', e);
    }
  }, []);

  const toggleDemo = useCallback(async (enabled, send) => {
    try {
      await fetch(`${API_BASE}/api/demo/toggle?enabled=${enabled}`, { method: 'POST' });
      send?.({ type: 'set_demo', enabled });
      setData((p) => ({ ...p, demoMode: enabled }));
    } catch (e) {
      console.error('Demo toggle error:', e);
    }
  }, []);

  return {
    data,
    updateFromWS,
    simulateDoS,
    simulatePortScan,
    analyzeSocial,
    resetSystem,
    toggleDemo,
  };
}
