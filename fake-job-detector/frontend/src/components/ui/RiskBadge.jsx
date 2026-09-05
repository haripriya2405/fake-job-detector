import React from 'react';
import { getRiskLevelMeta } from '../../utils/riskHelpers';
import { ShieldAlert, ShieldCheck, AlertTriangle, Flame } from 'lucide-react';

export const RiskBadge = ({ score, level: explicitLevel, size = 'md', showScore = true, className = '' }) => {
  const meta = getRiskLevelMeta(score !== undefined ? score : (explicitLevel === 'critical' ? 90 : explicitLevel === 'high' ? 70 : explicitLevel === 'medium' ? 45 : 10));

  const getIcon = () => {
    switch (meta.key) {
      case 'critical':
        return <Flame className="w-3.5 h-3.5 shrink-0" />;
      case 'high':
        return <ShieldAlert className="w-3.5 h-3.5 shrink-0" />;
      case 'medium':
        return <AlertTriangle className="w-3.5 h-3.5 shrink-0" />;
      case 'low':
      default:
        return <ShieldCheck className="w-3.5 h-3.5 shrink-0" />;
    }
  };

  const sizes = {
    sm: 'text-xs px-2 py-0.5 gap-1 font-medium',
    md: 'text-xs px-3 py-1 gap-1.5 font-semibold',
    lg: 'text-sm px-4 py-1.5 gap-2 font-bold',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border ${meta.badgeClass} ${sizes[size] || sizes.md} ${className}`}
      style={{
        boxShadow: `0 0 12px ${meta.bgColor}`,
      }}
    >
      {getIcon()}
      <span>{meta.label}</span>
      {showScore && score !== undefined && (
        <span className="opacity-80 font-mono font-normal">({score}/100)</span>
      )}
    </span>
  );
};

export const Badge = ({ children, variant = 'default', className = '', icon: Icon }) => {
  const variants = {
    default: 'bg-slate-800 text-slate-300 border-slate-700',
    primary: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    ai: 'bg-purple-500/15 text-purple-400 border-purple-500/30',
    success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    warning: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    danger: 'bg-red-500/15 text-red-400 border-red-500/30',
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${variants[variant] || variants.default} ${className}`}>
      {Icon && <Icon className="w-3 h-3 shrink-0" />}
      {children}
    </span>
  );
};

export default RiskBadge;
