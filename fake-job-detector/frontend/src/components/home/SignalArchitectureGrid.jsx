import React from 'react';

const SIGNAL_LAYERS = [
  {
    num: '01',
    title: 'Company Authentication',
    desc: 'Domain age, SSL, WHOIS data, business registry, LinkedIn company page. Flags domains under 90 days old.',
  },
  {
    num: '02',
    title: 'Careers Page Verification',
    desc: 'Live check — does the specific role exist on the official ATS listing? The single strongest signal of legitimacy.',
  },
  {
    num: '03',
    title: 'Recruiter Identity',
    desc: 'Cross-references recruiter names and emails against the employer\'s verified LinkedIn employee base. Free-email detection.',
  },
  {
    num: '04',
    title: 'Salary Benchmarking',
    desc: 'Compares offered salary against Glassdoor, LinkedIn Salary, and BLS data. Flags offers 50%+ above role norms.',
  },
  {
    num: '05',
    title: 'Scam Pattern Detection',
    desc: '30+ AI-trained patterns: task scams, fake checks, identity harvest, advance fees, ghost jobs, impersonation.',
  },
  {
    num: '06',
    title: 'Contact Validation',
    desc: 'Phone/email cross-reference against FTC, IC3, and BBB fraud databases. Recycled scammer identifiers flagged.',
  },
  {
    num: '07',
    title: 'Domain & SSL Intelligence',
    desc: 'Typosquatting, homoglyph attacks, registrar reputation, MX record validity, redirect chain analysis.',
  },
  {
    num: '08',
    title: 'Live Threat Intelligence',
    desc: 'Real-time cross-check: FTC alerts, BBB Scam Tracker, IC3 filings, Reddit reports, and our own verified scam database.',
  },
];

export const SignalArchitectureGrid = () => {
  return (
    <section id="features" className="bg-[#050a08] py-20 sm:py-24 border-t border-dashed border-white/10" aria-labelledby="features-heading">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header matching Screenshot 3 */}
        <div className="text-center mb-12 sm:mb-14">
          <div className="flex items-center justify-center gap-4">
            <span className="eyebrow-line" aria-hidden="true" />
            <p className="text-[11px] font-mono font-medium uppercase tracking-[0.18em] text-fog">
              Signal Architecture
            </p>
            <span className="eyebrow-line eyebrow-line-r" aria-hidden="true" />
          </div>
          <h2 id="features-heading" className="mt-4 font-medium text-frost tracking-tight text-2xl sm:text-3xl lg:text-4xl">
            8 layers · parallel execution
          </h2>
          <p className="mt-4 text-mist max-w-2xl mx-auto font-light text-base sm:text-lg leading-relaxed">
            Every scan runs the full eight-layer signal stack. Checks run in parallel where possible, and every signal is weighted into a single <span className="text-frost font-medium">0–100 risk score</span>.
          </p>
        </div>

        {/* 8-Card Grid matching Screenshot 3 */}
        <div className="grid sm:grid-cols-2 gap-px bg-white/10 rounded-2xl overflow-hidden shadow-2xl border border-white/10">
          {SIGNAL_LAYERS.map((layer) => (
            <div
              key={layer.num}
              className="bg-[#07100c] px-6 py-5 flex items-start gap-4 hover:bg-[#0a1710] transition-colors"
            >
              <span className="text-[11px] font-mono font-medium text-emerald-500/70 mt-0.5 w-6 flex-shrink-0 tabular-nums">
                {layer.num}
              </span>
              <div>
                <p className="text-sm font-semibold text-frost">
                  {layer.title}
                </p>
                <p className="text-xs text-fog mt-1 leading-relaxed font-light">
                  {layer.desc}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Footnote matching Screenshot 3 */}
        <p className="mt-6 text-center text-xs text-fog font-light">
          50+ total checks across all 8 layers · single 0–100 risk score · clear evidence for every verdict
        </p>

      </div>
    </section>
  );
};

export default SignalArchitectureGrid;
