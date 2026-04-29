import { format } from 'date-fns';

const AlertCard = ({ event }) => {
  if (!event) return null;

  const { state, score, timestamp, ear } = event;
  const timeStr = timestamp ? format(new Date(timestamp), 'HH:mm:ss') : '--:--:--';

  const styles = {
    ALERT: "border-green-500/30 bg-green-500/10 text-green-400",
    MILD: "border-yellow-500/30 bg-yellow-500/10 text-yellow-400",
    DROWSY: "border-orange-500/30 bg-orange-500/10 text-orange-400",
    CRITICAL: "border-red-500/30 bg-red-500/10 text-red-400",
  };

  const currentStyle = styles[state] || styles.ALERT;

  return (
    <div className={`flex items-center justify-between p-3 rounded border ${currentStyle} backdrop-blur-sm transition-all duration-300`}>
      <div className="flex items-center gap-3">
        <span className="text-xs font-mono opacity-70">{timeStr}</span>
        <span className="font-bold tracking-wide">{state}</span>
      </div>
      <div className="flex items-center gap-4 text-sm">
        <div className="flex flex-col items-end">
          <span className="opacity-70 text-xs">Score</span>
          <span className="font-mono">{(score || 0).toFixed(2)}</span>
        </div>
        <div className="flex flex-col items-end">
          <span className="opacity-70 text-xs">EAR</span>
          <span className="font-mono">{(ear || 0).toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
};

export default AlertCard;
