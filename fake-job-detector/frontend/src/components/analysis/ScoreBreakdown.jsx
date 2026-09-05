import React from 'react';
import { BrainCircuit, Scale, GlobeLock } from 'lucide-react';

export const ScoreBreakdown = ({ breakdown }) => {
  if (!breakdown) return null;

  const {
    ml_contribution = 0,
    rule_contribution = 0,
    domain_penalty = 0,
    total_score = 0,
  } = breakdown;

  const items = [
    {
      title: 'ML Linguistic Probability',
      max: 45,
      value: ml_contribution,
      percentage: Math.round((ml_contribution / 45) * 100),
      color: 'bg-emerald-400',
      textColor: 'text-emerald-400',
      icon: BrainCircuit,
      description: 'NLP TF-IDF & statistical classification trained on real-world employment fraud datasets.',
    },
    {
      title: 'Deterministic Rule Penalties',
      max: 40,
      value: rule_contribution,
      percentage: Math.round((rule_contribution / 40) * 100),
      color: 'bg-red-500',
      textColor: 'text-red-400',
      icon: Scale,
      description: 'Hard rule triggers: advance fee checks, anonymous Telegram funnels, and task lures.',
    },
    {
      title: 'Domain & Entity Reputation',
      max: 15,
      value: domain_penalty,
      percentage: Math.round((domain_penalty / 15) * 100),
      color: 'bg-skywash',
      textColor: 'text-skywash',
      icon: GlobeLock,
      description: 'RDAP registration age, MX mail servers, SSL certificates, and verified careers portal listing.',
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between pb-1 border-b border-white/10">
        <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-fog">
          Explainable Score Attribution
        </h4>
        <span className="text-xs font-mono font-bold text-frost">Total: {total_score}/100</span>
      </div>

      <div className="space-y-3">
        {items.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div key={idx} className="p-3 rounded-xl bg-black/30 border border-white/10 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 font-medium text-frost">
                  <Icon className={`w-3.5 h-3.5 ${item.textColor}`} />
                  <span>{item.title}</span>
                </div>
                <div className="flex items-center gap-1 font-mono">
                  <span className={`font-bold ${item.textColor}`}>+{item.value}</span>
                  <span className="text-fog text-[10px]">/ {item.max} pts</span>
                </div>
              </div>

              {/* Progress track */}
              <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${item.color}`}
                  style={{ width: `${Math.min(item.percentage, 100)}%` }}
                />
              </div>

              <p className="text-[11px] text-fog leading-relaxed font-light">{item.description}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ScoreBreakdown;
