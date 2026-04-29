import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart2, AlertCircle, Clock, CalendarDays } from 'lucide-react';

import apiClient from '../api/client';
import { useAuthStore } from '../store/authStore';

import StatCard from '../components/cards/StatCard';
import SessionCard from '../components/cards/SessionCard';
import WeeklyTrendChart from '../components/charts/WeeklyTrendChart';

const AnalyticsPage = () => {
  const driver = useAuthStore((state) => state.driver);
  const navigate = useNavigate();
  
  const [stats, setStats] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!driver?.id) return;
    
    const fetchAnalytics = async () => {
      try {
        setIsLoading(true);
        const [statsRes, sessionsRes] = await Promise.all([
          apiClient.get(`/analytics/driver/${driver.id}`),
          apiClient.get(`/sessions/driver/${driver.id}`)
        ]);

        setStats(statsRes.data);
        setSessions(sessionsRes.data);
      } catch (err) {
        console.error("Failed to fetch analytics", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalytics();
  }, [driver?.id]);

  if (isLoading || !stats) {
    return (
      <div className="flex justify-center items-center h-64 text-slate-400">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500 mr-3"></div>
        Loading driver analytics...
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-20">
      <div className="flex items-center gap-3 mb-8">
        <BarChart2 className="w-8 h-8 text-blue-500" />
        <h1 className="text-2xl font-bold text-white">{driver?.name}'s Safety Profile</h1>
      </div>

      {/* Driver Lifetime Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Trips" value={stats.total_sessions} color="blue" icon={CalendarDays} />
        <StatCard title="Total Events" value={stats.total_events} color="yellow" icon={AlertCircle} />
        <StatCard title="Critical Events" value={stats.critical_events} color="red" icon={AlertCircle} />
        <StatCard title="Avg Score" value={stats.avg_drowsiness_score.toFixed(2)} unit="/1.0" color="orange" icon={Clock} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        
        {/* Trend Graph */}
        <div className="lg:col-span-2 bg-slate-800 p-5 rounded-lg border border-slate-700">
          <h3 className="text-slate-400 font-medium uppercase tracking-wider mb-2">Weekly Drowsiness Trend</h3>
          <p className="text-xs text-slate-500 mb-2">Total events recorded vs strictly critical events per day.</p>
          <WeeklyTrendChart data={stats.trend_7_days} />
        </div>

        {/* Recent Session History */}
        <div className="bg-slate-800 p-5 rounded-lg border border-slate-700 flex flex-col h-[400px] overflow-hidden">
          <h3 className="text-slate-400 font-medium uppercase tracking-wider mb-4 border-b border-slate-700 pb-2">
            Trip History
          </h3>
          
          <div className="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar">
            {sessions.length === 0 ? (
              <div className="text-center text-slate-500 py-10">No driving sessions recorded yet</div>
            ) : (
              sessions.map((session) => (
                <SessionCard 
                  key={session._id} 
                  session={session} 
                  onClick={() => navigate(`/sessions/${session._id}`)} 
                />
              ))
            )}
          </div>
        </div>
        
      </div>
    </div>
  );
};

export default AnalyticsPage;
