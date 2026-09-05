import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { CheckCircle2, AlertTriangle, ShieldCheck, ShieldAlert, ArrowRight } from 'lucide-react';

export const SAMPLE_DATA = [
  {
    id: 'sample-safe',
    role: 'Remote Customer Service Representative',
    company: 'Teleperformance USA',
    verdict: 'Safe',
    score: 95,
    borderClass: 'border-emerald-500/25',
    badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25',
    scoreClass: 'text-emerald-400',
    footerBg: 'bg-emerald-500/10 border-emerald-500/20',
    footerText: 'text-emerald-200/90',
    footerAdvice: 'This appears to be a legitimate opportunity. Apply through official channels.',
    linkText: 'See a full sample report (50+ checks) →',
    points: [
      { text: 'Listed on official Teleperformance careers site', safe: true },
      { text: 'Recruiter verified on LinkedIn at Teleperformance', safe: true },
      { text: 'Domain established 25+ years · SSL valid', safe: true },
      { text: 'Minor: posting syndicated across multiple job boards', safe: false, minor: true },
    ],
  },
  {
    id: 'sample-caution',
    role: 'Remote Data Entry Clerk',
    company: 'Horizon Labs',
    verdict: 'Caution',
    score: 52,
    borderClass: 'border-amber-500/30',
    badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    scoreClass: 'text-amber-400',
    footerBg: 'bg-amber-500/10 border-amber-500/30',
    footerText: 'text-amber-200/90',
    footerAdvice: 'Proceed with caution. Verify directly with the company before sharing personal info.',
    points: [
      { text: "Job NOT found on company's official careers page", safe: false },
      { text: 'Recruiter email unverified — could not confirm LinkedIn', safe: false },
      { text: 'Company website and LinkedIn page found', safe: true },
      { text: 'Salary range is realistic for role level', safe: true },
    ],
  },
  {
    id: 'sample-risky',
    role: 'Data Scientist',
    company: 'StemPar Sciences',
    verdict: 'Risky',
    archetype: '🚫 Task Scam',
    score: 0,
    borderClass: 'border-red-500/40',
    badgeClass: 'bg-red-500/10 text-red-400 border-red-500/30',
    scoreClass: 'text-red-400',
    footerBg: 'bg-red-500/10 border-red-500/40',
    footerText: 'text-red-200/90',
    footerAdvice: 'Task scam confirmed. Do not apply, send money, or share personal information.',
    points: [
      { text: 'Task scam: "simple" app data tasks to boost store rankings', safe: false },
      { text: 'Stempar.com rated 1% trust on Scamdoc — confirmed scam source', safe: false },
      { text: 'No careers page, LinkedIn, or verified web presence found', safe: false },
      { text: 'Industry mismatch: biotech firm posting app ranking job', safe: false },
    ],
  },
];

export const SampleResultsShowcase = ({ onSelectSample }) => {
  const navigate = useNavigate();

  const handleCardClick = (sample) => {
    if (onSelectSample) {
      onSelectSample(sample);
    } else {
      navigate(`/analysis/${sample.id}`);
    }
  };

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
    <section id="sample-results" className="bg-[#050a08] py-20 sm:py-24 border-t border-white/5" aria-labelledby="sample-heading">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center mb-12 sm:mb-16">
          <div className="flex items-center justify-center gap-4">
            <span className="eyebrow-line" aria-hidden="true" />
            <p className="text-[11px] font-mono font-medium uppercase tracking-[0.2em] text-fog">
              Sample results
            </p>
            <span className="eyebrow-line eyebrow-line-r" aria-hidden="true" />
          </div>
          <h2 id="sample-heading" className="mt-3 font-semibold text-frost tracking-tight text-3xl sm:text-4xl">
            This is what your scan looks like
          </h2>
          <p className="mt-3 text-mist max-w-2xl mx-auto font-light text-sm sm:text-base">
            Every scan gives you a clear verdict — Safe, Caution, or Risky — backed by specific evidence you can verify.
          </p>
        </div>

        {/* 3 Sample Cards matching Screenshot 2 */}
        <div className="grid gap-6 md:grid-cols-3 items-stretch">
          {SAMPLE_DATA.map((sample) => (
            <div
              key={sample.id}
              onClick={() => handleCardClick(sample)}
              className={`glass-card glass-card-hover rounded-2xl border flex flex-col justify-between overflow-hidden cursor-pointer ${sample.borderClass}`}
            >
              {/* Card Top */}
              <div className="px-5 pt-5 pb-4 border-b border-white/10">
                {sample.archetype && (
                  <div className="mb-3 inline-flex items-center gap-1.5 rounded-md border border-red-500/30 bg-red-500/10 px-2.5 py-1 text-[11px] font-mono font-bold uppercase tracking-wider text-red-400">
                    {sample.archetype}
                  </div>
                )}

                <div className="flex items-start justify-between gap-3 mb-1">
                  <div>
                    <p className="text-xs text-fog mb-0.5 font-light">Sample scan</p>
                    <h3 className="text-base font-medium text-frost leading-tight">{sample.role}</h3>
                    <p className="text-sm text-mist font-light">{sample.company}</p>
                  </div>

                  <div className={`flex-shrink-0 flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold uppercase tracking-wide border ${sample.badgeClass}`}>
                    {sample.verdict === 'Safe' && <CheckCircle2 className="w-3.5 h-3.5" />}
                    {sample.verdict === 'Caution' && <AlertTriangle className="w-3.5 h-3.5" />}
                    {sample.verdict === 'Risky' && <ShieldAlert className="w-3.5 h-3.5" />}
                    <span>{sample.verdict}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 mt-3">
                  <p className="text-xs text-fog font-light">Legitimacy score</p>
                  <span className={`text-2xl font-bold font-mono ${sample.scoreClass}`}>
                    {sample.score}<span className="text-sm font-normal text-fog">/100</span>
                  </span>
                  {sample.score === 0 && (
                    <span className="ml-1 text-[10px] font-mono font-bold uppercase tracking-wider text-red-400 border border-red-500/30 rounded px-1.5 py-0.5">
                      MAX RISK
                    </span>
                  )}
                </div>
              </div>

              {/* Card Body with bullet checks */}
              <div className="px-5 py-4 flex-1 space-y-2.5 bg-black/20">
                {sample.points.map((pt, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    {pt.safe ? (
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                    ) : (
                      <AlertTriangle className={`h-4 w-4 flex-shrink-0 mt-0.5 ${pt.minor ? 'text-amber-400' : 'text-red-400'}`} />
                    )}
                    <span className="text-xs text-mist leading-relaxed font-light">{pt.text}</span>
                  </div>
                ))}
              </div>

              {/* Card Footer matching Screenshot 2 */}
              <div className={`px-5 py-4 border-t text-xs leading-relaxed font-light ${sample.footerBg}`}>
                {sample.linkText && (
                  <div className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-400 hover:text-emerald-300 transition-colors mb-2">
                    <span>{sample.linkText}</span>
                  </div>
                )}
                <p className={`font-medium ${sample.footerText}`}>{sample.footerAdvice}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Big Bottom Action CTA Button matching Screenshot 2 */}
        <div className="mt-10 sm:mt-12 text-center space-y-3">
          <button
            onClick={handleScrollToScanner}
            className="inline-flex items-center gap-2 rounded-full bg-emerald-500 hover:bg-emerald-400 active:bg-emerald-600 px-7 py-3.5 text-sm font-semibold text-white shadow-emerald-button hover:shadow-emerald-glow transition-all duration-150"
          >
            <span>Scan your job now</span>
            <ArrowRight className="h-4 w-4" />
          </button>
          <p className="text-xs text-fog font-light">Free · Private · No account required</p>
        </div>

      </div>
    </section>
  );
};

export default SampleResultsShowcase;
