import React from 'react';
import { DollarSign, TrendingUp, AlertTriangle, CheckCircle2, HelpCircle } from 'lucide-react';

export const SalaryBenchmarkCard = ({ benchmark }) => {
  if (!benchmark) return null;

  const isTrap = benchmark.is_unrealistic_high;
  const hasSalary = benchmark.verdict !== 'NO_SALARY_DETECTED';

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`p-1.5 rounded-lg border ${
            isTrap ? 'bg-red-500/10 text-red-400 border-red-500/20' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
          }`}>
            <DollarSign className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Market Salary Benchmark Analysis</h3>
            <p className="text-[11px] text-slate-400">Cross-referenced with BLS & EMSCAD industry distributions</p>
          </div>
        </div>

        {hasSalary && (
          <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${
            isTrap
              ? 'bg-red-500/15 text-red-400 border-red-500/30'
              : 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
          }`}>
            {isTrap ? 'UNREALISTIC HIGH TRAP' : 'REALISTIC MARKET RATE'}
          </span>
        )}
      </div>

      {hasSalary ? (
        <div className="space-y-3">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            <div className="p-3 rounded-xl bg-black/40 border border-white/10">
              <span className="block text-[10px] uppercase font-mono tracking-wider text-slate-400">Stated Pay</span>
              <span className="text-sm font-bold text-white truncate block">{benchmark.detected_salary_text}</span>
              <span className="text-[10px] text-slate-500">{benchmark.frequency}</span>
            </div>

            <div className="p-3 rounded-xl bg-black/40 border border-white/10">
              <span className="block text-[10px] uppercase font-mono tracking-wider text-slate-400">Job Family</span>
              <span className="text-sm font-bold text-white capitalize truncate block">
                {benchmark.matched_job_family.replace(/_/g, ' ')}
              </span>
              <span className="text-[10px] text-slate-500">Classification</span>
            </div>

            <div className="p-3 rounded-xl bg-black/40 border border-white/10">
              <span className="block text-[10px] uppercase font-mono tracking-wider text-slate-400">Market Median</span>
              <span className="text-sm font-bold text-emerald-400 block">
                ${benchmark.market_median_annual.toLocaleString()}/yr
              </span>
              <span className="text-[10px] text-slate-500">BLS Standard</span>
            </div>

            <div className="p-3 rounded-xl bg-black/40 border border-white/10">
              <span className="block text-[10px] uppercase font-mono tracking-wider text-slate-400">Variance Ratio</span>
              <span className={`text-sm font-bold block ${isTrap ? 'text-red-400' : 'text-slate-300'}`}>
                {benchmark.discrepancy_ratio}x
              </span>
              <span className="text-[10px] text-slate-500">vs Normal Median</span>
            </div>
          </div>

          <div className={`p-3.5 rounded-xl border text-xs leading-relaxed ${
            isTrap ? 'bg-red-950/30 border-red-500/30 text-red-200' : 'bg-emerald-950/20 border-emerald-500/20 text-emerald-200'
          }`}>
            <div className="flex items-start gap-2">
              {isTrap ? <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" /> : <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />}
              <span>{benchmark.explanation}</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-4 rounded-xl bg-black/30 border border-white/10 text-xs text-slate-400 flex items-center gap-2">
          <HelpCircle className="w-4 h-4 text-slate-500 flex-shrink-0" />
          <span>No specific compensation numbers stated in job posting text.</span>
        </div>
      )}
    </div>
  );
};
