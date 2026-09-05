/**
 * Utility functions for Risk Scoring & Classification
 */

export const RISK_LEVELS = {
  LOW: {
    key: 'low',
    label: 'Safe',
    verdict: 'SAFE',
    color: '#10B981',
    bgColor: 'rgba(16, 185, 129, 0.12)',
    borderColor: 'rgba(16, 185, 129, 0.3)',
    textColor: 'text-emerald-400',
    badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    description: 'Legitimate patterns detected. Standard hiring procedures observed.',
  },
  MEDIUM: {
    key: 'medium',
    label: 'Caution',
    verdict: 'CAUTION',
    color: '#FBBF24',
    bgColor: 'rgba(251, 191, 36, 0.12)',
    borderColor: 'rgba(251, 191, 36, 0.3)',
    textColor: 'text-amber-400',
    badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    description: 'Minor inconsistencies detected. Proceed with measured caution.',
  },
  HIGH: {
    key: 'high',
    label: 'Risky',
    verdict: 'RISKY',
    color: '#F43F5E',
    bgColor: 'rgba(244, 63, 94, 0.12)',
    borderColor: 'rgba(244, 63, 94, 0.3)',
    textColor: 'text-red-400',
    badgeClass: 'bg-red-500/10 text-red-400 border-red-500/30',
    description: 'Strong scam indicators detected. Avoid sharing sensitive data or payments.',
  },
  CRITICAL: {
    key: 'critical',
    label: 'Max Risk',
    verdict: 'MAX RISK',
    color: '#EF4444',
    bgColor: 'rgba(239, 68, 68, 0.15)',
    borderColor: 'rgba(239, 68, 68, 0.4)',
    textColor: 'text-red-400',
    badgeClass: 'bg-red-500/15 text-red-400 border-red-500/40 animate-pulse',
    description: 'High scam probability with predatory indicators. Immediate disengagement advised.',
  },
};

export function getRiskLevelMeta(score) {
  const numericScore = Number(score) || 0;
  if (numericScore < 30) return RISK_LEVELS.LOW;
  if (numericScore < 60) return RISK_LEVELS.MEDIUM;
  if (numericScore < 80) return RISK_LEVELS.HIGH;
  return RISK_LEVELS.CRITICAL;
}

export function getSeverityBadge(severity) {
  const s = (severity || '').toLowerCase();
  switch (s) {
    case 'critical':
      return {
        label: 'Critical Flag',
        class: 'bg-red-500/15 text-red-400 border border-red-500/30',
      };
    case 'high':
      return {
        label: 'High Severity',
        class: 'bg-orange-500/15 text-orange-400 border border-orange-500/30',
      };
    case 'medium':
      return {
        label: 'Medium Severity',
        class: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
      };
    case 'low':
    default:
      return {
        label: 'Low Warning',
        class: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
      };
  }
}
