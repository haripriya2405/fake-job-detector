import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowRight, Lock } from 'lucide-react';

export const BottomCtaBanner = () => {
  const navigate = useNavigate();

  const handleScrollToScanner = () => {
    const el = document.getElementById('landing-scan-input');
    if (el) {
      el.focus();
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
      navigate('/analyze');
    }
  };

  return (
    <section className="bg-[#050a08] py-16 sm:py-20 border-t border-white/5">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        
        {/* Large Rounded Glass Banner Card */}
        <div className="glass-card rounded-2xl sm:rounded-3xl p-6 sm:p-10 border border-white/10 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-6">
          
          {/* Left Text */}
          <div className="space-y-3 text-center md:text-left flex-1">
            <h2 className="text-2xl sm:text-3xl font-semibold text-frost tracking-tight">
              One paste. Full verdict. 60 seconds.
            </h2>
            <p className="text-xs sm:text-sm text-mist font-light max-w-md leading-relaxed">
              The FTC reports a median loss of <strong className="text-frost font-normal">$2,000 per job scam</strong>. Scan before you apply with the free public checker.
            </p>
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-x-2.5 gap-y-1 text-[11px] text-fog font-light pt-1">
              <span className="flex items-center gap-1 text-emerald-400">
                <Lock className="w-3 h-3" />
                <span>Anonymous scan</span>
              </span>
              <span className="text-white/20">·</span>
              <span>First scan without an account</span>
              <span className="text-white/20">·</span>
              <span>100 scans/month with a free account</span>
            </div>
          </div>

          {/* Right Action */}
          <div className="flex flex-col items-center gap-2.5 shrink-0">
            <button
              onClick={handleScrollToScanner}
              className="inline-flex items-center gap-2 rounded-full px-6 py-3.5 text-xs sm:text-sm font-semibold text-white bg-emerald-500 hover:bg-emerald-400 active:bg-emerald-600 shadow-emerald-button hover:shadow-emerald-glow transition-all"
            >
              <span>Start Free Scan</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <Link
              to="/analyze"
              className="text-xs text-fog hover:text-frost transition-colors inline-flex items-center gap-1 font-light"
            >
              <span>Open full scanner</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

        </div>

      </div>
    </section>
  );
};

export default BottomCtaBanner;
