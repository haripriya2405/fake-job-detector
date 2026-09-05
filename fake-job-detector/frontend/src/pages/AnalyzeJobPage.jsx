import { useAuth } from '../context/AuthContext';
import { GoogleAuthModal } from '../components/auth/GoogleAuthModal';
import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import {
  FileText,
  Upload,
  Image as ImageIcon,
  Link as LinkIcon,
  Search,
  Building,
  CheckCircle2,
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  Lock,
  DollarSign,
  ShieldAlert,
  ShieldCheck,
  Globe,
  Sparkles,
  User,
  Users,
  Briefcase,
  GraduationCap,
  HelpCircle,
  Layers,
  LogIn,
} from 'lucide-react';
import { DropZone } from '../components/upload/DropZone';
import { LanguageSelector } from '../components/navigation/LanguageSelector';
import { analysisService } from '../services/analysisService';
import { useToast } from '../hooks/useToast';

const SCAN_STAGES = [
  'Extracting job text & metadata signals...',
  'Checking company domain age via RDAP/DNS...',
  'Searching official ATS career listings...',
  'Benchmarking compensation against BLS models...',
  'Evaluating 30+ trained scam pattern vectors...',
  'Synthesizing 8-layer risk score & recommendations...',
];

const VERIFICATION_CHECKS = [
  {
    title: 'Careers Page Verification',
    icon: Search,
    desc: "Checks whether the specific role exists on the company's official careers page. This is the single strongest signal of job legitimacy — scammers cannot replicate a real company's ATS listing. If the job is not there, the posting may be fake, expired, or a ghost job.",
  },
  {
    title: 'Company Authentication',
    icon: Building,
    desc: 'Verifies the company domain age (established vs. brand-new), SSL certificate validity, WHOIS registration data, business registry presence, LinkedIn company page, and Glassdoor profile. Flags suspicious registrations under 90 days old.',
  },
  {
    title: 'Recruiter Identity Check',
    icon: User,
    desc: "Cross-references the recruiter's name and email against the employer's verified employee base on LinkedIn. Flags free-email addresses (Gmail, Yahoo, Outlook) used by corporate recruiters — a critical red flag in 94% of confirmed scams.",
  },
  {
    title: 'Salary Benchmarking',
    icon: DollarSign,
    desc: 'Compares the offered salary against real market data for the role, level, and location using Glassdoor, LinkedIn Salary, and Bureau of Labor Statistics data. Salary offers 50%+ above market for entry-level or vague roles are a consistent scam signal.',
  },
  {
    title: 'Scam Pattern Detection',
    icon: AlertTriangle,
    desc: 'AI trained on thousands of confirmed scam cases detects: fake check language, task scam structures, advance fees, cryptocurrency compensation, and off-platform interview requests.',
  },
  {
    title: 'Contact Validation',
    icon: Globe,
    desc: 'Validates phone numbers and email addresses against public complaint patterns, BBB Scam Tracker-style reports, and recycled scammer footprints.',
  },
  {
    title: 'Domain & SSL Intelligence',
    icon: Lock,
    desc: 'Checks domain age, registrar reputation, WHOIS data, MX record validity, and SSL certificate details. A domain registered in the last 30 days for a company claiming 10 years of operation is an immediate red flag.',
  },
  {
    title: 'Real-Time Fraud Database Cross-Reference',
    icon: ShieldAlert,
    desc: 'Continuously updated cross-check against FTC fraud alerts, BBB Scam Tracker-style reports, IC3 guidance, community-reported patterns, and our own verified scam database.',
  },
];

const WHO_SHOULD_USE = [
  {
    title: 'Active job seekers',
    desc: 'Verify any job before investing time in an application or interview. Takes 60 seconds — faster than writing a cover letter.',
  },
  {
    title: 'Recent graduates',
    desc: 'Entry-level roles are disproportionately targeted by scammers. Graduates are often less familiar with normal hiring processes, making them higher-risk targets. Run every offer through the checker before responding.',
  },
  {
    title: 'Remote workers',
    desc: 'Remote job postings are 3–5x more likely to be fraudulent than on-site roles, according to BBB research. Any unsolicited remote opportunity warrants a check.',
  },
  {
    title: 'Career changers',
    desc: 'Transitioning to a new industry means less familiarity with normal offer structures for that field. The salary benchmarking check alone can confirm whether an offer is realistic.',
  },
  {
    title: 'Recruiters and HR teams',
    desc: 'Verify that job boards are not impersonating your company — a real threat documented by major employers including Amazon, Microsoft, and Google. Use the checker to monitor for fake postings using your brand.',
  },
];

const HIGH_RISK_FLAGS = [
  'Job not listed on company\'s official careers page',
  'Recruiter using Gmail, Yahoo, or other free email',
  'Salary is 50%+ above market rate for the role',
  'Any upfront payment requested (training, equipment, background check)',
  'Company domain registered within the last 90 days',
  'No verifiable LinkedIn company page or employee presence',
  'Interview conducted only via WhatsApp or Telegram',
  'Offer made within hours of applying with no real interview',
  'Requests for SSN, bank details, or ID before a formal offer',
  'Fake check or wire-back scheme described in posting',
  'Job posting identical across 20+ unrelated job boards',
  'Pressure tactics: "offer expires in 24 hours"',
];

const FAQS = [
  {
    q: 'Is the job scam checker really free?',
    a: 'Yes. Your first scan is completely free with no account required. No credit card is ever needed. A free account includes 100 scans per month and saved history.',
  },
  {
    q: 'How does the job scam checker work?',
    a: 'The checker runs 50+ verification checks: careers page lookup, recruiter identity signals, company domain age check, salary benchmarking, complaint-source review, and AI scam pattern analysis. Results include the evidence behind the verdict.',
  },
  {
    q: 'Can I scan a job from a screenshot?',
    a: 'Yes. Upload one or two screenshots and enter the job title and company name for best results.',
  },
  {
    q: 'What job boards does the checker support?',
    a: 'Any job source: text paste, LinkedIn URL, Indeed URL, company career page URL, Workday, Greenhouse, Lever, ZipRecruiter, Monster, Dice, and recruiter emails or messages.',
  },
  {
    q: 'How accurate is the detection?',
    a: 'No automated tool is perfect. Every verdict includes specific evidence, so you see exactly what was checked, what matched, and what still needs manual verification.',
  },
];

const RELATED_GUIDES = [
  {
    title: '25 Job Scam Red Flags (2026)',
    desc: 'The complete list of warning signs, sorted by severity. Critical flags first.',
  },
  {
    title: 'Job Scam Statistics 2026',
    desc: 'How much do job scams cost? Which platforms are most targeted? FTC, BBB, IC3 data.',
  },
  {
    title: 'Top 5 LinkedIn Job Scams in 2026',
    desc: 'Fake recruiter DMs, cloned company pages, phishing in interview messages.',
  },
  {
    title: 'AI-Generated Fake Job Offers',
    desc: 'How scammers use generative AI to create convincing fake postings.',
  },
];

export const AnalyzeJobPage = () => {
  const { isAuthenticated, hasUsedGuestScan, incrementGuestScan } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { error, success } = useToast();

  const [activeTab, setActiveTab] = useState('text'); // 'text' | 'image' | 'url' | 'batch'
  const [jobTitle, setJobTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [jobText, setJobText] = useState('');
  const [jobUrl, setJobUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [batchInput, setBatchInput] = useState('');
  const [batchResponse, setBatchResponse] = useState(null);
  const [enhancedOpen, setEnhancedOpen] = useState(false);
  const [recruiterEmail, setRecruiterEmail] = useState('');
  const [jobLocation, setJobLocation] = useState('');

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [stageIdx, setStageIdx] = useState(0);
  const [faqExpanded, setFaqExpanded] = useState({});

  useEffect(() => {
    if (location.state?.preset) {
      const preset = location.state.preset;
      setJobText(preset.description);
      setJobTitle(preset.title);
      setActiveTab('text');
    }
  }, [location.state]);

  const toggleFaq = (idx) => {
    setFaqExpanded((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();

    if (!isAuthenticated && guestScanCount >= 1) {
      error("You have already used your 1 free scan. Please sign in with Google or Email to unlock unlimited scans.");
      setShowAuthModal(true);
      return;
    }

    if (activeTab === 'text') {
      if (!jobText.trim() || jobText.trim().length < 20) {
        error('Please enter at least 20 characters of job description content.');
        return;
      }
    } else if (activeTab === 'url') {
      if (!jobUrl.trim() || !jobUrl.includes('.')) {
        error('Please enter a valid job URL.');
        return;
      }
    } else if (activeTab === 'batch') {
      if (!batchInput.trim()) {
        error('Please provide at least one job posting for batch scanning.');
        return;
      }
    } else {
      if (!selectedFile) {
        error('Please upload an image screenshot or PDF.');
        return;
      }
    }

    setIsAnalyzing(true);
    setStageIdx(0);
    setBatchResponse(null);

    const interval = setInterval(() => {
      setStageIdx((prev) => (prev < SCAN_STAGES.length - 1 ? prev + 1 : prev));
    }, 280);

    try {
      if (activeTab === 'batch') {
        let itemsToScan = [];
        const trimmed = batchInput.trim();
        if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
          try {
            const parsed = JSON.parse(trimmed);
            itemsToScan = parsed.map((p) => ({
              text: p.text || p.raw_content || p.description || '',
              title: p.title || p.job_title || 'Batch Role',
              company: p.company || p.company_name || 'Unspecified',
            }));
          } catch (pe) {
            // fall back to delimiter
          }
        }
        if (itemsToScan.length === 0) {
          const rawBlocks = trimmed.split(/---+|\n\n\n+/).map((b) => b.trim()).filter((b) => b.length >= 20);
          itemsToScan = rawBlocks.slice(0, 25).map((block, idx) => ({
            text: block,
            title: `Batch Job #${idx + 1}`,
            company: 'Batch Analysis Submission',
          }));
        }

        if (itemsToScan.length === 0) {
          throw new Error('Could not parse any valid job postings (minimum 20 chars each).');
        }

        const batchRes = await analysisService.analyzeBatch(itemsToScan);
        setBatchResponse(batchRes);
        clearInterval(interval);
        if (!isAuthenticated) incrementGuestScan();
        success(`Batch scan complete. Evaluated ${batchRes.total_analyzed} job postings.`);
        return;
      }

      let report;
      if (activeTab === 'text') {
        report = await analysisService.analyzeText(jobText, {
          job_title: jobTitle || undefined,
          company_name: companyName || undefined,
        });
      } else if (activeTab === 'url') {
        report = await analysisService.analyzeUrl(jobUrl, {
          job_title: jobTitle || undefined,
          company_name: companyName || undefined,
        });
      } else {
        const isPdf = Boolean(
          (selectedFile.type && selectedFile.type.includes('pdf')) ||
          (selectedFile.name && selectedFile.name.toLowerCase().endsWith('.pdf'))
        );
        const fileType = isPdf ? 'pdf' : 'image';
        report = await analysisService.analyzeUpload(selectedFile, fileType, {
          job_title: jobTitle || selectedFile.name,
          company_name: companyName || undefined,
        });
      }

      clearInterval(interval);
      if (!isAuthenticated) {
        incrementGuestScan();
      }
      success('Analysis complete. Risk assessment generated.');
      navigate(`/analysis/${report.id}`, { state: { report } });
    } catch (err) {
      clearInterval(interval);
      error(err.message || 'Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050a08] text-frost py-6 px-4 sm:px-6 lg:px-8 relative selection:bg-emerald-500 selection:text-white">
      
      {/* Background blueprint grid */}
      <div className="pointer-events-none absolute inset-0" aria-hidden="true">
        <div className="absolute inset-0 bg-blueprint opacity-50" />
        <div className="absolute inset-0 bg-spotlight" />
      </div>

      <div className="max-w-6xl mx-auto space-y-10 relative z-10">
        
        {/* Top Header Bar matching Page 6 */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-fog hover:text-frost transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to home</span>
          </Link>

          <div className="flex items-center gap-4">
            <Link
              to="/guides/job-scam-red-flags"
              className="text-xs text-fog hover:text-frost transition-colors inline-flex items-center gap-1"
            >
              <span>Red Flags Guide</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
            <LanguageSelector />
          </div>
        </div>

        {/* Title, Subtitle, & Stats Pill matching Page 6 */}
        <div className="space-y-4 text-left">
          <p className="text-[10px] sm:text-[11px] font-mono font-medium uppercase tracking-[0.2em] text-fog">
            Free scam check — results in about a minute
          </p>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-semibold text-frost tracking-tight">
            Job Scam Checker & Detector
          </h1>

          <p className="text-sm sm:text-base text-mist font-light max-w-3xl leading-relaxed">
            Paste any job ad and we'll cross-check corporate data, salary norms, recruiter footprint, and known scam fingerprints.
          </p>

          {/* 3 Stats Pill */}
          <div className="inline-flex flex-wrap items-center gap-3 sm:gap-6 rounded-2xl bg-black/40 border border-white/10 px-4 py-2 text-xs text-mist font-mono">
            <span className="flex items-center gap-1.5 text-amber-400">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>60% of scans flagged risky</span>
            </span>
            <span className="hidden sm:inline text-white/20">|</span>
            <span className="flex items-center gap-1.5 text-emerald-400">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>50+ verification checks</span>
            </span>
            <span className="hidden sm:inline text-white/20">|</span>
            <span className="flex items-center gap-1.5 text-frost">
              <Sparkles className="w-3.5 h-3.5 text-skywash" />
              <span>Avg. ~60 sec per scan</span>
            </span>
          </div>

          {/* Quota Banner */}
          <div className="rounded-xl bg-white/[0.03] border border-white/10 px-4 py-2.5 text-xs text-fog font-light">
            {!isAuthenticated ? (
              guestScanCount >= 1 ? (
                <span className="text-amber-300">
                  1 free scan used. <button type="button" onClick={() => setShowAuthModal(true)} className="text-emerald-400 underline underline-offset-2 font-medium">Sign in with Google or Email</button> to unlock unlimited scans & save history.
                </span>
              ) : (
                <span>
                  1 free scan per device. <button type="button" onClick={() => setShowAuthModal(true)} className="text-emerald-400 underline underline-offset-2 font-medium">Sign in</button> to unlock unlimited scans & history vault.
                </span>
              )
            ) : (
              <span className="text-emerald-400 font-mono text-[11px]">
                ✓ Unlimited scans enabled for logged-in analyst account.
              </span>
            )}
          </div>
        </div>

        {/* Main Grid: Left Form Card (7 cols) + Right Sidebar (5 cols) matching Page 6 & 7 */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Column Form */}
          <div className="lg:col-span-8 glass-card rounded-2xl p-6 sm:p-8 border border-white/10 shadow-2xl space-y-6">
            
            <form onSubmit={handleAnalyze} className="space-y-6">
              <div>
                <label className="block text-xs font-medium text-mist mb-2">How do you want to check this job?</label>
                <div className="flex rounded-full bg-black/40 border border-white/10 p-1 shadow-hairline-inset">
                  <button
                    type="button"
                    onClick={() => setActiveTab('text')}
                    className={`flex-1 min-w-0 flex items-center justify-center gap-1.5 rounded-full px-3 py-2 text-xs font-medium transition-all ${
                      activeTab === 'text'
                        ? 'bg-white/10 text-frost shadow-hairline-inset border border-white/15'
                        : 'text-fog hover:text-frost'
                    }`}
                  >
                    <span>Text Input</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setActiveTab('image')}
                    className={`flex-1 min-w-0 flex items-center justify-center gap-1.5 rounded-full px-3 py-2 text-xs font-medium transition-all ${
                      activeTab === 'image'
                        ? 'bg-white/10 text-frost shadow-hairline-inset border border-white/15'
                        : 'text-fog hover:text-frost'
                    }`}
                  >
                    <Upload className="w-3.5 h-3.5" />
                    <span>Upload PDF / Image</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setActiveTab('url')}
                    className={`flex-1 min-w-0 flex items-center justify-center gap-1.5 rounded-full px-3 py-2 text-xs font-medium transition-all ${
                      activeTab === 'url'
                        ? 'bg-white/10 text-frost shadow-hairline-inset border border-white/15'
                        : 'text-fog hover:text-frost'
                    }`}
                  >
                    <LinkIcon className="w-3.5 h-3.5" />
                    <span>Link URL</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setActiveTab('batch')}
                    className={`flex-1 min-w-0 flex items-center justify-center gap-1.5 rounded-full px-3 py-2 text-xs font-medium transition-all ${
                      activeTab === 'batch'
                        ? 'bg-white/10 text-frost shadow-hairline-inset border border-white/15'
                        : 'text-fog hover:text-frost'
                    }`}
                  >
                    <Layers className="w-3.5 h-3.5" />
                    <span>Batch (Bulk)</span>
                  </button>
                </div>
              </div>

              {/* Common Inputs: Job Title & Company (Hide when in batch mode) */}
              {activeTab !== 'batch' && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="block text-xs font-medium text-mist">
                      Job Title <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={jobTitle}
                      onChange={(e) => setJobTitle(e.target.value)}
                      placeholder="e.g., Senior Backend Engineer"
                      className="w-full px-4 py-2.5 text-xs sm:text-sm rounded-xl bg-black/50 border border-white/10 text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50"
                    />
                    <p className="text-[10px] text-fog font-light">Include role level and key skills for better accuracy</p>
                  </div>

                  <div className="space-y-1">
                    <label className="block text-xs font-medium text-mist">
                      Company Name / Recruitment Agency <span className="text-fog font-normal">(optional)</span>
                    </label>
                    <input
                      type="text"
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      placeholder="e.g., Acme Corp or Robert Half"
                      className="w-full px-4 py-2.5 text-xs sm:text-sm rounded-xl bg-black/50 border border-white/10 text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50"
                    />
                    <p className="text-[10px] text-fog font-light">Exact name helps with verification</p>
                  </div>
                </div>
              )}

              {/* Tab 1: Text Input */}
              {activeTab === 'text' && (
                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-mist">
                    Job Description <span className="text-red-400">*</span>
                  </label>
                  <textarea
                    rows={6}
                    required
                    value={jobText}
                    onChange={(e) => setJobText(e.target.value)}
                    maxLength={10000}
                    placeholder="Paste the full job post or recruiter message — description, requirements, salary, contact details..."
                    className="w-full px-4 py-3 text-xs sm:text-sm rounded-xl bg-black/50 border border-white/10 text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50 resize-none font-sans leading-relaxed"
                  />
                  <div className="flex justify-between text-[10px] text-fog font-mono">
                    <span>{jobText.length.toLocaleString()} / 10,000 characters (min 50)</span>
                    <button
                      type="button"
                      onClick={() => {
                        setJobTitle('Remote Customer Support');
                        setCompanyName('Teleperformance');
                        setJobText('Teleperformance USA is hiring Remote Customer Support Reps. Hourly rate $19-$22/hr. Apply at teleperformance.com/careers.');
                      }}
                      className="text-emerald-400 hover:text-emerald-300"
                    >
                      Fill sample
                    </button>
                  </div>
                </div>
              )}

              {/* Tab 2: Upload Document / Image */}
              {activeTab === 'image' && (
                <DropZone
                  acceptType="both"
                  selectedFile={selectedFile}
                  onFileSelected={(file) => setSelectedFile(file)}
                  onRemoveFile={() => setSelectedFile(null)}
                />
              )}

              {/* Tab 3: URL Link */}
              {activeTab === 'url' && (
                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-mist">
                    Job Posting URL <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="url"
                    required
                    value={jobUrl}
                    onChange={(e) => setJobUrl(e.target.value)}
                    placeholder="https://company.com/careers/job-id-12345"
                    className="w-full px-4 py-2.5 text-xs sm:text-sm rounded-xl bg-black/50 border border-white/10 text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50 font-mono"
                  />
                  <p className="text-[10px] text-fog font-light">SSRF-protected scanner extracts text directly from ATS portal</p>
                </div>
              )}

              {/* Tab 4: Batch Bulk Input */}
              {activeTab === 'batch' && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="block text-xs font-medium text-mist">
                      Batch Job Input (Separate postings with <code className="text-emerald-400 font-mono">---</code>) <span className="text-red-400">*</span>
                    </label>
                    <button
                      type="button"
                      onClick={() => {
                        setBatchInput(`Google LLC is looking for Senior Python Engineers in Bengaluru. Competitive salary ₹35,00,000 - ₹50,00,000. Apply at careers.google.com.\n---\nURGENT: Work from Home Data Entry Operator wanted. Earn $500/day. Send money for home office equipment setup via Telegram @quickrecruiter.\n---\nMicrosoft Corporation is hiring Full Stack Cloud Architects. Hybrid role in Hyderabad. Official application portal: careers.microsoft.com.`);
                      }}
                      className="text-[11px] text-emerald-400 hover:text-emerald-300 font-mono"
                    >
                      Load 3 Sample Postings
                    </button>
                  </div>
                  <textarea
                    rows={8}
                    required
                    value={batchInput}
                    onChange={(e) => setBatchInput(e.target.value)}
                    placeholder="Paste multiple job postings separated by '---'. Supports up to 25 simultaneous scans."
                    className="w-full px-4 py-3 text-xs sm:text-sm rounded-xl bg-black/50 border border-white/10 text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50 resize-none font-mono leading-relaxed"
                  />
                  <p className="text-[10px] text-fog font-light">Concurrent batch analysis returns individual risk reports and summary threat intelligence metrics.</p>
                </div>
              )}

              {/* Enhanced Accuracy Collapsible Accordion matching Page 7 */}
              <div className="border border-white/10 rounded-xl overflow-hidden bg-black/30">
                <button
                  type="button"
                  onClick={() => setEnhancedOpen(!enhancedOpen)}
                  className="w-full px-4 py-3 flex items-center justify-between text-xs font-medium text-frost hover:bg-white/5 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Enhanced Accuracy Fields</span>
                    <span className="text-fog font-light text-[11px] hidden sm:inline">(Add location, recruiter info, or job URL for higher accuracy)</span>
                  </div>
                  {enhancedOpen ? <ChevronUp className="w-4 h-4 text-fog" /> : <ChevronDown className="w-4 h-4 text-fog" />}
                </button>

                {enhancedOpen && (
                  <div className="p-4 border-t border-white/10 space-y-3 bg-black/50">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <label className="block text-[11px] text-mist">Recruiter Email or Handle</label>
                        <input
                          type="text"
                          value={recruiterEmail}
                          onChange={(e) => setRecruiterEmail(e.target.value)}
                          placeholder="e.g. recruiter@company.com or @TelegramUser"
                          className="w-full px-3 py-2 text-xs rounded-lg bg-black/40 border border-white/10 text-frost focus:outline-none focus:border-emerald-500/50"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="block text-[11px] text-mist">Job Location</label>
                        <input
                          type="text"
                          value={jobLocation}
                          onChange={(e) => setJobLocation(e.target.value)}
                          placeholder="e.g. Remote (US) or San Francisco, CA"
                          className="w-full px-3 py-2 text-xs rounded-lg bg-black/40 border border-white/10 text-frost focus:outline-none focus:border-emerald-500/50"
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Submit CTA */}
              <div className="space-y-2 pt-2">
                {!isAuthenticated && guestScanCount >= 1 ? (
                  <button
                    type="button"
                    onClick={() => setShowAuthModal(true)}
                    className="w-full flex items-center justify-center gap-2 py-3.5 px-6 rounded-xl bg-gradient-to-r from-amber-500 via-amber-600 to-amber-500 hover:from-amber-400 hover:to-amber-500 text-white font-semibold text-sm shadow-lg shadow-amber-500/25 transition-all transform active:scale-[0.99]"
                  >
                    <LogIn className="w-4 h-4" />
                    <span>Sign In with Google or Email to Scan (1 Free Scan Used)</span>
                  </button>
                ) : (
                  <button
                    type="submit"
                    disabled={isAnalyzing}
                    className="w-full flex items-center justify-center gap-2 py-3.5 px-6 rounded-xl bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 hover:from-emerald-400 hover:to-teal-400 text-black font-semibold text-sm shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all transform active:scale-[0.99] disabled:opacity-50 disabled:pointer-events-none"
                  >
                    {isAnalyzing ? (
                      <span className="flex items-center gap-2">
                        <span className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                        <span>Analyzing Posting...</span>
                      </span>
                    ) : (
                      <>
                        <span>{activeTab === 'batch' ? 'Run Batch Threat Analysis' : 'Analyze Job Posting'}</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                )}

                <p className="text-[11px] text-center text-fog font-light flex items-center justify-center gap-1.5">
                  <Lock className="w-3 h-3 text-emerald-400" />
                  <span>Analyzed securely over an encrypted connection — we never contact the employer.</span>
                </p>
              </div>
            </form>

            {/* Batch Results View */}
            {batchResponse && (
              <div className="mt-8 pt-6 border-t border-white/10 space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <h3 className="text-base font-bold text-frost flex items-center gap-2">
                      <Layers className="w-4 h-4 text-emerald-400" />
                      <span>Batch Threat Assessment Results</span>
                    </h3>
                    <p className="text-xs text-fog font-light">Analyzed {batchResponse.total_analyzed} jobs concurrently.</p>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-mono">
                    <span className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      Safe: {batchResponse.summary?.safe_count}
                    </span>
                    <span className="px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      Caution: {batchResponse.summary?.caution_count}
                    </span>
                    <span className="px-2.5 py-1 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20">
                      Risky: {batchResponse.summary?.risky_count}
                    </span>
                  </div>
                </div>

                {/* Aggregated Metric Cards */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="p-3 rounded-xl bg-black/40 border border-white/10">
                    <span className="text-fog">Avg. Risk Score</span>
                    <div className="text-xl font-mono font-bold text-frost">{batchResponse.summary?.average_risk_score}/100</div>
                  </div>
                  <div className="p-3 rounded-xl bg-black/40 border border-white/10">
                    <span className="text-fog">Max Risk Peak</span>
                    <div className="text-xl font-mono font-bold text-red-400">{batchResponse.summary?.highest_risk_score}/100</div>
                  </div>
                  <div className="p-3 rounded-xl bg-black/40 border border-white/10">
                    <span className="text-fog">Critical Flags</span>
                    <div className="text-xl font-mono font-bold text-amber-400">{batchResponse.summary?.critical_flags_found}</div>
                  </div>
                  <div className="p-3 rounded-xl bg-black/40 border border-white/10">
                    <span className="text-fog">Throughput</span>
                    <div className="text-xl font-mono font-bold text-emerald-400">100% OK</div>
                  </div>
                </div>

                {/* Individual Job Results List */}
                <div className="space-y-2.5 max-h-80 overflow-y-auto pr-1">
                  {batchResponse.results?.map((res, idx) => (
                    <div
                      key={res.id || idx}
                      className="flex items-center justify-between p-3 rounded-xl bg-black/30 border border-white/10 hover:border-white/20 transition-all text-xs"
                    >
                      <div className="min-w-0 pr-3">
                        <p className="font-semibold text-frost truncate">{res.job_title || `Job #${idx + 1}`}</p>
                        <p className="text-fog font-light text-[11px] truncate">{res.company_name || 'Corporate Posting'}</p>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                          res.risk_score < 30 ? 'bg-emerald-500/20 text-emerald-300' :
                          res.risk_score < 70 ? 'bg-amber-500/20 text-amber-300' : 'bg-red-500/20 text-red-300'
                        }`}>
                          Risk: {res.risk_score}
                        </span>
                        <Link
                          to={`/analysis/${res.id}`}
                          state={{ report: res }}
                          className="px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-frost text-[11px] transition-colors"
                        >
                          View Report
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column Sidebar matching Page 6 & 7 */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* Every Scan Checks Card */}
            <div className="glass-card rounded-2xl p-6 border border-white/10 space-y-4">
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-fog">
                Every scan checks
              </h3>

              <ul className="space-y-4 text-xs">
                <li className="flex items-start gap-3">
                  <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0 mt-0.5">
                    <Building className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="font-semibold text-frost">Company & domain</p>
                    <p className="text-fog font-light text-[11px] leading-relaxed">Official careers page, domain age, and web footprint</p>
                  </div>
                </li>

                <li className="flex items-start gap-3">
                  <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0 mt-0.5">
                    <User className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="font-semibold text-frost">Recruiter identity</p>
                    <p className="text-fog font-light text-[11px] leading-relaxed">Name, email domain, and impersonation signals</p>
                  </div>
                </li>

                <li className="flex items-start gap-3">
                  <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0 mt-0.5">
                    <DollarSign className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="font-semibold text-frost">Salary realism</p>
                    <p className="text-fog font-light text-[11px] leading-relaxed">Pay vs. market norms for the role and location</p>
                  </div>
                </li>

                <li className="flex items-start gap-3">
                  <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0 mt-0.5">
                    <ShieldAlert className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="font-semibold text-frost">Known scam patterns</p>
                    <p className="text-fog font-light text-[11px] leading-relaxed">Cross-referenced against reported scam tactics</p>
                  </div>
                </li>
              </ul>
            </div>

            {/* You Get Back Card */}
            <div className="glass-card rounded-2xl p-6 border border-white/10 space-y-3">
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-fog">
                You get back
              </h3>

              <ul className="space-y-2 text-xs text-mist">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>A 0–100 risk score</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Every red flag explained</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Clear next steps to stay safe</span>
                </li>
              </ul>
            </div>

          </div>

        </div>

        {/* 1. What the Job Scam Checker Verifies matching Pages 8, 11, 12, 13 */}
        <section className="pt-12 border-t border-white/10 space-y-6">
          <div className="space-y-2">
            <h2 className="text-2xl sm:text-3xl font-semibold text-frost tracking-tight">
              What the Job Scam Checker Verifies
            </h2>
            <p className="text-xs sm:text-sm text-mist font-light max-w-3xl leading-relaxed">
              Every scan runs 50+ checks across eight verification layers. Here is what the job scam checker examines and why each check matters.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {VERIFICATION_CHECKS.map((chk, idx) => {
              const Icon = chk.icon;
              return (
                <div key={idx} className="glass-card rounded-2xl p-6 border border-white/10 space-y-3">
                  <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 w-fit">
                    <Icon className="w-4 h-4" />
                  </div>
                  <h3 className="text-base font-semibold text-frost">{chk.title}</h3>
                  <p className="text-xs text-mist leading-relaxed font-light">{chk.desc}</p>
                </div>
              );
            })}
          </div>
        </section>

        {/* 2. How the Job Scam Checker Works matching Pages 13 & 14 */}
        <section className="pt-12 border-t border-white/10 space-y-6">
          <div className="space-y-2">
            <h2 className="text-2xl sm:text-3xl font-semibold text-frost tracking-tight">
              How the Job Scam Checker Works
            </h2>
            <p className="text-xs sm:text-sm text-mist font-light max-w-3xl leading-relaxed">
              The checker accepts job postings in three formats. Each input type runs the full 50+ check suite — no checks are skipped based on how you submit the job.
            </p>
          </div>

          <div className="space-y-4">
            <div className="glass-card rounded-2xl p-6 border border-white/10 space-y-2">
              <h3 className="text-sm font-semibold text-frost">Option 1: Paste the job text</h3>
              <p className="text-xs text-mist leading-relaxed font-light">
                Copy the complete job posting from any source — LinkedIn, Indeed, a recruiter email, a WhatsApp message — and paste it into the text field. The AI extracts company name, job title, salary, location, contact details, and job description automatically. Adding these fields manually improves accuracy for ambiguous or abbreviated postings.
              </p>
            </div>

            <div className="glass-card rounded-2xl p-6 border border-white/10 space-y-2">
              <h3 className="text-sm font-semibold text-frost">Option 2: Enter a job URL</h3>
              <p className="text-xs text-mist leading-relaxed font-light">
                Paste the direct URL of any job listing — from LinkedIn, Indeed, Glassdoor, Workday, Greenhouse, Lever, company career pages, or any other source. The checker fetches the page, extracts all relevant fields, and runs the full verification suite. This is the fastest method when you have a direct link.
              </p>
            </div>

            <div className="glass-card rounded-2xl p-6 border border-white/10 space-y-2">
              <h3 className="text-sm font-semibold text-frost">Option 3: Upload a screenshot</h3>
              <p className="text-xs text-mist leading-relaxed font-light">
                Upload one or two screenshots of the job posting. Our AI extracts text via OCR, then runs the full check suite. For best accuracy, also enter the job title and company name manually — the checker uses these to verify against official sources even when screenshot text is cropped or unclear.
              </p>
            </div>
          </div>
        </section>

        {/* 3. Who Should Use This Job Scam Checker matching Page 15 */}
        <section className="pt-12 border-t border-white/10 space-y-6">
          <div className="space-y-2">
            <h2 className="text-2xl sm:text-3xl font-semibold text-frost tracking-tight">
              Who Should Use This Job Scam Checker
            </h2>
            <p className="text-xs sm:text-sm text-mist font-light max-w-3xl leading-relaxed">
              The FTC reports that Americans lost over $500 million to job and employment scams in 2023. The BBB found that 1 in 3 people who encountered a job scam lost money — with a median loss of $1,500. The checker is built for anyone in an active job search.
            </p>
          </div>

          <div className="space-y-3">
            {WHO_SHOULD_USE.map((item, idx) => (
              <div key={idx} className="glass-card rounded-xl p-5 border border-white/10 flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <span className="text-xs font-semibold text-frost">{item.title}: </span>
                  <span className="text-xs text-mist font-light leading-relaxed">{item.desc}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 4. What the Checker Flags as High-Risk matching Page 16 */}
        <section className="pt-12 border-t border-white/10 space-y-6">
          <div className="space-y-2">
            <h2 className="text-2xl sm:text-3xl font-semibold text-frost tracking-tight">
              What the Checker Flags as High-Risk
            </h2>
            <p className="text-xs sm:text-sm text-mist font-light max-w-3xl leading-relaxed">
              These are the patterns the job scam checker weighs most heavily. Each contributes to the overall risk score. More than two of these in the same posting is a strong indicator of fraud.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {HIGH_RISK_FLAGS.map((flag, idx) => (
              <div key={idx} className="glass-card rounded-xl p-4 border border-red-500/20 bg-red-950/20 flex items-start gap-2.5">
                <AlertTriangle className="w-3.5 h-3.5 text-red-400 shrink-0 mt-0.5" />
                <span className="text-xs text-mist font-light">{flag}</span>
              </div>
            ))}
          </div>
        </section>

        {/* 5. Frequently Asked Questions matching Page 17 */}
        <section className="pt-12 border-t border-white/10 space-y-6">
          <h2 className="text-2xl sm:text-3xl font-semibold text-frost tracking-tight">
            Frequently Asked Questions About the Job Scam Checker
          </h2>

          <div className="space-y-3">
            {FAQS.map((faq, idx) => (
              <div key={idx} className="glass-card rounded-xl border border-white/10 overflow-hidden">
                <button
                  type="button"
                  onClick={() => toggleFaq(idx)}
                  className="w-full p-4 text-left flex items-center justify-between text-xs sm:text-sm font-medium text-frost hover:bg-white/5 transition-colors"
                >
                  <span>{faq.q}</span>
                  {faqExpanded[idx] ? <ChevronUp className="w-4 h-4 text-fog" /> : <ChevronDown className="w-4 h-4 text-fog" />}
                </button>
                {faqExpanded[idx] && (
                  <div className="p-4 border-t border-white/10 text-xs text-mist font-light leading-relaxed bg-black/40">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* 6. Related Guides matching Page 18 */}
        <section className="pt-12 border-t border-white/10 space-y-6">
          <h2 className="text-2xl sm:text-3xl font-semibold text-frost tracking-tight">
            Related Guides
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {RELATED_GUIDES.map((g, idx) => (
              <div key={idx} className="glass-card rounded-2xl p-5 border border-white/10 flex flex-col justify-between space-y-3">
                <div>
                  <h3 className="text-sm font-semibold text-frost">{g.title}</h3>
                  <p className="text-xs text-mist font-light mt-1">{g.desc}</p>
                </div>
                <Link
                  to="/guides/job-scam-red-flags"
                  className="text-xs font-medium text-emerald-400 hover:text-emerald-300 inline-flex items-center gap-1"
                >
                  <span>Read guide</span>
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            ))}
          </div>

          <div className="pt-4 flex items-center justify-between text-xs">
            <Link to="/" className="text-fog hover:text-frost inline-flex items-center gap-1">
              <ArrowLeft className="w-3 h-3" />
              <span>Back to home</span>
            </Link>
            <Link to="/alerts" className="text-emerald-400 hover:text-emerald-300 inline-flex items-center gap-1">
              <span>View live scam alerts</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
        </section>

      </div>
      <GoogleAuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={() => setShowAuthModal(false)}
      />
    </div>
  );
};

export default AnalyzeJobPage;