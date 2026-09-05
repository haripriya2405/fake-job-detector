import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Linkedin, Twitter, Github } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="border-t border-white/10 bg-[#030806] text-fog font-light">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-10 lg:gap-14">
          
          {/* Brand Info (4 cols) */}
          <div className="md:col-span-4 space-y-4">
            <Link to="/" className="flex items-center gap-2.5 group">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
              </div>
              <span className="text-base font-semibold text-frost tracking-tight">SentinelJob AI</span>
            </Link>
            
            <p className="text-xs text-mist max-w-sm leading-relaxed font-light">
              Stop job scams before you apply. AI-powered fraud detection with evidence behind every verdict.
            </p>

            <div className="flex items-center gap-3 text-fog pt-1">
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-frost transition-colors p-1"
                aria-label="LinkedIn"
              >
                <Linkedin className="w-4 h-4" />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-frost transition-colors p-1"
                aria-label="Twitter"
              >
                <Twitter className="w-4 h-4" />
              </a>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-frost transition-colors p-1"
                aria-label="GitHub"
              >
                <Github className="w-4 h-4" />
              </a>
            </div>
          </div>

          {/* Links 1: Resources (3 cols) */}
          <div className="md:col-span-3 space-y-3">
            <h4 className="text-xs font-mono font-semibold uppercase tracking-[0.16em] text-frost">
              Resources
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link to="/guides/job-scam-red-flags" className="hover:text-frost transition-colors">
                  After a Job Scam: Recovery Steps
                </Link>
              </li>
              <li>
                <Link to="/guides/job-scam-red-flags" className="hover:text-frost transition-colors">
                  Job Scam Red Flags Guide
                </Link>
              </li>
              <li>
                <Link to="/guides/job-scam-red-flags" className="hover:text-frost transition-colors">
                  LinkedIn Job Scams 2026
                </Link>
              </li>
              <li>
                <Link to="/guides/job-scam-red-flags" className="hover:text-frost transition-colors">
                  Spot Fake Indeed Jobs
                </Link>
              </li>
              <li>
                <Link to="/guides/job-scam-red-flags" className="hover:text-frost transition-colors">
                  AI-Generated Fake Offers
                </Link>
              </li>
              <li>
                <Link to="/analyze" className="hover:text-frost transition-colors">
                  Job Posting Scam Checks
                </Link>
              </li>
              <li>
                <Link to="/alerts" className="hover:text-frost transition-colors text-emerald-400 font-medium">
                  Live Scam Alerts
                </Link>
              </li>
              <li>
                <Link to="/" className="hover:text-frost transition-colors">
                  About Us
                </Link>
              </li>
            </ul>
          </div>

          {/* Links 2: Legal (2 cols) */}
          <div className="md:col-span-2 space-y-3">
            <h4 className="text-xs font-mono font-semibold uppercase tracking-[0.16em] text-frost">
              Legal
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link to="/" className="hover:text-frost transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/" className="hover:text-frost transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link to="/" className="hover:text-frost transition-colors">
                  Cookie Policy
                </Link>
              </li>
              <li>
                <Link to="/" className="hover:text-frost transition-colors">
                  Affiliate Disclosure
                </Link>
              </li>
            </ul>
          </div>

          {/* Links 3: Support (3 cols) */}
          <div className="md:col-span-3 space-y-3">
            <h4 className="text-xs font-mono font-semibold uppercase tracking-[0.16em] text-frost">
              Support
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link to="/analyze" className="hover:text-frost transition-colors">
                  Help & FAQ
                </Link>
              </li>
              <li>
                <Link to="/settings" className="hover:text-frost transition-colors">
                  Contact Us
                </Link>
              </li>
              <li className="pt-1">
                <a
                  href="mailto:support@sentineljob.ai"
                  className="text-emerald-400/90 hover:text-emerald-300 transition-colors font-mono text-[11px]"
                >
                  support@sentineljob.ai
                </a>
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom Copyright Strip matching Page 5 */}
        <div className="mt-12 pt-8 border-t border-white/10 text-center text-[11px] text-fog font-light">
          © 2026 SentinelJob AI. All rights reserved. SentinelJob AI is a dedicated recruitment security intelligence platform. Protecting job seekers from employment fraud.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
