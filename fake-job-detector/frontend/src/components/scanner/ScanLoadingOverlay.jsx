import React, { useState, useEffect } from 'react';
import { CheckCircle2, Building, AlertTriangle, Cpu, Loader2 } from 'lucide-react';

const STAGES = [
  {
    id: 1,
    title: 'Parsing job details',
    desc: 'Extracting key information',
    icon: CheckCircle2,
  },
  {
    id: 2,
    title: 'Company verification',
    desc: 'Checking careers page & domains',
    icon: Building,
  },
  {
    id: 3,
    title: 'Scam pattern detection',
    desc: 'Cross-referencing known threats',
    icon: AlertTriangle,
  },
  {
    id: 4,
    title: 'AI analysis',
    desc: 'LLM correlation & scoring',
    icon: Cpu,
  },
];

export const ScanLoadingOverlay = ({ isScanning, currentStage = 0 }) => {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    if (!isScanning) {
      setActiveStep(0);
      return;
    }

    const interval = setInterval(() => {
      setActiveStep((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 700);

    return () => clearInterval(interval);
  }, [isScanning]);

  if (!isScanning) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/85 backdrop-blur-lg animate-in fade-in duration-300">
      <div className="relative w-full max-w-3xl bg-[#081017] border border-slate-800 rounded-3xl p-8 sm:p-10 shadow-2xl space-y-8 text-center overflow-hidden">
        
        {/* Glowing spotlight effect */}
        <div className="pointer-events-none absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl" />

        {/* Top Spinning Arc */}
        <div className="flex justify-center pt-2">
          <div className="relative w-16 h-16 sm:w-20 sm:h-20 flex items-center justify-center">
            <div className="absolute inset-0 rounded-full border-4 border-emerald-500/20 border-t-emerald-400 animate-spin" />
            <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400">
              <Loader2 className="w-6 h-6 animate-spin" />
            </div>
          </div>
        </div>

        {/* Title & Subtitle matching video frame 20 */}
        <div className="space-y-2 max-w-xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Analyzing this job...
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 font-light leading-relaxed">
            Usually about a minute — thorough scans can take a few. We're researching the company, checking scam databases, and analyzing patterns.
          </p>
        </div>

        {/* 4 Stage Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-left">
          {STAGES.map((st, idx) => {
            const isCompleted = idx < activeStep;
            const isCurrent = idx === activeStep;
            const Icon = st.icon;

            return (
              <div
                key={st.id}
                className={`p-4 rounded-2xl border transition-all duration-300 ${
                  isCompleted
                    ? 'border-emerald-500/60 bg-emerald-950/20 text-emerald-300 shadow-md'
                    : isCurrent
                    ? 'border-emerald-400 bg-emerald-950/40 text-white ring-1 ring-emerald-400/50 shadow-lg shadow-emerald-500/20 scale-[1.02]'
                    : 'border-slate-800/80 bg-slate-900/40 text-slate-500'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div
                    className={`p-2 rounded-xl ${
                      isCompleted
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : isCurrent
                        ? 'bg-emerald-400 text-slate-950 animate-pulse'
                        : 'bg-slate-800 text-slate-600'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  {isCompleted && (
                    <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-emerald-glow" />
                  )}
                  {isCurrent && (
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                  )}
                </div>

                <h3 className="text-xs font-semibold font-sans leading-snug">
                  {st.title}
                </h3>
                <p className="text-[10px] text-slate-400 font-light mt-0.5 leading-relaxed">
                  {st.desc}
                </p>
              </div>
            );
          })}
        </div>

        {/* Progress Bar matching video */}
        <div className="space-y-2 pt-2">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>Analysis in progress</span>
            <span className="text-emerald-400 animate-pulse">Please wait...</span>
          </div>
          <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 via-teal-400 to-emerald-400 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${Math.min(98, ((activeStep + 1) / STAGES.length) * 100)}%` }}
            />
          </div>
        </div>

      </div>
    </div>
  );
};

export default ScanLoadingOverlay;
