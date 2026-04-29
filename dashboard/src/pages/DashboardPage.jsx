import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { Play, Square, Activity, Eye, EyeOff, Timer } from 'lucide-react';

import apiClient from '../api/client';
import { useWebSocket } from '../hooks/useWebSocket';
import { useSessionStore } from '../store/sessionStore';
import { useAuthStore } from '../store/authStore';

import StatCard from '../components/cards/StatCard';
import AlertCard from '../components/cards/AlertCard';
import LiveStatusBadge from '../components/live/LiveStatusBadge';
import LiveMetricsBar from '../components/live/LiveMetricsBar';
import DrowsinessScoreChart from '../components/charts/DrowsinessScoreChart';

const DashboardPage = () => {
  const driver = useAuthStore((state) => state.driver);
  const { activeSessionId, setActiveSession, clearActiveSession } = useSessionStore();
  
  const [sessionData, setSessionData] = useState(null);
  const [isStarting, setIsStarting] = useState(false);
  const [isEnding, setIsEnding] = useState(false);
  const [geminiSummary, setGeminiSummary] = useState(null);

  // Hook into WebSocket
  const { isConnected, latestEvent, eventHistory } = useWebSocket(activeSessionId);

  // Derived state from WS history
  const recentEventsDisplay = [...eventHistory].slice(0, 20); // Last 20 for feed
  const currentRiskScore = latestEvent ? latestEvent.drowsiness_score : 0;
  const currentBlinkRate = latestEvent ? latestEvent.blink_rate : 0;
  
  // Track live session duration
  const [durationMins, setDurationMins] = useState(0);

  useEffect(() => {
    if (activeSessionId && sessionData?.start_time) {
      const interval = setInterval(() => {
        const start = new Date(sessionData.start_time);
        const now = new Date();
        const diffMs = now.getTime() - start.getTime();
        setDurationMins(Math.max(0, Math.floor(diffMs / 60000)));
      }, 10000);
      return () => clearInterval(interval);
    }
  }, [activeSessionId, sessionData]);

  // Handle Session Start/End
  const handleStartSession = async () => {
    setIsStarting(true);
    setGeminiSummary(null);
    try {
      const res = await apiClient.post('/sessions/start');
      const sessionId = res.data.session_id;
      setActiveSession(sessionId);
      
      const sessionRes = await apiClient.get(`/sessions/${sessionId}`);
      setSessionData(sessionRes.data);
      setDurationMins(0);
      toast.success('Live driving session started');
      
      // Stage 4 Automation: Remotely spin up the webcam python script 
      try {
        await apiClient.post(`/camera/start?session_id=${sessionId}&driver_id=${driver.id}`);
        toast.success('Webcam initialized automatically');
      } catch (camErr) {
        toast.error('Failed to auto-start webcam. You may need to run it manually.');
        console.error(camErr);
      }

    } catch (err) {
      toast.error('Failed to start session');
      console.error(err);
    } finally {
      setIsStarting(false);
    }
  };

  const handleEndSession = async () => {
    if (!activeSessionId) return;
    setIsEnding(true);
    try {
      const res = await apiClient.post(`/sessions/${activeSessionId}/end`);
      clearActiveSession();
      setSessionData(null);
      
      // Stage 4 Automation: Remotely kill the webcam python script 
      try {
         await apiClient.post(`/camera/stop`);
      } catch (camErr) {
         console.warn("Camera stop issue: ", camErr);
      }
      
      if (res.data.gemini_risk_summary) {
        setGeminiSummary(res.data.gemini_risk_summary);
      }
      toast.success('Session ended. Analysis ready.');
    } catch (err) {
      toast.error('Failed to end session');
      console.error(err);
    } finally {
      setIsEnding(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* HEADER & CONTROLS */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-800 p-5 rounded-lg border border-slate-700">
        <div>
          <h1 className="text-2xl font-bold text-white">Live Dashboard</h1>
          <p className="text-slate-400 text-sm">
            {activeSessionId 
              ? `Session ID: ${activeSessionId}` 
              : "No active session. Start a session to connect telemetry."}
          </p>
        </div>
        
        <div className="flex gap-4">
          {!activeSessionId ? (
            <button
              onClick={handleStartSession}
              disabled={isStarting}
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-bold transition-all"
            >
              <Play className="w-5 h-5" />
              {isStarting ? "Starting..." : "Start Session"}
            </button>
          ) : (
            <button
              onClick={handleEndSession}
              disabled={isEnding}
              className="flex items-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-500 rounded-lg text-white font-bold animate-pulse transition-all"
            >
              <Square className="w-5 h-5" />
              {isEnding ? "Ending..." : "End Session"}
            </button>
          )}
        </div>
      </div>

      {geminiSummary && (
        <div className="bg-gradient-to-r from-blue-900/40 to-indigo-900/40 border border-blue-500/30 p-6 rounded-lg shadow-xl relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
          <h2 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
            ✨ Gemini AI Safety Analysis
          </h2>
          <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">{geminiSummary}</p>
        </div>
      )}

      {/* STAT CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Connection" 
          value={isConnected ? "LIVE" : "WAITING"} 
          color={isConnected ? "green" : "yellow"}
          icon={Activity}
        />
        <StatCard 
          title="Drowsiness Score" 
          value={currentRiskScore.toFixed(2)} 
          unit="/ 1.0"
          color={currentRiskScore > 0.5 ? "red" : currentRiskScore > 0.3 ? "orange" : "blue"}
          icon={EyeOff}
        />
        <StatCard 
          title="Blink Rate" 
          value={currentBlinkRate.toFixed(0)} 
          unit="bpm"
          color="blue"
          icon={Eye}
        />
        <StatCard 
          title="Session Duration" 
          value={durationMins} 
          unit="mins"
          color="blue"
          icon={Timer}
        />
      </div>

      {/* MAIN VIEW */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* LEFT COLUMN: Data viz */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-800 p-5 rounded-lg border border-slate-700 h-[360px] flex flex-col">
            <h3 className="text-slate-400 font-medium uppercase tracking-wider mb-4">Risk Probability Curve</h3>
            <div className="flex-1 w-full relative">
              <DrowsinessScoreChart data={[...eventHistory].reverse()} />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-center justify-center p-6 bg-slate-800 rounded-lg border border-slate-700 min-h-[200px]">
              <LiveStatusBadge state={latestEvent?.state} />
            </div>
            
            <LiveMetricsBar 
              ear={latestEvent?.ear} 
              mar={latestEvent?.mar} 
              pitch={latestEvent?.pitch} 
            />
          </div>
        </div>
        
        {/* RIGHT COLUMN: Event Feed */}
        <div className="bg-slate-800 rounded-lg border border-slate-700 flex flex-col h-[600px] overflow-hidden">
          <div className="p-4 border-b border-slate-700 bg-slate-800 z-10">
            <h3 className="text-slate-400 font-medium uppercase tracking-wider flex justify-between">
              <span>Live Telemetry</span>
              <span className="text-xs bg-slate-700 text-slate-300 px-2 py-1 rounded">Latest events</span>
            </h3>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
             {recentEventsDisplay.length === 0 ? (
               <div className="h-full flex items-center justify-center text-slate-500 pb-10">
                 Waiting for camera telemetry...
               </div>
             ) : (
               recentEventsDisplay.map((ev, idx) => (
                 <AlertCard key={`${ev.timestamp}-${idx}`} event={ev} />
               ))
             )}
          </div>
        </div>
      </div>
      
    </div>
  );
};

export default DashboardPage;
