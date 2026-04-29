import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const timeStr = data.timestamp ? format(new Date(data.timestamp), 'HH:mm:ss') : '';
    
    return (
      <div className="bg-slate-800 border border-slate-700 p-3 rounded shadow-xl">
        <p className="text-slate-300 text-sm mb-1">{timeStr}</p>
        <p className="text-white font-bold">Score: {data.drowsiness_score.toFixed(3)}</p>
        <p className={`text-sm tracking-widest mt-1 ${
          data.state === 'CRITICAL' ? 'text-red-400' :
          data.state === 'DROWSY' ? 'text-orange-400' :
          data.state === 'MILD' ? 'text-yellow-400' : 'text-green-400'
        }`}>
          {data.state}
        </p>
      </div>
    );
  }
  return null;
};

const DrowsinessScoreChart = ({ data }) => {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={(tick) => tick ? format(new Date(tick), 'HH:mm:ss') : ''}
            stroke="#94a3b8" 
            fontSize={12}
            tickMargin={10}
            minTickGap={30}
          />
          <YAxis 
            domain={[0, 1]} 
            stroke="#94a3b8" 
            fontSize={12}
            tickCount={6}
          />
          <Tooltip content={<CustomTooltip />} />
          
          <ReferenceLine y={0.3} stroke="#eab308" strokeDasharray="3 3" opacity={0.5} />
          <ReferenceLine y={0.5} stroke="#ef4444" strokeDasharray="3 3" opacity={0.5} />
          
          <Line 
            type="monotone" 
            dataKey="drowsiness_score" 
            stroke="#3b82f6" 
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 6, fill: '#3b82f6', stroke: '#1e293b', strokeWidth: 2 }}
            isAnimationActive={false} // Disable to prevent jerky re-renders on rapid WS streaming
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DrowsinessScoreChart;
