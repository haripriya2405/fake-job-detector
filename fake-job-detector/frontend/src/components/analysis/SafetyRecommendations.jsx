import React from 'react';
import { ShieldCheck, ShieldAlert, AlertOctagon, ArrowRight } from 'lucide-react';

export const SafetyRecommendations = ({ recommendations = [] }) => {
  if (!recommendations || recommendations.length === 0) return null;

  const getPriorityMeta = (priority) => {
    switch (priority) {
      case 'urgent':
        return {
          icon: AlertOctagon,
          badge: 'CRITICAL ACTION',
          containerClass: 'bg-red-950/20 border-red-500/30 text-red-300',
          badgeClass: 'bg-red-500/20 text-red-400 border-red-500/40',
        };
      case 'advisory':
        return {
          icon: ShieldAlert,
          badge: 'ADVISORY',
          containerClass: 'bg-amber-950/20 border-amber-500/30 text-amber-300',
          badgeClass: 'bg-amber-500/20 text-amber-400 border-amber-500/40',
        };
      case 'safe':
      default:
        return {
          icon: ShieldCheck,
          badge: 'BEST PRACTICE',
          containerClass: 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300',
          badgeClass: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
        };
    }
  };

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-white flex items-center gap-2">
        <ShieldCheck className="w-4 h-4 text-emerald-400" />
        <span>Safety & Mitigation Recommendations</span>
      </h4>

      <div className="space-y-2.5">
        {recommendations.map((rec, idx) => {
          const meta = getPriorityMeta(rec.priority);
          const Icon = meta.icon;
          return (
            <div
              key={idx}
              className={`p-4 rounded-xl border ${meta.containerClass} transition-all space-y-1.5`}
            >
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 font-semibold text-xs text-white">
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{rec.action}</span>
                </div>
                <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider border ${meta.badgeClass}`}>
                  {meta.badge}
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed pl-6">{rec.detail}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SafetyRecommendations;
