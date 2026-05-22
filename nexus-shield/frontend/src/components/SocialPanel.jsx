import { useState, useRef } from 'react';
import { Globe, Search, Bot, Newspaper, RefreshCw } from 'lucide-react';

function EmotionBar({ label, value, color, bgColor }) {
  const pct = Math.round((value || 0) * 100);
  return (
    <div className="mb-2">
      <div className="flex justify-between text-xs mb-1">
        <span className={`font-medium ${color}`}>{label}</span>
        <span className={`font-bold ${color}`}>{pct}%</span>
      </div>
      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${bgColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function HeadlineFeed({ headlines }) {
  if (!headlines?.length) {
    return <div className="text-xs text-gray-600 italic">No headlines — enter a topic to monitor</div>;
  }
  return (
    <div className="space-y-1.5">
      {headlines.slice(0, 5).map((item, i) => (
        <div
          key={i}
          className="timeline-entry flex items-start gap-2 text-xs py-1.5 px-2 rounded bg-gray-900/50 border border-gray-800 hover:border-cyan-800 transition-colors"
        >
          <span className="pulse-dot bg-cyan-400 mt-1 shrink-0" />
          <span className="text-gray-300 leading-relaxed line-clamp-2">
            {typeof item === 'string' ? item : item.text}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function SocialPanel({ data, onAnalyze, loading }) {
  const [topic, setTopic] = useState('cybersecurity');
  const [lastRefresh, setLastRefresh] = useState(null);
  const inputRef = useRef(null);

  const { emotionBreakdown, fakeNewsRatio, botActivity, recentSocial, emotionScore } = data;

  const handleAnalyze = async () => {
    if (!topic.trim()) return;
    await onAnalyze(topic.trim());
    setLastRefresh(new Date().toLocaleTimeString());
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleAnalyze();
  };

  const fakeNewsPct = Math.round((fakeNewsRatio || 0) * 100);
  const botPct = Math.round((botActivity || 0) * 100);

  return (
    <div className={`cyber-panel h-full flex flex-col ${emotionScore > 70 ? 'glow-red' : 'glow-cyan'}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-cyber-border">
        <div className="flex items-center gap-2">
          <Globe size={16} className="text-cyan-400" />
          <span className="text-xs font-bold tracking-widest text-cyan-300">SOCIAL PULSE MONITOR</span>
        </div>
        <div className={`text-xs font-bold px-2 py-0.5 rounded ${
          emotionScore > 70 ? 'bg-red-900/50 text-red-400' :
          emotionScore > 40 ? 'bg-yellow-900/50 text-yellow-400' :
          'bg-green-900/50 text-green-400'
        }`}>
          {emotionScore.toFixed(0)}%
        </div>
      </div>

      {/* Search box */}
      <div className="p-3 border-b border-cyber-border">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              ref={inputRef}
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter topic to monitor..."
              className="w-full bg-gray-900 border border-gray-700 rounded pl-7 pr-3 py-1.5 text-xs text-gray-200
                placeholder-gray-600 focus:outline-none focus:border-cyan-600 transition-colors"
            />
          </div>
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="flex items-center gap-1 px-3 py-1.5 rounded text-xs font-bold
              bg-cyan-900/40 border border-cyan-600 text-cyan-300 hover:bg-cyan-800/60
              transition-all duration-200 disabled:opacity-50 active:scale-95"
          >
            <RefreshCw size={11} className={loading ? 'animate-spin' : ''} />
            SCAN
          </button>
        </div>
        {lastRefresh && (
          <div className="text-xs text-gray-600 mt-1">Last scan: {lastRefresh} · Auto-refresh: 30s</div>
        )}
      </div>

      {/* Emotion breakdown */}
      <div className="p-3 border-b border-cyber-border">
        <div className="text-xs text-gray-400 tracking-wider mb-2">EMOTION BREAKDOWN</div>
        <EmotionBar label="😡 ANGRY" value={emotionBreakdown?.angry} color="text-red-400" bgColor="bg-red-500" />
        <EmotionBar label="😨 FEAR" value={emotionBreakdown?.fear} color="text-orange-400" bgColor="bg-orange-500" />
        <EmotionBar label="😐 NEUTRAL" value={emotionBreakdown?.neutral} color="text-gray-400" bgColor="bg-gray-500" />
        <EmotionBar label="😊 POSITIVE" value={emotionBreakdown?.positive} color="text-green-400" bgColor="bg-green-500" />
      </div>

      {/* Fake news + bot activity */}
      <div className="grid grid-cols-2 gap-2 p-3 border-b border-cyber-border">
        <div className="cyber-panel p-2">
          <div className="flex items-center gap-1.5 mb-1">
            <Newspaper size={11} className="text-yellow-400" />
            <span className="text-xs text-gray-400">FAKE NEWS</span>
          </div>
          <div className="flex items-end gap-1">
            <span className={`text-xl font-bold ${fakeNewsPct > 40 ? 'text-red-400' : fakeNewsPct > 20 ? 'text-yellow-400' : 'text-green-400'}`}>
              {fakeNewsPct}%
            </span>
          </div>
          <div className="h-1.5 bg-gray-800 rounded-full mt-1.5 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                fakeNewsPct > 40 ? 'bg-red-500' : fakeNewsPct > 20 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${fakeNewsPct}%` }}
            />
          </div>
        </div>
        <div className="cyber-panel p-2">
          <div className="flex items-center gap-1.5 mb-1">
            <Bot size={11} className="text-purple-400" />
            <span className="text-xs text-gray-400">BOT ACTIVITY</span>
          </div>
          <div className="flex items-end gap-1">
            <span className={`text-xl font-bold ${botPct > 30 ? 'text-red-400' : botPct > 15 ? 'text-yellow-400' : 'text-green-400'}`}>
              {botPct}%
            </span>
          </div>
          <div className="h-1.5 bg-gray-800 rounded-full mt-1.5 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                botPct > 30 ? 'bg-red-500' : botPct > 15 ? 'bg-yellow-500' : 'bg-purple-500'
              }`}
              style={{ width: `${botPct}%` }}
            />
          </div>
        </div>
      </div>

      {/* Live headline feed */}
      <div className="flex-1 p-3 overflow-hidden">
        <div className="flex items-center gap-2 mb-2">
          <span className="pulse-dot bg-cyan-400" />
          <span className="text-xs text-gray-400 tracking-wider">LIVE HEADLINES</span>
        </div>
        <div className="overflow-y-auto max-h-48">
          <HeadlineFeed headlines={recentSocial} />
        </div>
      </div>
    </div>
  );
}
