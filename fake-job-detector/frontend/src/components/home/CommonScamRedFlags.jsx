import React from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, Search, ExternalLink, ArrowRight } from 'lucide-react';

const RED_FLAGS = [
  'Salary is unrealistically high for the role',
  'No interview — or only a WhatsApp/Telegram chat',
  'Recruiter uses Gmail, Yahoo, or another free email',
  'Upfront payment required for training or equipment',
  "Job doesn't appear on the company's careers page",
  'Requests for SSN, bank details, or ID scans early',
  'Vague job description with no real responsibilities',
  'Urgency pressure: "accept in 24 hours"',
  'Generic AI-generated text, oddly non-specific',
  'Fake check or "overpayment" scheme to wire back',
];

const FRAUD_TYPES = [
  {
    name: 'Ghost Jobs',
    desc: "Real-looking postings for positions that don't exist — used to harvest CVs or string applicants along.",
  },
  {
    name: 'Fake Check Scams',
    desc: 'You\'re "hired," sent a fake paycheck, and asked to wire back the "extra." The check bounces.',
  },
  {
    name: 'Task Scams',
    desc: '"Work-from-home" jobs that pay small amounts before larger sums disappear.',
  },
  {
    name: 'Identity Harvest',
    desc: 'Fake applications that collect SSN, passport photos, and bank info under the guise of onboarding.',
  },
  {
    name: 'AI-Generated Fakes',
    desc: 'Fully fabricated postings created by generative AI — indistinguishable without verification tools.',
  },
  {
    name: 'Advance Fee Scams',
    desc: 'Requires upfront payment for a "guaranteed" remote job, visa, or placement that never materialises.',
  },
];

export const CommonScamRedFlags = () => {
  return (
    <section className="bg-[#050a08] py-20 sm:py-24 border-t border-white/5" aria-labelledby="red-flags-heading">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        
        {/* Top explanatory text matching reference */}
        <div className="max-w-3xl mx-auto text-center mb-12 space-y-2">
          <p className="text-xs sm:text-sm text-mist leading-relaxed font-light">
            A job scam is a fraudulent employment offer designed to steal your money, personal information, or identity. According to the{' '}
            <a
              href="https://consumer.ftc.gov/articles/job-scams"
              target="_blank"
              rel="noopener noreferrer"
              className="text-emerald-400 hover:text-emerald-300 transition-colors underline underline-offset-2"
            >
              FTC
            </a>
            , job scams cost Americans hundreds of millions of dollars every year — and with AI-generated fake postings now flooding every major job board, spotting them has never been harder.
          </p>
        </div>

        {/* 2-Column Grid matching Screenshot 4 */}
        <div className="grid gap-6 md:grid-cols-2 items-stretch">
          
          {/* Left Card: Common Job Scam Red Flags */}
          <div className="glass-card rounded-2xl p-6 sm:p-8 border border-white/10 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-frost font-semibold text-base sm:text-lg pb-2 border-b border-white/10">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                <h3>Common Job Scam Red Flags</h3>
              </div>

              <ul className="space-y-2.5">
                {RED_FLAGS.map((flag, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 text-xs text-mist leading-relaxed font-light">
                    <AlertTriangle className="w-3.5 h-3.5 text-red-400/80 flex-shrink-0 mt-0.5" />
                    <span>{flag}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Right Card: Types of Job Fraud to Know */}
          <div className="glass-card rounded-2xl p-6 sm:p-8 border border-white/10 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-frost font-semibold text-base sm:text-lg pb-2 border-b border-white/10">
                <Search className="w-5 h-5 text-emerald-400" />
                <h3>Types of Job Fraud to Know</h3>
              </div>

              <div className="space-y-3">
                {FRAUD_TYPES.map((type, idx) => (
                  <div key={idx} className="text-xs leading-relaxed">
                    <span className="font-semibold text-frost">{type.name}: </span>
                    <span className="text-mist font-light">{type.desc}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Bottom Sources Links */}
            <div className="pt-5 mt-4 border-t border-white/10 flex items-center gap-3 text-[11px] text-fog">
              <span>Sources:</span>
              <a
                href="https://consumer.ftc.gov"
                target="_blank"
                rel="noopener noreferrer"
                className="text-emerald-400/90 hover:text-emerald-300 transition-colors inline-flex items-center gap-1"
              >
                FTC.gov <ExternalLink className="w-2.5 h-2.5" />
              </a>
              <span className="text-white/20">·</span>
              <a
                href="https://www.bbb.org"
                target="_blank"
                rel="noopener noreferrer"
                className="text-emerald-400/90 hover:text-emerald-300 transition-colors inline-flex items-center gap-1"
              >
                BBB.org <ExternalLink className="w-2.5 h-2.5" />
              </a>
              <span className="text-white/20">·</span>
              <a
                href="https://www.ic3.gov"
                target="_blank"
                rel="noopener noreferrer"
                className="text-emerald-400/90 hover:text-emerald-300 transition-colors inline-flex items-center gap-1"
              >
                FBI IC3 <ExternalLink className="w-2.5 h-2.5" />
              </a>
            </div>
          </div>

        </div>

        {/* Bottom CTA Guide Link */}
        <div className="mt-8 text-center">
          <Link
            to="/guides/job-scam-red-flags"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-400 hover:text-emerald-300 transition-colors"
          >
            <span>Read our complete Job Scam Red Flags Guide</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

      </div>
    </section>
  );
};

export default CommonScamRedFlags;
