import React, { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowRight, ShieldCheck, Sparkles, User, History, LayoutDashboard } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { HeroScannerCard } from '../components/scanner/HeroScannerCard';
import { HowItWorks } from '../components/home/HowItWorks';
import { SignalArchitectureGrid } from '../components/home/SignalArchitectureGrid';
import { SampleResultsShowcase } from '../components/home/SampleResultsShowcase';
import { CommonScamRedFlags } from '../components/home/CommonScamRedFlags';
import { BottomCtaBanner } from '../components/home/BottomCtaBanner';

export const LandingPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSelectSample = (sample) => {
    navigate(`/analysis/${sample.id}`, { state: { samplePreset: sample } });
  };

  return (
    <div className="space-y-0 text-frost selection:bg-emerald-500 selection:text-white">
      
      {/* 1. Hero Section matching Screenshot 1 */}
      <section className="relative overflow-hidden pt-10 sm:pt-16 lg:pt-20 pb-20 sm:pb-28">
        
        {/* Subtle background blueprint and ambient spotlight glow */}
        <div className="pointer-events-none absolute inset-0" aria-hidden="true">
          <div className="absolute inset-0 bg-blueprint opacity-50" />
          <div className="absolute inset-0 bg-spotlight" />
          <div className="absolute right-0 top-1/2 h-[650px] w-[650px] -translate-y-1/2 translate-x-1/3 rounded-full bg-emerald-500/[0.04] blur-[130px]" />
        </div>

        <div className="relative mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="grid items-center gap-10 lg:grid-cols-12 lg:gap-14">
            
            {/* Left Column (5 cols / ~45%) */}
            <div className="lg:col-span-5 text-center lg:text-left space-y-6 min-w-0">
              
              {isAuthenticated ? (
                /* Authenticated State Banner with Smooth Pulse Animation */
                <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-mono shadow-lg shadow-emerald-500/5 animate-fadeIn">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                  <span className="font-semibold">Welcome back, {user?.full_name?.split(' ')[0] || user?.email?.split('@')[0] || 'Analyst'}</span>
                  <span className="text-fog">|</span>
                  <span className="text-[11px] text-emerald-400/90 uppercase tracking-wider font-semibold">Pro Suite Active</span>
                </div>
              ) : (
                <p className="text-[10px] sm:text-[11px] font-mono font-medium uppercase tracking-[0.2em] text-fog">
                  Free AI job scam checker
                </p>
              )}

              <h1 className="text-4xl sm:text-5xl lg:text-[3.75rem] font-medium tracking-[-0.02em] leading-[1.05] text-frost">
                Check if a job is a <br className="hidden sm:inline" />
                scam <br />
                <span className="text-emerald-400">before you reply.</span>
              </h1>

              <p className="text-base sm:text-lg text-mist max-w-md mx-auto lg:mx-0 leading-relaxed font-light">
                {isAuthenticated ? (
                  <>
                    Your account is equipped with <span className="text-frost font-normal">unlimited forensic scans</span>, 13-stage pipeline telemetry, and instant cloud history sync.
                  </>
                ) : (
                  <>
                    Paste any job link or message. Get a <span className="text-frost font-normal">0–100 risk score</span> with every red flag explained — first scan <span className="text-frost font-normal">free with no account required</span>.
                  </>
                )}
              </p>

              {/* Authenticated Fast Navigation Pill */}
              {isAuthenticated && (
                <div className="flex flex-wrap items-center justify-center lg:justify-start gap-3 pt-1 animate-fadeIn">
                  <Link
                    to="/dashboard"
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-mono text-frost transition-all duration-200 hover:border-emerald-500/40 group"
                  >
                    <LayoutDashboard className="w-3.5 h-3.5 text-emerald-400 group-hover:scale-110 transition-transform" />
                    <span>My Dashboard</span>
                    <ArrowRight className="w-3 h-3 text-fog group-hover:translate-x-0.5 transition-transform" />
                  </Link>

                  <Link
                    to="/history"
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-mono text-fog hover:text-frost transition-all duration-200 hover:border-white/20 group"
                  >
                    <History className="w-3.5 h-3.5 text-fog group-hover:text-emerald-400 transition-colors" />
                    <span>Scan History</span>
                  </Link>
                </div>
              )}

              {/* 3-Stat Metric Bar matching Screenshot 1 */}
              <div className="pt-6 sm:pt-8 border-t border-white/10 max-w-xl mx-auto lg:mx-0">
                <div className="grid grid-cols-3 gap-0 divide-x divide-white/10">
                  
                  {/* Stat 1 */}
                  <div className="flex flex-col items-center lg:items-start text-center lg:text-left px-2 sm:px-3 min-w-0">
                    <p className="flex items-center gap-1.5 text-2xl sm:text-3xl font-medium font-mono tabular-nums tracking-tight text-frost">
                      <span className="h-2 w-2 rounded-full bg-emerald-400 shrink-0" />
                      <span>60%</span>
                    </p>
                    <p className="mt-1.5 text-[9px] sm:text-[10px] font-mono font-medium uppercase tracking-[0.16em] text-fog leading-snug">
                      Of scans flagged risky
                    </p>
                  </div>

                  {/* Stat 2 */}
                  <div className="flex flex-col items-center lg:items-start text-center lg:text-left px-2 sm:px-3 min-w-0">
                    <p className="text-2xl sm:text-3xl font-medium font-mono tabular-nums tracking-tight text-frost">
                      50+
                    </p>
                    <p className="mt-1.5 text-[9px] sm:text-[10px] font-mono font-medium uppercase tracking-[0.16em] text-fog leading-snug">
                      Checks per scan
                    </p>
                  </div>

                  {/* Stat 3 */}
                  <div className="flex flex-col items-center lg:items-start text-center lg:text-left px-2 sm:px-3 min-w-0">
                    <p className="text-2xl sm:text-3xl font-medium font-mono tabular-nums tracking-tight text-frost">
                      ~60
                    </p>
                    <p className="mt-1.5 text-[9px] sm:text-[10px] font-mono font-medium uppercase tracking-[0.16em] text-fog leading-snug">
                      Sec to verdict (avg)
                    </p>
                  </div>
                </div>
              </div>

            </div>

            {/* Right Column: Hero Scanner Widget (7 cols / ~55%) */}
            <div className="lg:col-span-7 w-full min-w-0">
              <HeroScannerCard onSampleClick={handleSelectSample} />
            </div>

          </div>
        </div>
      </section>

      {/* 2. How It Works Section */}
      <HowItWorks />

      {/* 3. Sample Results Showcase matching Screenshot 2 */}
      <SampleResultsShowcase onSelectSample={handleSelectSample} />

      {/* 4. 8-Layer Signal Architecture matching Screenshot 3 */}
      <SignalArchitectureGrid />

      {/* 5. Common Job Scam Red Flags & Fraud Types matching Screenshot 4 */}
      <CommonScamRedFlags />

      {/* 6. Bottom CTA Banner matching Screenshot 5 */}
      <BottomCtaBanner />

    </div>
  );
};

export default LandingPage;
