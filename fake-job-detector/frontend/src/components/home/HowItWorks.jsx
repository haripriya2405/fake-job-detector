import React from 'react';

export const HowItWorks = () => {
  return (
    <section id="how" className="bg-[#050a08] py-20 sm:py-24 lg:py-28 border-t border-dashed border-white/10" aria-labelledby="how-heading">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center mb-12 sm:mb-14">
          <div className="flex items-center justify-center gap-4">
            <span className="eyebrow-line" aria-hidden="true" />
            <p className="text-[11px] font-mono font-medium uppercase tracking-[0.18em] text-fog">
              How it works
            </p>
            <span className="eyebrow-line eyebrow-line-r" aria-hidden="true" />
          </div>
          <h2 id="how-heading" className="mt-4 font-medium text-frost tracking-tight text-2xl sm:text-3xl lg:text-4xl">
            From paste to verdict in 60 seconds
          </h2>
          <p className="mt-4 text-mist max-w-2xl mx-auto font-light text-base sm:text-lg">
            Three steps. No setup required.
          </p>
        </div>

        {/* 3 Step Cards */}
        <div className="grid gap-6 sm:gap-8 md:grid-cols-3">
          
          {/* Card 1 */}
          <div className="glass-card glass-card-hover rounded-2xl p-6 sm:p-7 flex flex-col justify-between border border-white/10">
            <div>
              <div className="flex h-11 w-11 items-center justify-center rounded-full bg-white/5 shadow-hairline-inset text-emerald-300 text-base font-mono font-medium mb-5">
                1
              </div>
              <h3 className="text-lg font-medium text-frost mb-2">Paste the job</h3>
              <p className="text-sm text-mist leading-relaxed font-light">
                Copy the full job posting text or URL and paste it in. Our job scam checker automatically extracts company name, salary, contact info, and key details.
              </p>
            </div>
          </div>

          {/* Card 2 */}
          <div className="glass-card glass-card-hover rounded-2xl p-6 sm:p-7 flex flex-col justify-between border border-white/10">
            <div>
              <div className="flex h-11 w-11 items-center justify-center rounded-full bg-white/5 shadow-hairline-inset text-emerald-300 text-base font-mono font-medium mb-5">
                2
              </div>
              <h3 className="text-lg font-medium text-frost mb-2">AI verifies 50+ sources</h3>
              <p className="text-sm text-mist leading-relaxed font-light">
                We cross-check the company careers page, recruiter identity, salary data, fraud databases, BBB complaints, and AI-pattern analysis — simultaneously.
              </p>
            </div>
          </div>

          {/* Card 3 */}
          <div className="glass-card glass-card-hover rounded-2xl p-6 sm:p-7 flex flex-col justify-between border border-white/10">
            <div>
              <div className="flex h-11 w-11 items-center justify-center rounded-full bg-white/5 shadow-hairline-inset text-emerald-300 text-base font-mono font-medium mb-5">
                3
              </div>
              <h3 className="text-lg font-medium text-frost mb-2">Get your verdict</h3>
              <p className="text-sm text-mist leading-relaxed font-light">
                A clear Safe / Caution / Risky score with cited evidence, specific red and green flags, and actionable next steps to protect yourself.
              </p>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
};

export default HowItWorks;
