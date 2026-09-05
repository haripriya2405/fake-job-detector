import React from 'react';
import { Card } from '../ui/Card';
import { TrendingUp, TrendingDown } from 'lucide-react';

export const MetricCard = ({
  title,
  value,
  subtitle,
  change,
  changeType = 'increase', // 'increase' | 'decrease'
  icon: Icon,
  iconColor = 'text-blue-400',
  iconBg = 'bg-blue-500/10 border-blue-500/20',
}) => {
  return (
    <Card className="p-5 relative overflow-hidden group">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</p>
          <div className="text-2xl font-bold font-mono text-white tracking-tight">{value}</div>
        </div>

        <div className={`w-11 h-11 rounded-xl ${iconBg} border flex items-center justify-center ${iconColor} shadow-sm group-hover:scale-105 transition-transform`}>
          {Icon && <Icon className="w-5 h-5" />}
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
        {change && (
          <span className={`inline-flex items-center gap-1 font-semibold ${
            changeType === 'increase' ? 'text-emerald-400' : 'text-amber-400'
          }`}>
            {changeType === 'increase' ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
            {change}
          </span>
        )}
        <span className="text-slate-400">{subtitle}</span>
      </div>
    </Card>
  );
};

export default MetricCard;
