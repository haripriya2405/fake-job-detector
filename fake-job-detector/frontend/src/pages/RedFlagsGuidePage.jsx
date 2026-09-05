import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  ArrowLeft,
  AlertTriangle,
  Flame,
  CheckCircle2,
  DollarSign,
  Lock,
  Search,
  Building,
  Mail,
  Smartphone,
  HelpCircle,
} from 'lucide-react';
import { Button } from '../components/ui/Button';

const SCAM_GUIDES = [
  {
    id: 'task-scam',
    title: 'Task Scams (App Optimization / Store Ranking)',
    badge: 'Critical Threat',
    badgeColor: 'bg-red-500/15 text-red-400 border-red-500/30',
    summary: 'Scammers hire candidates to complete "simple tasks" like clicking app reviews, liking products, or testing crypto apps with promises of daily commission payouts.',
    indicators: [
      'Daily pay promised for basic repetitive clicking ($200–$500/day)',
      'Communication strictly routed via Telegram or WhatsApp',
      'Small payouts given at first to build trust, followed by "deposit" demands to unlock funds',
      'Fake web portal with inflated virtual balances that cannot be withdrawn without a fee',
    ],
    example: '"Earn $300-$500 daily helping boost merchant store rankings on our cloud platform. 30-40 minutes per task. Withdraw anytime via USDT or bank transfer. Contact our mentor on Telegram to get started."',
    whatToDo: 'Cease communication immediately. Never send cryptocurrency or deposit money to unlock claimed earnings. Report the recruiter on the platform where they contacted you.',
  },
  {
    id: 'fake-check',
    title: 'Fake Check & Home Equipment Scams',
    badge: 'High Financial Risk',
    badgeColor: 'bg-red-500/15 text-red-400 border-red-500/30',
    summary: 'The employer sends a counterfeit cashier check to "purchase home office supplies" from their designated "vendor". When the check bounces, you owe the full bank balance.',
    indicators: [
      'Employer mails or emails a digital check for $2,000–$5,000 before you start work',
      'Strict instruction to deposit the check and wire/Zelle the excess to a specific hardware vendor',
      'Immediate pressure to execute the transfer before the bank clears the check',
      'No formal technical or face-to-face video interview conducted',
    ],
    example: '"Welcome to the team! We are dispatching a cashier check of $3,500. Please deposit it via your mobile app and transfer $2,800 to our approved IT supplier via Zelle for your Apple workstation."',
    whatToDo: 'Do not deposit the check. Take the physical check to your local bank branch and notify fraud prevention. Legitimate corporations ship hardware directly—they never send equipment checks.',
  },
  {
    id: 'advance-fee',
    title: 'Advance Fee & Mandatory Paid Training Scams',
    badge: 'Direct Extortion',
    badgeColor: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    summary: 'You are offered a role but told you must first pay for a mandatory background check, software license, or certification course through a specific link.',
    indicators: [
      'Requirement to pay upfront fees before receiving an official contract',
      'Mandatory proprietary software or certification that costs $100–$400',
      'Guaranteed job placement conditioned upon purchasing training materials',
    ],
    example: '"Your application has been approved. To finalize your employment file, you must complete your background verification through our partner portal for $89 (refundable after 30 days)."',
    whatToDo: 'Never pay any money as a prerequisite for employment. Legitimate employers bear all costs for background checks, training, and software licenses.',
  },
  {
    id: 'identity-harvest',
    title: 'Identity Theft & Premature SSN Harvesting',
    badge: 'Identity Threat',
    badgeColor: 'bg-red-500/15 text-red-400 border-red-500/30',
    summary: 'Fraudulent postings designed solely to collect Social Security Numbers, banking details, passport scans, or credit reports before an interview takes place.',
    indicators: [
      'Application form demands full SSN, date of birth, and bank routing numbers upfront',
      'Requirement to submit photos of driver’s license or passport on unsecured forms',
      'Vague company details with no physical address or registered business entity',
    ],
    example: '"Before we can schedule your interview, please complete the onboarding form including your SSN, banking info for direct deposit, and a photo of your state ID."',
    whatToDo: 'Never share your SSN or banking details until you have a signed official offer from a verified employer with confirmed corporate presence.',
  },
  {
    id: 'recruiter-impersonation',
    title: 'Recruiter Impersonation & Free Webmail Traps',
    badge: 'Phishing Vector',
    badgeColor: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    summary: 'Scammers pretend to represent Fortune 500 companies using lookalike domains or free webmail addresses (@gmail.com, @yahoo.com) rather than corporate servers.',
    indicators: [
      'Recruiter uses a Gmail/Outlook account claiming to represent a multinational corporation',
      'Lookalike domain registered recently (e.g., stripe-careers-portal.net instead of stripe.com)',
      'Recruiter cannot be found on LinkedIn under the claimed organization',
    ],
    example: '"I am Jessica Miller, Senior Talent Lead at Amazon Global. We reviewed your resume for our Remote Analyst position. Please reach me at amazon.talent.hiring.team@gmail.com."',
    whatToDo: 'Always cross-reference the sender’s email domain with the company’s official web address. Message the verified recruiter directly on LinkedIn to confirm authenticity.',
  },
  {
    id: 'ghost-jobs',
    title: 'Ghost Jobs & Deceptive Postings',
    badge: 'Deceptive Practice',
    badgeColor: 'bg-skywash/15 text-skywash border-skywash/30',
    summary: 'Job listings posted by companies with no immediate intention to hire, used to collect candidate resumes, build talent pools, or project artificial growth to investors.',
    indicators: [
      'Job continuously reposted for 6+ months with no active hiring updates',
      'Generic job descriptions with no specific team or project responsibilities',
      'Posting does not appear on the official corporate ATS portal',
    ],
    example: '"General Software Engineering Talent Pipeline — We are always looking for exceptional talent across all technical domains. Continuous open hiring."',
    whatToDo: 'Verify if the specific role exists on the company’s official ATS (Greenhouse, Lever, Workday) and apply directly through the official website.',
  },
];

export const RedFlagsGuidePage = () => {
  const navigate = useNavigate();

  return (
    <div className="space-y-12 max-w-5xl mx-auto pb-16 pt-4">
      
      {/* Top Header */}
      <div className="space-y-4">
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs text-fog hover:text-frost transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Job Scam Checker</span>
        </Link>

        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/25 bg-emerald-500/10 text-emerald-400 text-xs font-mono font-medium">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Fraud Intelligence Directory</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-semibold text-frost tracking-tight">
            Job Scam Red Flags Guide
          </h1>
          <p className="text-mist text-sm sm:text-base max-w-2xl font-light leading-relaxed">
            Learn the core fraud vectors used by recruitment scammers, how to spot them in job postings and recruiter emails, and actionable steps to protect yourself.
          </p>
        </div>
      </div>

      {/* Guide Cards */}
      <div className="space-y-6">
        {SCAM_GUIDES.map((guide) => (
          <div
            key={guide.id}
            className="glass-card rounded-2xl p-6 sm:p-7 border border-white/10 space-y-4"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-white/10">
              <h2 className="text-lg sm:text-xl font-semibold text-frost">
                {guide.title}
              </h2>
              <span className={`self-start sm:self-auto px-2.5 py-0.5 rounded-full text-xs font-mono font-bold border ${guide.badgeColor}`}>
                {guide.badge}
              </span>
            </div>

            <p className="text-sm text-mist leading-relaxed font-light">
              {guide.summary}
            </p>

            {/* Red Flag Indicators */}
            <div className="space-y-2 pt-1">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-fog">
                Common Warning Signals
              </h3>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {guide.indicators.map((ind, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-xs text-mist leading-relaxed">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                    <span>{ind}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Real Example Box */}
            <div className="p-3.5 rounded-xl bg-black/40 border border-white/10 space-y-1">
              <span className="text-[10px] font-mono uppercase tracking-wider text-fog">
                Simulated Scammer Message
              </span>
              <p className="text-xs text-slate-300 font-mono italic leading-relaxed">
                {guide.example}
              </p>
            </div>

            {/* What to do box */}
            <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/20 flex items-start gap-2 text-xs text-emerald-300 leading-relaxed">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <strong className="font-semibold text-emerald-200">Recommended Action: </strong>
                <span>{guide.whatToDo}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Bottom CTA */}
      <div className="p-8 rounded-2xl glass-card border border-emerald-500/20 text-center space-y-4 shadow-emerald-glow">
        <h3 className="text-xl font-semibold text-frost">
          Received a suspicious job offer or recruiter message?
        </h3>
        <p className="text-xs sm:text-sm text-mist max-w-lg mx-auto font-light">
          Paste the text into SentinelJob AI for an automated 50+ check scan across 8 signal layers in under 60 seconds.
        </p>
        <Button
          variant="primary"
          size="lg"
          onClick={() => navigate('/analyze')}
          className="bg-emerald-500 hover:bg-emerald-400 shadow-emerald-button"
        >
          Scan Your Job Posting Now →
        </Button>
      </div>

    </div>
  );
};

export default RedFlagsGuidePage;
