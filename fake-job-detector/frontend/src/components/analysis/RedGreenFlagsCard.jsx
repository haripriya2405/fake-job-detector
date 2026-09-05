import React from 'react';
import { AlertCircle, CheckCircle2, ShieldX, ShieldCheck } from 'lucide-react';

export const RedGreenFlagsCard = ({ redFlags = [], greenFlags = [] }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Red Flags Card */}
      <div className="p-5 rounded-2xl border border-red-500/30 bg-red-950/20 shadow-xl space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-red-500/20">
          <div className="flex items-center gap-2">
            <ShieldX className="w-4 h-4 text-red-400" />
            <h3 className="text-sm font-bold text-red-300 uppercase tracking-wider">Red Flags ({redFlags.length})</h3>
          </div>
          <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-red-500/20 text-red-400">
            Threat Indicators
          </span>
        </div>

        {redFlags.length > 0 ? (
          <ul className="space-y-2">
            {redFlags.map((flag, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-red-200/90 leading-relaxed">
                <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                <span>{flag}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-xs text-slate-400 italic">No critical red flags or malicious signatures detected.</p>
        )}
      </div>

      {/* Green Flags Card */}
      <div className="p-5 rounded-2xl border border-emerald-500/30 bg-emerald-950/20 shadow-xl space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-emerald-500/20">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-emerald-300 uppercase tracking-wider">Green Flags ({greenFlags.length})</h3>
          </div>
          <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">
            Trust Signals
          </span>
        </div>

        {greenFlags.length > 0 ? (
          <ul className="space-y-2">
            {greenFlags.map((flag, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-emerald-200/90 leading-relaxed">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span>{flag}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-xs text-slate-400 italic">Limited positive trust markers established for unverified source.</p>
        )}
      </div>
    </div>
  );
};
