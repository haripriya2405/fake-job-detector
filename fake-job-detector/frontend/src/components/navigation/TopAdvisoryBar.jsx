import React from 'react';
import { ShieldAlert } from 'lucide-react';

export const TopAdvisoryBar = () => {
  return (
    <div className="border-b border-white/5 bg-white/[0.02] text-fog text-[11px] sm:text-xs py-2 px-4">
      <div className="max-w-7xl mx-auto flex items-center justify-center gap-2 text-center flex-wrap">
        <ShieldAlert className="w-3.5 h-3.5 text-emerald-400 shrink-0 inline" />
        <span>Detection intelligence informed by public fraud-report patterns from</span>
        <div className="inline-flex items-center gap-1.5 font-medium text-mist">
          <span className="hover:text-frost transition-colors underline underline-offset-2">FTC</span>
          <span className="text-white/20">·</span>
          <span className="hover:text-frost transition-colors underline underline-offset-2">BBB</span>
          <span className="text-white/20">·</span>
          <span className="hover:text-frost transition-colors underline underline-offset-2">FBI IC3</span>
        </div>
      </div>
    </div>
  );
};

export default TopAdvisoryBar;
