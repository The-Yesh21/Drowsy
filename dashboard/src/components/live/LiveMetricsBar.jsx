const ProgressBar = ({ label, value, max, threshold = null }) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  let colorClass = "bg-blue-500";
  if (threshold) {
    if (value < threshold.danger) colorClass = "bg-red-500";
    else if (value < threshold.warning) colorClass = "bg-yellow-500";
    else colorClass = "bg-green-500";
  }

  return (
    <div className="mb-4 last:mb-0">
      <div className="flex justify-between mb-1">
        <span className="text-sm font-medium text-slate-300">{label}</span>
        <span className="text-sm font-mono text-slate-400">{value.toFixed(2)}</span>
      </div>
      <div className="w-full bg-slate-700 rounded-full h-2">
        <div
          className={`${colorClass} h-2 rounded-full transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};

const LiveMetricsBar = ({ ear, mar, pitch }) => {
  return (
    <div className="bg-slate-800 rounded-lg p-5 shadow-lg border border-slate-700">
      <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-4">Live Biometrics</h3>
      <ProgressBar label="Eye Aspect Ratio (EAR)" value={ear || 0} max={0.4} threshold={{ danger: 0.22, warning: 0.28 }} />
      <ProgressBar label="Mouth Aspect Ratio (MAR)" value={mar || 0} max={0.8} />
      <ProgressBar label="Head Pitch" value={Math.abs(pitch || 0)} max={40} />
    </div>
  );
};

export default LiveMetricsBar;
