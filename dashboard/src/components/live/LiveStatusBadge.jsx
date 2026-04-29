const LiveStatusBadge = ({ state }) => {
  const isCritical = state === 'CRITICAL' || state === 'DROWSY';
  
  const styles = {
    ALERT: "bg-green-500 text-white shadow-green-500/50",
    MILD: "bg-yellow-500 text-white shadow-yellow-500/50",
    DROWSY: "bg-orange-500 text-white shadow-orange-500/50",
    CRITICAL: "bg-red-500 text-white shadow-red-500/50",
  };

  const currentStyle = styles[state] || styles.ALERT;
  
  return (
    <div className={`
      flex items-center justify-center px-8 py-4 rounded-full font-black text-3xl tracking-widest shadow-lg
      transition-all duration-300 transform
      ${currentStyle}
      ${isCritical ? 'animate-pulse scale-105 ring-4 ring-offset-4 ring-offset-slate-900 ring-red-500/50' : 'scale-100'}
    `}>
      {state || 'WAITING'}
    </div>
  );
};

export default LiveStatusBadge;
