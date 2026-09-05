import React, { useState } from 'react';
import { ChevronDown, ChevronUp, AlertCircle, ShieldAlert, CheckCircle } from 'lucide-react';
import { getSeverityBadge } from '../../utils/riskHelpers';

export const IndicatorCard = ({ indicator, index }) => {
  const [expanded, setExpanded] = useState(true);
  const badge = getSeverityBadge(indicator.severity);

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/80 overflow-hidden transition-all duration-200 hover:border-slate-700">
      <div
        onClick={() => setExpanded(!expanded)}
        className="p-4 flex items-start justify-between cursor-pointer select-none gap-4"
      >
        <div className="flex items-start gap-3">
          <div className="mt-0.5 w-6 h-6 rounded-lg bg-slate-800 flex items-center justify-center font-mono text-xs font-bold text-slate-400">
            {index + 1}
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="text-sm font-semibold text-white">{indicator.title}</h4>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${badge.class}`}>
                {badge.label}
              </span>
              {indicator.category && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700">
                  {indicator.category}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">{indicator.description}</p>
          </div>
        </div>

        <button className="text-slate-400 hover:text-white p-1">
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {expanded && indicator.recommendation && (
        <div className="px-4 pb-4 pt-0 border-t border-slate-800/60 mt-1">
          <div className="p-3 rounded-lg bg-blue-950/20 border border-blue-500/20 mt-3 flex items-start gap-2.5">
            <CheckCircle className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
            <div className="text-xs text-slate-300">
              <strong className="text-blue-400 font-semibold">Mitigation Strategy: </strong>
              {indicator.recommendation}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IndicatorCard;
