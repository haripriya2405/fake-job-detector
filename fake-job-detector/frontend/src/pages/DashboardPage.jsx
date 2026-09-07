import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  CheckCircle2,
  Sparkles,
  BarChart3,
  AlertTriangle,
  Info,
  Clock,
  Globe,
  Users,
  MapPin,
  Calendar,
  ExternalLink,
  ShieldCheck,
  ShieldAlert,
  TrendingUp,
  Lock,
  Shield,
  Trash2,
  X,
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { analysisService } from '../services/analysisService';
import { Modal } from '../components/ui/Modal';

// Threat intelligence advisory data matching screenshots 2, 3, 4
const WORLDWIDE_SCAMS = [
  {
    id: 'scam-1',
    title: 'call operator',
    company: 'Azad digital media',
    community: true,
    tag: 'PAYMENT SCAM',
    tagColor: 'bg-red-500/10 text-red-400 border-red-500/30',
    location: 'https://maps.app.goo.gl/ks7dQ6u6MABTMEEB8',
    date: 'Jun 30, 2026',
    description: 'Fake VoIP softphone procurement scheme. The victim is hired as a remote operator and instructed to deposit a company-provided fraudulent check to buy softphone software from a designated vendor. Check bounces 48 hours later.',
    riskScore: 92,
  },
  {
    id: 'scam-2',
    title: 'Bespoke Technologies Inc scam',
    company: 'Bespoke Technologies Inc',
    community: true,
    tag: 'IMPERSONATION',
    tagColor: 'bg-red-500/10 text-red-400 border-red-500/30',
    location: 'Varies',
    date: 'Mar 1, 2026',
    description: 'Fraudulent entity spoofing Bespoke Technologies domain with subtle lookalike typography. Conducts automated Microsoft Teams questionnaires and requests bank routing details during interview.',
    riskScore: 88,
  },
  {
    id: 'scam-3',
    title: 'Delivery Operations Specialist',
    company: 'Fake logistics / reshipping scam',
    tag: 'RESHIPPING',
    tagColor: 'bg-red-500/10 text-red-400 border-red-500/30',
    location: 'Remote (US)',
    date: 'Dec 2025',
    description: 'Package mule operation. Candidates are sent high-value electronics purchased with stolen cards, given prepaid shipping labels, and asked to re-pack and ship abroad. Victim is left legally liable.',
    riskScore: 95,
  },
  {
    id: 'scam-4',
    title: 'Quality Control Manager – Work From Home',
    company: 'Scammers impersonating major retailers',
    tag: 'RESHIPPING',
    tagColor: 'bg-red-500/10 text-red-400 border-red-500/30',
    location: 'Remote (Worldwide)',
    date: 'Dec 2025',
    description: 'Scammers impersonating Walmart and Target logistics departments offering $35/hour work-from-home quality inspection. Instructs candidates to process packages received at residential address.',
    riskScore: 94,
  },
  {
    id: 'scam-5',
    title: 'Remote Data Entry / Task-Based Pay',
    company: 'Unsolicited WhatsApp/Telegram job offers',
    tag: 'TASK SCAM',
    tagColor: 'bg-red-500/10 text-red-400 border-red-500/30',
    location: 'Remote',
    date: 'Nov 2025',
    highlight: true,
    description: 'Classic multi-level task scam. Promises $300-$800 daily for liking YouTube videos, clicking product booster buttons, or app ratings. Requires recurring USDT / crypto deposits to unlock higher reward tiers.',
    riskScore: 98,
  },
  {
    id: 'scam-6',
    title: 'HR Recruiter – "Instant offer" via personal email',
    company: 'Fake recruiter (Gmail/Yahoo, not corporate)',
    tag: 'FAKE RECRUITER',
    tagColor: 'bg-red-500/10 text-red-400 border-red-500/30',
    location: 'Remote (US)',
    date: 'Jul 2025',
    description: 'Unsolicited offer letters delivered from free webmail accounts (e.g. recruiter.hr2025@gmail.com) promising executive salary without any technical interview, followed by onboarding form requesting sensitive SSN and banking routing.',
    riskScore: 90,
  },
  {
    id: 'scam-7',
    title: 'Operations Coordinator – Repackage & ship',
    company: 'Package mule / reshipping scheme',
    tag: 'RESHIPPING',
    tagColor: 'bg-red-500/10 text-red-400 border-red-500/30',
    location: 'Remote',
    date: 'Nov 2025',
    description: 'Listings on job portals for "Regional Supply Chain Assistant". Involves receiving goods at personal home address and rerouting packages to international freight forwarders.',
    riskScore: 93,
  },
  {
    id: 'scam-8',
    title: 'Boss imposter after new job announced',
    company: 'Social media–based impersonation',
    tag: 'IMPERSONATION',
    tagColor: 'bg-red-500/10 text-red-400 border-red-500/30',
    location: 'Varies',
    date: '2025',
    description: 'Targeted spear phishing targeting newly hired employees on LinkedIn. Fraudster impersonates the CEO or VP over SMS/WhatsApp requesting immediate purchase of gift cards for an emergency executive client presentation.',
    riskScore: 91,
  },
];

export const DashboardPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedScam, setSelectedScam] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const history = await analysisService.getHistory();
        setAnalyses(Array.isArray(history) ? history : []);
      } catch (err) {
        console.error('Failed to load dashboard scans', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const displayName =
    user?.full_name || user?.username || (user?.email ? user.email.split('@')[0] : 'denvermh64');

  // Stats calculation
  const totalScans = analyses.length > 0 ? analyses.length : 1;
  const highRiskCount = analyses.filter(
    (a) => a.risk_score >= 60 || a.risk_level === 'high' || a.risk_level === 'critical'
  ).length;
  const mediumRiskCount = analyses.filter(
    (a) => (a.risk_score >= 35 && a.risk_score < 60) || a.risk_level === 'medium'
  ).length;
  const lowRiskCount = analyses.length > 0
    ? analyses.filter((a) => a.risk_score < 35 || a.risk_level === 'low').length
    : 1;

  const trustedCount = lowRiskCount;

  // Percentage distribution
  const safePercent = Math.round((lowRiskCount / totalScans) * 100);
  const cautionPercent = Math.round((mediumRiskCount / totalScans) * 100);
  const riskyPercent = Math.round((highRiskCount / totalScans) * 100);

  // Recent scans
  const recentScans = useMemo(() => {
    if (analyses.length > 0) {
      return analyses.slice(0, 3).map((item) => {
        const score = Math.max(0, 100 - (item.risk_score || 0));
        const isSafe = (item.risk_score || 0) < 35;
        const isCaution = (item.risk_score || 0) >= 35 && (item.risk_score || 0) < 60;
        return {
          id: item.id,
          job_title: item.job_title || 'Analyzed Job Posting',
          company_name: item.company_name || 'Verified Employer',
          score,
          isSafe,
          risk_label: isSafe ? 'Safe' : isCaution ? 'Caution' : 'Risky',
          timeAgo: 'Just now',
        };
      });
    }

    // Default sample matching Screenshot 2
    return [
      {
        id: 'sample-1',
        job_title: 'Front-End Developer Intern',
        company_name: 'Code Nimbus Solutions',
        score: 100,
        isSafe: true,
        risk_label: 'Safe',
        timeAgo: '2d ago',
      },
    ];
  }, [analyses]);

  return (
    <div className="space-y-8 select-none pb-12">
      
      {/* 1. Top Scan Teaser Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 p-6 rounded-2xl bg-[#09100d] border border-white/10 shadow-xl relative overflow-hidden">
        <div className="space-y-2 max-w-2xl">
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Scan a new job in seconds
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 font-light leading-relaxed">
            Paste a posting, link, or recruiter message — we cross-check the company, recruiter, salary, and known scam patterns automatically.
          </p>
          <div className="flex flex-wrap items-center gap-4 pt-1 text-xs text-emerald-400 font-medium">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              50+ verification checks
            </span>
            <span className="text-slate-600">·</span>
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              AI + open-source intelligence
            </span>
          </div>
        </div>

        <button
          onClick={() => navigate('/scan')}
          className="px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm flex items-center gap-2 shadow-[0_0_25px_rgba(16,185,129,0.3)] transition-all hover:scale-[1.02] shrink-0"
        >
          <Search className="w-4 h-4" />
          <span>Start a scan →</span>
        </button>
      </div>

      {/* 2. Welcome Back & Risk Distribution Row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Welcome Back Card */}
        <div className="lg:col-span-7 p-6 rounded-2xl bg-[#09100d]/90 border border-white/10 flex flex-col justify-between space-y-6 shadow-xl">
          <div className="space-y-2">
            <div className="text-[10px] font-mono tracking-widest text-slate-400 uppercase font-bold">
              WELCOME BACK
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white leading-tight">
              Hi {displayName}, let's <span className="text-emerald-400">protect your</span>
              <br />
              <span className="text-emerald-400">job search</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 max-w-lg font-light leading-relaxed">
              Monitor new submissions, flag suspicious postings, and keep yourself protected with real-time intelligence.
            </p>
          </div>

          {/* 3 Metric Cards */}
          <div className="grid grid-cols-3 gap-3 pt-2">
            {/* Total Scans */}
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex flex-col justify-between space-y-3">
              <div className="flex items-center justify-between text-emerald-400">
                <BarChart3 className="w-4 h-4" />
                <Info className="w-3.5 h-3.5 text-slate-600 hover:text-slate-400 cursor-pointer" />
              </div>
              <div>
                <p className="text-2xl sm:text-3xl font-bold text-white font-sans">{totalScans}</p>
                <p className="text-xs text-slate-400 mt-0.5">Total scans</p>
              </div>
            </div>

            {/* High-risk Flagged */}
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex flex-col justify-between space-y-3">
              <div className="flex items-center justify-between text-red-400">
                <AlertTriangle className="w-4 h-4" />
                <Info className="w-3.5 h-3.5 text-slate-600 hover:text-slate-400 cursor-pointer" />
              </div>
              <div>
                <p className="text-2xl sm:text-3xl font-bold text-white font-sans">{highRiskCount}</p>
                <p className="text-xs text-slate-400 mt-0.5">High-risk flagged</p>
              </div>
            </div>

            {/* Trusted Jobs */}
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex flex-col justify-between space-y-3">
              <div className="flex items-center justify-between text-emerald-400">
                <CheckCircle2 className="w-4 h-4" />
                <Info className="w-3.5 h-3.5 text-slate-600 hover:text-slate-400 cursor-pointer" />
              </div>
              <div>
                <p className="text-2xl sm:text-3xl font-bold text-white font-sans">{trustedCount}</p>
                <p className="text-xs text-slate-400 mt-0.5">Trusted jobs</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Risk Distribution Card */}
        <div className="lg:col-span-5 p-6 rounded-2xl bg-[#09100d]/90 border border-white/10 flex flex-col justify-between space-y-6 shadow-xl">
          <div>
            <div className="text-[10px] font-mono tracking-widest text-slate-400 uppercase font-bold">
              RISK DISTRIBUTION
            </div>
            <h2 className="text-xl font-bold text-white mt-1">Your scan results</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Based on {totalScans} scan{totalScans !== 1 ? 's' : ''}
            </p>
          </div>

          <div className="space-y-4">
            {/* Safe progress bar */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-emerald-400">Safe</span>
                <span className="text-slate-300 font-mono">{lowRiskCount} ({safePercent}%)</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-800/90 overflow-hidden">
                <div
                  className="h-full bg-emerald-400 rounded-full transition-all duration-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"
                  style={{ width: `${safePercent}%` }}
                />
              </div>
            </div>

            {/* Caution progress bar */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-amber-400">Caution</span>
                <span className="text-slate-300 font-mono">{mediumRiskCount} ({cautionPercent}%)</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-800/90 overflow-hidden">
                <div
                  className="h-full bg-amber-400 rounded-full transition-all duration-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]"
                  style={{ width: `${cautionPercent}%` }}
                />
              </div>
            </div>

            {/* Risky progress bar */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-red-400">Risky</span>
                <span className="text-slate-300 font-mono">{highRiskCount} ({riskyPercent}%)</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-800/90 overflow-hidden">
                <div
                  className="h-full bg-red-400 rounded-full transition-all duration-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]"
                  style={{ width: `${riskyPercent}%` }}
                />
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* 3. Recent Scans Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-white">Recent scans</h3>
            <p className="text-xs text-slate-400">Your latest job analyses</p>
          </div>
          <button
            onClick={() => navigate('/history')}
            className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1 transition-colors"
          >
            <span>View all</span>
            <span>→</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recentScans.map((scan) => (
            <div
              key={scan.id}
              onClick={() => {
                if (scan.id !== 'sample-1') {
                  navigate(`/analysis/${scan.id}`);
                } else {
                  navigate('/scan');
                }
              }}
              className="p-5 rounded-2xl bg-[#0c120f]/90 border border-white/10 hover:border-emerald-500/40 transition-all cursor-pointer space-y-4 group shadow-lg"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h4 className="text-sm font-bold text-white group-hover:text-emerald-300 transition-colors truncate">
                    {scan.job_title}
                  </h4>
                  <p className="text-xs text-slate-400 truncate mt-0.5">
                    {scan.company_name}
                  </p>
                </div>
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                  scan.isSafe
                    ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400'
                    : 'bg-red-500/10 border border-red-500/30 text-red-400'
                }`}>
                  {scan.isSafe ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-red-400" />
                  )}
                </div>
              </div>

              <div className="flex items-end justify-between pt-3 border-t border-white/5">
                <div>
                  <p className="text-2xl font-extrabold text-white leading-none font-sans">
                    {scan.score}
                  </p>
                  <p className="text-[10px] text-slate-500 uppercase tracking-wider mt-1 font-mono">
                    Score
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${
                    scan.isSafe
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : 'bg-red-500/10 text-red-400 border-red-500/30'
                  }`}>
                    {scan.risk_label}
                  </span>
                  <span className="text-[11px] text-slate-500 flex items-center gap-1 font-mono">
                    <Clock className="w-3 h-3" />
                    {scan.timeAgo}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 4. Recent Scam Jobs Worldwide */}
      <div className="space-y-4 pt-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-red-500/15 border border-red-500/30 flex items-center justify-center text-red-400 shadow-[0_0_15px_rgba(239,68,68,0.2)]">
              <Globe className="w-5 h-5 text-red-400" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white tracking-tight">Recent Scam Jobs Worldwide</h3>
              <p className="text-xs text-slate-400">Real-time alerts from our global intelligence network</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/report-scam')}
              className="px-3.5 py-1.5 rounded-lg bg-emerald-950/40 hover:bg-emerald-900/50 border border-emerald-500/40 text-emerald-300 text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm"
            >
              <AlertTriangle className="w-3.5 h-3.5 text-emerald-400" />
              <span>Report a scam</span>
            </button>
            <button
              onClick={() => navigate('/alerts')}
              className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1 transition-colors"
            >
              <span>View all alerts</span>
              <ExternalLink className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* 3-column Grid of Scam Alert Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {WORLDWIDE_SCAMS.map((item, idx) => (
            <div
              key={idx}
              onClick={() => setSelectedScam(item)}
              className={`p-5 rounded-2xl bg-[#0b100d]/90 border transition-all cursor-pointer flex flex-col justify-between space-y-4 hover:scale-[1.01] ${
                item.highlight
                  ? 'border-red-500/50 shadow-[0_0_20px_rgba(239,68,68,0.15)] bg-red-950/10'
                  : 'border-white/10 hover:border-white/20'
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="w-6 h-6 rounded-md bg-red-500/15 border border-red-500/30 flex items-center justify-center text-red-400">
                    <AlertTriangle className="w-3.5 h-3.5" />
                  </div>
                  <div className="flex items-center gap-1.5 flex-wrap justify-end">
                    {item.community && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-blue-500/15 text-blue-400 border border-blue-500/30 flex items-center gap-1">
                        <Users className="w-2.5 h-2.5" />
                        COMMUNITY
                      </span>
                    )}
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${item.tagColor}`}>
                      {item.tag}
                    </span>
                  </div>
                </div>

                <div>
                  <h4 className={`text-sm font-bold leading-snug ${item.highlight ? 'text-red-400' : 'text-white'}`}>
                    {item.title}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1">{item.company}</p>
                </div>
              </div>

              <div className="pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                <span className="flex items-center gap-1 truncate max-w-[140px]" title={item.location}>
                  <MapPin className="w-3 h-3 text-emerald-400 shrink-0" />
                  <span className="truncate">{item.location}</span>
                </span>
                <span className="flex items-center gap-1 shrink-0">
                  <Calendar className="w-3 h-3 shrink-0" />
                  {item.date}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 5. Global Stats Strip */}
      <div className="rounded-2xl bg-white/[0.02] border border-white/10 p-4 flex flex-wrap items-center justify-around gap-4 text-xs font-mono text-slate-300 shadow-inner">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span className="font-bold text-white">985</span> jobs analyzed
        </div>
        <div className="hidden sm:block text-slate-700">|</div>
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-emerald-400" />
          <span className="font-bold text-white">601</span> flagged as high-risk
        </div>
        <div className="hidden sm:block text-slate-700">|</div>
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          <span className="font-bold text-white">61%</span> of all scans were risky
        </div>
      </div>

      {/* 6. Security Assurance Badges Footer */}
      <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
        <div className="px-4 py-1.5 rounded-full bg-emerald-950/40 border border-emerald-500/20 text-emerald-400 text-xs font-medium flex items-center gap-1.5">
          <Lock className="w-3.5 h-3.5" />
          <span>Encrypted in transit</span>
        </div>
        <div className="px-4 py-1.5 rounded-full bg-emerald-950/40 border border-emerald-500/20 text-emerald-400 text-xs font-medium flex items-center gap-1.5">
          <Shield className="w-3.5 h-3.5" />
          <span>Never sold or shared</span>
        </div>
        <div className="px-4 py-1.5 rounded-full bg-emerald-950/40 border border-emerald-500/20 text-emerald-400 text-xs font-medium flex items-center gap-1.5">
          <Trash2 className="w-3.5 h-3.5" />
          <span>Delete anytime</span>
        </div>
      </div>

      {/* Scam Detail Modal */}
      {selectedScam && (
        <Modal
          isOpen={!!selectedScam}
          onClose={() => setSelectedScam(null)}
          title={selectedScam.title}
        >
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold uppercase border ${selectedScam.tagColor}`}>
                {selectedScam.tag}
              </span>
              <span className="text-xs text-slate-400 font-mono">• {selectedScam.company}</span>
            </div>

            <div className="p-4 rounded-xl bg-black/60 border border-white/10 text-xs text-slate-300 leading-relaxed space-y-2">
              <p className="font-semibold text-white">Intelligence Profile & Modus Operandi:</p>
              <p>{selectedScam.description}</p>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-400 font-mono pt-2 border-t border-white/10">
              <span>Reported: {selectedScam.date}</span>
              <span>Threat Score: <strong className="text-red-400">{selectedScam.riskScore}/100</strong></span>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => {
                  setSelectedScam(null);
                  navigate('/scan');
                }}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-950 bg-emerald-400 hover:bg-emerald-300 transition-all shadow-md font-sans"
              >
                Scan a Job Against This Pattern →
              </button>
            </div>
          </div>
        </Modal>
      )}

    </div>
  );
};

export default DashboardPage;
