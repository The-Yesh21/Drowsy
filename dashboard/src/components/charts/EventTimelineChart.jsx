import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ZAxis } from 'recharts';
import { format } from 'date-fns';

const COLORS = {
  ALERT: '#22c55e',
  MILD: '#eab308',
  DROWSY: '#f97316',
  CRITICAL: '#ef4444',
};

const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const timeStr = data.timestamp ? format(new Date(data.timestamp), 'HH:mm:ss') : '';
      
      return (
        <div className="bg-slate-800 border border-slate-700 p-3 rounded shadow-xl z-50">
          <p className="text-slate-300 text-sm mb-1">{timeStr}</p>
          <p className="text-white font-bold tracking-wider">{data.state}</p>
          <p className="text-slate-400 text-sm mt-1">Score: {data.drowsiness_score.toFixed(3)}</p>
        </div>
      );
    }
    return null;
  };

const EventTimelineChart = ({ data }) => {
  // Format data for scatter
  const formattedData = data.map(item => ({
    ...item,
    timeMs: new Date(item.timestamp).getTime()
  }));

  if (!formattedData.length) return <div className="h-48 flex items-center justify-center text-slate-500">No events</div>;

  const minTime = Math.min(...formattedData.map(d => d.timeMs));
  const maxTime = Math.max(...formattedData.map(d => d.timeMs));

  return (
    <div className="h-64 w-full mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          
          <XAxis 
            type="number" 
            dataKey="timeMs" 
            domain={[minTime, maxTime]}
            tickFormatter={(tick) => format(new Date(tick), 'HH:mm:ss')}
            stroke="#94a3b8" 
            fontSize={12}
            tickCount={8}
            name="Time"
          />
          
          <YAxis 
            type="number" 
            dataKey="drowsiness_score" 
            domain={[0, 1]} 
            stroke="#94a3b8" 
            fontSize={12}
            tickCount={5}
            name="Score"
          />
          
          {/* ZAxis handles dot size */}
          <ZAxis type="number" range={[40, 40]} />

          <Tooltip cursor={{ strokeDasharray: '3 3', stroke: '#cbd5e1' }} content={<CustomTooltip />} />
          
          <Scatter data={formattedData} isAnimationActive={false}>
            {formattedData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.state] || '#94a3b8'} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EventTimelineChart;
