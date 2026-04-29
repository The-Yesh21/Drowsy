import { format } from 'date-fns';
import { Calendar, Clock, AlertTriangle } from 'lucide-react';

const SessionCard = ({ session, onClick }) => {
  const { start_time, end_time, total_events, critical_events, gemini_risk_summary } = session;
  
  const start = new Date(start_time);
  const end = end_time ? new Date(end_time) : null;
  
  const durationStr = end 
    ? `${Math.round((end.getTime() - start.getTime()) / 60000)} mins`
    : 'Active';

  // Determine risk level badge from gemini summary if it exists
  let riskBadge = null;
  if (gemini_risk_summary) {
    const summaryUpper = gemini_risk_summary.toUpperCase();
    if (summaryUpper.includes('CRITICAL RISK')) {
      riskBadge = <span className="px-2 py-1 text-xs font-bold bg-red-500/20 text-red-500 rounded border border-red-500/30">CRITICAL</span>;
    } else if (summaryUpper.includes('HIGH RISK')) {
      riskBadge = <span className="px-2 py-1 text-xs font-bold bg-orange-500/20 text-orange-500 rounded border border-orange-500/30">HIGH</span>;
    } else if (summaryUpper.includes('MEDIUM RISK')) {
      riskBadge = <span className="px-2 py-1 text-xs font-bold bg-yellow-500/20 text-yellow-500 rounded border border-yellow-500/30">MEDIUM</span>;
    } else if (summaryUpper.includes('LOW RISK')) {
      riskBadge = <span className="px-2 py-1 text-xs font-bold bg-green-500/20 text-green-500 rounded border border-green-500/30">LOW</span>;
    }
  }

  return (
    <div 
      onClick={onClick}
      className="bg-slate-800 border border-slate-700 hover:border-blue-500/50 rounded-lg p-5 cursor-pointer transition-all hover:shadow-lg group"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2 text-slate-300">
          <Calendar className="w-4 h-4 text-blue-400 group-hover:text-blue-300" />
          <span className="font-medium group-hover:text-white transition-colors">
            {format(start, 'MMM dd, yyyy')}
          </span>
        </div>
        <div>
          {riskBadge}
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <Clock className="w-4 h-4" />
          <span>{format(start, 'HH:mm')} ({durationStr})</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <AlertTriangle className={`w-4 h-4 ${critical_events > 0 ? 'text-red-400' : 'text-slate-500'}`} />
          <span>{total_events} events ({critical_events} critical)</span>
        </div>
      </div>
    </div>
  );
};

export default SessionCard;
