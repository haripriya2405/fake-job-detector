import React, { useState, useEffect } from 'react';
import { Cookie, X } from 'lucide-react';
import { Link } from 'react-router-dom';

export const CookieBanner = () => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem('sentinel_cookie_consent');
    if (!consent) {
      // Delay slightly for smooth entrance animation
      const timer = setTimeout(() => setVisible(true), 600);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleAccept = (type) => {
    localStorage.setItem('sentinel_cookie_consent', type);
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-md w-[calc(100%-2rem)] sm:w-[420px] transition-all duration-300 animate-in slide-in-from-bottom-5 fade-in">
      <div className="relative rounded-2xl border border-slate-800/90 bg-[#0c121d]/95 backdrop-blur-md p-5 shadow-2xl shadow-black/80 space-y-4">
        <button
          onClick={() => handleAccept('dismissed')}
          className="absolute top-3 right-3 text-slate-400 hover:text-slate-200 transition-colors p-1"
          aria-label="Close cookie notice"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-start gap-3.5 pr-4">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shrink-0 mt-0.5">
            <Cookie className="w-5 h-5" />
          </div>
          <div className="space-y-1 text-xs text-slate-300 leading-relaxed font-light">
            <p>
              We use essential cookies to run JobScamScore. With your permission, we also use privacy-friendly first-party analytics — no ads, no cross-site tracking — to see which features help people most.{' '}
              <Link to="/privacy" className="text-emerald-400 underline underline-offset-2 hover:text-emerald-300">
                Cookie Policy
              </Link>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 pt-1">
          <button
            type="button"
            onClick={() => handleAccept('essential')}
            className="flex-1 py-2.5 px-4 rounded-xl border border-slate-700/80 bg-slate-900/80 hover:bg-slate-800 text-xs font-semibold text-slate-200 transition-all text-center"
          >
            Essential only
          </button>
          <button
            type="button"
            onClick={() => handleAccept('all')}
            className="flex-1 py-2.5 px-4 rounded-xl bg-emerald-500 hover:bg-emerald-400 active:bg-emerald-600 text-xs font-semibold text-slate-950 transition-all text-center shadow-lg shadow-emerald-500/20"
          >
            Accept analytics
          </button>
        </div>
      </div>
    </div>
  );
};

export default CookieBanner;
