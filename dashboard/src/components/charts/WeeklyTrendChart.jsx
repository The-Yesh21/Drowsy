import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-800 border border-slate-700 p-3 rounded shadow-xl">
        <p className="text-white font-bold mb-2">{label}</p>
        <p className="text-blue-400 text-sm">Total Events: <span className="text-white font-mono">{payload[0].value}</span></p>
        {payload[1] && (
          <p className="text-red-400 text-sm mt-1">Critical Events: <span className="text-white font-mono">{payload[1].value}</span></p>
        )}
      </div>
    );
  }
  return null;
};

const WeeklyTrendChart = ({ data }) => {
  // data format: [{ date: 'Mon', total_events: 120, critical_events: 5 }, ...]
  
  if (!data || data.length === 0) {
    return (
      <div className="h-64 w-full flex items-center justify-center text-slate-500">
        No trend data available
      </div>
    );
  }

  return (
    <div className="h-72 w-full mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 20, right: 30, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis 
            dataKey="date" 
            stroke="#94a3b8" 
            fontSize={12}
            tickMargin={10}
            axisLine={false}
            tickLine={false}
          />
          <YAxis 
            stroke="#94a3b8" 
            fontSize={12}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: '#334155', opacity: 0.4 }} />
          <Legend verticalAlign="top" height={36} />
          
          <Bar dataKey="total_events" name="Total Events" stackId="a" fill="#3b82f6" radius={[0, 0, 4, 4]} />
          <Bar dataKey="critical_events" name="Critical Events" stackId="a" fill="#ef4444" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default WeeklyTrendChart;
