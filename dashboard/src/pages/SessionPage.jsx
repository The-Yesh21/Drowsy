import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { format } from 'date-fns';
import { ArrowLeft, Clock, AlertTriangle, Calendar } from 'lucide-react';

import apiClient from '../api/client';
import StatCard from '../components/cards/StatCard';
import EventTimelineChart from '../components/charts/EventTimelineChart';
import StateDistributionChart from '../components/charts/StateDistributionChart';

const SessionPage = () => {
  const { sessionId } = useParams();
  const [session, setSession] = useState(null);
  const [events, setEvents] = useState([]);
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSessionData = async () => {
      try {
        setIsLoading(true);
        const [sessionRes, eventsRes, summaryRes] = await Promise.all([
          apiClient.get(`/sessions/${sessionId}`),
          apiClient.get(`/events/session/${sessionId}`),
          apiClient.get(`/events/session/${sessionId}/summary`),
        ]);

        setSession(sessionRes.data);
        setEvents(eventsRes.data);
        
        // Transform summary object to Recharts pie format
        const pieData = Object.entries(summaryRes.data).map(([state, data]) => ({
          name: state,
          value: data.count,
        }));
        setSummary(pieData);
      } catch (err) {
        console.error("Failed to fetch session data", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSessionData();
  }, [sessionId]);

  if (isLoading || !session) {
    return (
      <div className="flex justify-center items-center h-64 text-slate-400">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500 mr-3"></div>
        Loading session deep-dive...
      </div>
    );
  }

  const start = new Date(session.start_time);
  const end = session.end_time ? new Date(session.end_time) : null;
  const durationMins = end ? Math.round((end.getTime() - start.getTime()) / 60000) : 'Active';

  return (
    <div className="space-y-6 pb-20">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link to="/analytics" className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-6 h-6" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-white">Session Review</h1>
          <p className="text-sm font-mono text-slate-400 mt-1">{sessionId}</p>
        </div>
      </div>

      {session.gemini_risk_summary && (
        <div className="bg-gradient-to-r from-slate-800 to-slate-900 border border-slate-700 p-6 rounded-lg shadow-xl relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
          <h2 className="text-lg font-bold text-white mb-2">Safety Report</h2>
          <p className="text-slate-300 leading-relaxed max-w-4xl">{session.gemini_risk_summary}</p>
        </div>
      )}

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Date" value={format(start, 'MMM dd')} unit={format(start, 'yyyy')} color="blue" icon={Calendar} />
        <StatCard title="Duration" value={durationMins} unit="mins" color="blue" icon={Clock} />
        <StatCard title="Total Events" value={session.total_events} color="yellow" icon={AlertTriangle} />
        <StatCard title="Critical Events" value={session.critical_events} color="red" icon={AlertTriangle} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline Chart */}
        <div className="lg:col-span-2 bg-slate-800 p-5 rounded-lg border border-slate-700 h-[400px] flex flex-col">
          <h3 className="text-slate-400 font-medium uppercase tracking-wider mb-2">Session Event Timeline</h3>
          <p className="text-xs text-slate-500 mb-4">Scatter plot of all drowsiness events recorded during the trip.</p>
          <div className="flex-1 w-full relative">
            <EventTimelineChart data={events} />
          </div>
        </div>

        {/* State Dist Chart */}
        <div className="bg-slate-800 p-5 rounded-lg border border-slate-700 h-[400px] flex flex-col items-center">
          <h3 className="text-slate-400 font-medium uppercase tracking-wider mb-2 w-full text-left">State Distribution</h3>
          <div className="flex-1 w-full relative">
             <StateDistributionChart data={summary} />
          </div>
        </div>
      </div>

      {/* Raw Data Table */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <div className="p-4 border-b border-slate-700">
             <h3 className="text-slate-400 font-medium uppercase tracking-wider">Raw Telemetry Data</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-slate-300">
            <thead className="text-xs text-slate-400 uppercase bg-slate-900/50">
              <tr>
                <th className="px-6 py-3">Time</th>
                <th className="px-6 py-3">State</th>
                <th className="px-6 py-3">Score</th>
                <th className="px-6 py-3">EAR</th>
                <th className="px-6 py-3">Blinks (bpm)</th>
                <th className="px-6 py-3">Pitch</th>
              </tr>
            </thead>
            <tbody>
              {events.slice(0, 50).map((event) => (
                <tr key={event._id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="px-6 py-3 font-mono">{format(new Date(event.timestamp), 'HH:mm:ss')}</td>
                  <td className={`px-6 py-3 font-bold ${
                    event.state === 'CRITICAL' ? 'text-red-400' :
                    event.state === 'DROWSY' ? 'text-orange-400' :
                    event.state === 'MILD' ? 'text-yellow-400' : 'text-green-400'
                  }`}>
                    {event.state}
                  </td>
                  <td className="px-6 py-3">{event.drowsiness_score.toFixed(3)}</td>
                  <td className="px-6 py-3">{event.ear.toFixed(3)}</td>
                  <td className="px-6 py-3">{event.blink_rate.toFixed(0)}</td>
                  <td className="px-6 py-3">{event.pitch.toFixed(1)}°</td>
                </tr>
              ))}
            </tbody>
          </table>
          {events.length > 50 && (
            <div className="p-4 text-center text-sm text-slate-500 bg-slate-900/20">
              Showing first 50 events. Total events: {events.length}
            </div>
          )}
        </div>
      </div>

    </div>
  );
};

export default SessionPage;
