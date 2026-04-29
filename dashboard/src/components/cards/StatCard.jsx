const StatCard = ({ title, value, unit, color = "blue", icon: Icon }) => {
  const colorMap = {
    blue: "border-l-blue-500 text-blue-400",
    green: "border-l-green-500 text-green-400",
    yellow: "border-l-yellow-500 text-yellow-400",
    red: "border-l-red-500 text-red-400",
    orange: "border-l-orange-500 text-orange-400",
  };

  const bgBorder = colorMap[color] || colorMap.blue;

  return (
    <div className={`bg-slate-800 rounded-lg p-5 shadow-lg border-l-4 ${bgBorder} flex items-center justify-between`}>
      <div>
        <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">{title}</h3>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-white tracking-tight">{value}</span>
          {unit && <span className="text-slate-500 text-sm font-semibold">{unit}</span>}
        </div>
      </div>
      {Icon && (
        <div className={`p-3 rounded-full bg-slate-900/50 ${bgBorder.split(' ')[1]}`}>
          <Icon className="w-6 h-6" />
        </div>
      )}
    </div>
  );
};

export default StatCard;
