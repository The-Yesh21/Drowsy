import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const COLORS = {
  ALERT: '#22c55e',      // text-green-500
  MILD: '#eab308',       // text-yellow-500
  DROWSY: '#f97316',     // text-orange-500
  CRITICAL: '#ef4444',   // text-red-500
};

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-slate-800 border border-slate-700 py-2 px-3 rounded shadow-xl">
        <p className="text-white font-bold">{data.name}</p>
        <p className="text-slate-300 text-sm">{data.value} events</p>
      </div>
    );
  }
  return null;
};

const StateDistributionChart = ({ data }) => {
  // data expected format: [{ name: 'ALERT', value: 400 }, ...]
  
  if (!data || data.length === 0) {
    return (
      <div className="h-64 w-full flex items-center justify-center text-slate-500">
        No state data available
      </div>
    );
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
            stroke="none"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#94a3b8'} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend verticalAlign="bottom" height={36} iconType="circle" />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StateDistributionChart;
