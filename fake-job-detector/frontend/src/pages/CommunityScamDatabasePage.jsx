import React, { useState, useEffect, useCallback } from 'react';
import { 
  ShieldAlert, 
  Search, 
  Filter, 
  ThumbsUp, 
  AlertTriangle, 
  ExternalLink, 
  CheckCircle2, 
  Clock, 
  Building2, 
  Lock, 
  ArrowUpDown, 
  Eye, 
  X, 
  Sparkles,
  ChevronLeft,
  ChevronRight,
  Info,
  ShieldCheck,
  TrendingUp
} from 'lucide-react';
import { communityService } from '../services/communityService';
import { useToast } from '../context/ToastContext';

const SCAM_CATEGORIES = [
  { id: 'ALL', label: 'All Threats', icon: ShieldAlert },
  { id: 'CHECK_FRAUD', label: 'Fake Cashier Checks', icon: AlertTriangle },
  { id: 'TELEGRAM_INTERVIEW', label: 'Telegram Recruiter Lures', icon: Lock },
  { id: 'CRYPTO_TASK', label: 'Crypto Task Recharges', icon: TrendingUp },
  { id: 'UPFRONT_FEE', label: 'Upfront Onboarding Fees', icon: Building2 },
  { id: 'DATA_HARVESTING', label: 'Identity / SSN Phishing', icon: ShieldCheck },
];

export function CommunityScamDatabasePage() {
  const { addToast } = useToast();
  
  const [scams, setScams] = useState([]);
  const [stats, setStats] = useState({ total_threats: 5, avg_risk_score: 93.4, total_community_confirmations: 283 });
  const [loading, setLoading] = useState(true);
  
  const [query, setQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [sortBy, setSortBy] = useState('newest');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  // Detail Modal State
  const [selectedScam, setSelectedScam] = useState(null);
  const [confirmingId, setConfirmingId] = useState(null);

  const fetchScams = useCallback(async () => {
    try {
      setLoading(true);
      const data = await communityService.getScams({
        query: query.trim() || undefined,
        category: selectedCategory !== 'ALL' ? selectedCategory : undefined,
        sort_by: sortBy,
        page,
        page_size: 9,
      });

      setScams(data.items || []);
      setTotalPages(data.total_pages || 1);
      setTotalCount(data.total || 0);
      if (data.stats) {
        setStats(data.stats);
      }
    } catch (err) {
      addToast(err.message || 'Failed to fetch community threat database', 'error');
    } finally {
      setLoading(false);
    }
  }, [query, selectedCategory, sortBy, page, addToast]);

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      fetchScams();
    }, 250);
    return () => clearTimeout(debounceTimer);
  }, [fetchScams]);

  const handleConfirm = async (e, scamId) => {
    e.stopPropagation();
    try {
      setConfirmingId(scamId);
      const res = await communityService.confirmThreat(scamId);
      
      // Update locally
      setScams((prev) =>
        prev.map((s) =>
          s.public_id === scamId || s.id === scamId
            ? { ...s, community_confirmations: res.community_confirmations }
            : s
        )
      );

      if (selectedScam && (selectedScam.public_id === scamId || selectedScam.id === scamId)) {
        setSelectedScam((prev) => ({
          ...prev,
          community_confirmations: res.community_confirmations,
        }));
      }

      addToast('Thank you! Your confirmation helps protect the job seeker community.', 'success');
    } catch (err) {
      addToast(err.message || 'Could not confirm threat', 'error');
    } finally {
      setConfirmingId(null);
    }
  };

  const getCategoryBadgeClass = (cat) => {
    switch (cat) {
      case 'CHECK_FRAUD':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      case 'TELEGRAM_INTERVIEW':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
      case 'CRYPTO_TASK':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
      case 'UPFRONT_FEE':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      case 'DATA_HARVESTING':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      default:
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header Title Section */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/40 p-8 border border-slate-800 shadow-2xl">
          <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-semibold mb-3 tracking-wide uppercase">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                Live Threat Intelligence Feed
              </div>
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white flex items-center gap-3">
                <ShieldAlert className="w-10 h-10 text-red-400" />
                JobScam Community Database
              </h1>
              <p className="mt-2 text-slate-400 text-base max-w-2xl">
                Search verified job scams, impersonation domains, and deceptive recruitment tactics 
                reported and confirmed across the JobScamScore global threat network.
              </p>
            </div>

            {/* Live Stats */}
            <div className="grid grid-cols-3 gap-3 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 backdrop-blur-md">
              <div className="text-center px-2">
                <div className="text-2xl font-bold text-white tracking-tight">{stats.total_threats}</div>
                <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider mt-0.5">Known Threats</div>
              </div>
              <div className="text-center px-2 border-x border-slate-800">
                <div className="text-2xl font-bold text-red-400 tracking-tight">{stats.avg_risk_score}</div>
                <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider mt-0.5">Avg Risk</div>
              </div>
              <div className="text-center px-2">
                <div className="text-2xl font-bold text-cyan-400 tracking-tight">{stats.total_community_confirmations}</div>
                <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider mt-0.5">Confirmed</div>
              </div>
            </div>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="bg-slate-900/80 rounded-xl p-4 border border-slate-800 shadow-lg space-y-4">
          <div className="flex flex-col sm:flex-row gap-3">
            {/* Keyword Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  setPage(1);
                }}
                placeholder="Search by company name, impersonator domain, telegram handle, or scam keyword..."
                className="w-full pl-10 pr-4 py-2.5 bg-slate-950/70 border border-slate-700/60 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500 transition-all"
              />
              {query && (
                <button
                  onClick={() => setQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* Sort Dropdown */}
            <div className="flex items-center gap-2">
              <ArrowUpDown className="w-4 h-4 text-slate-400 shrink-0" />
              <select
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value);
                  setPage(1);
                }}
                className="bg-slate-950/70 border border-slate-700/60 rounded-lg px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500"
              >
                <option value="newest">Newest First</option>
                <option value="highest_risk">Highest Risk Score</option>
                <option value="most_confirmed">Most Community Confirmed</option>
              </select>
            </div>
          </div>

          {/* Category Filter Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-thin">
            {SCAM_CATEGORIES.map((cat) => {
              const Icon = cat.icon;
              const isSelected = selectedCategory === cat.id;
              return (
                <button
                  key={cat.id}
                  onClick={() => {
                    setSelectedCategory(cat.id);
                    setPage(1);
                  }}
                  className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap border ${
                    isSelected
                      ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-sm shadow-cyan-500/10'
                      : 'bg-slate-950/40 text-slate-400 border-slate-800 hover:text-slate-200 hover:border-slate-700'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {cat.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Threat Grid Section */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((idx) => (
              <div key={idx} className="bg-slate-900/50 rounded-xl p-6 border border-slate-800 animate-pulse space-y-4">
                <div className="flex justify-between items-center">
                  <div className="w-24 h-4 bg-slate-800 rounded" />
                  <div className="w-16 h-6 bg-slate-800 rounded-full" />
                </div>
                <div className="w-3/4 h-6 bg-slate-800 rounded" />
                <div className="w-1/2 h-4 bg-slate-800 rounded" />
                <div className="space-y-2 pt-2">
                  <div className="w-full h-3 bg-slate-800 rounded" />
                  <div className="w-5/6 h-3 bg-slate-800 rounded" />
                </div>
              </div>
            ))}
          </div>
        ) : scams.length === 0 ? (
          <div className="text-center py-16 bg-slate-900/40 rounded-2xl border border-slate-800/80 p-8">
            <ShieldCheck className="w-16 h-16 text-emerald-400/80 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white">No Scam Threats Matched Your Filter</h3>
            <p className="text-slate-400 text-sm max-w-md mx-auto mt-2">
              Try adjusting your search terms or selecting 'All Threats' to explore the active community threat registry.
            </p>
            <button
              onClick={() => {
                setQuery('');
                setSelectedCategory('ALL');
              }}
              className="mt-5 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm font-semibold transition-all shadow-md"
            >
              Reset Filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {scams.map((scam) => (
              <div
                key={scam.id || scam.public_id}
                onClick={() => setSelectedScam(scam)}
                className="group relative bg-slate-900/70 hover:bg-slate-900/95 border border-slate-800 hover:border-cyan-500/40 rounded-xl p-5 shadow-lg transition-all duration-200 cursor-pointer flex flex-col justify-between"
              >
                {/* Card Top Meta */}
                <div>
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <span className="font-mono text-xs font-bold text-cyan-400 tracking-wider bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/50">
                      {scam.public_id}
                    </span>
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
                      <AlertTriangle className="w-3 h-3" />
                      Score {scam.risk_score}
                    </span>
                  </div>

                  {/* Title & Impostor Entity */}
                  <h3 className="text-lg font-bold text-white group-hover:text-cyan-300 transition-colors line-clamp-1">
                    {scam.job_title}
                  </h3>
                  <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-1">
                    <Building2 className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    <span className="truncate font-medium text-slate-300">{scam.impostor_company}</span>
                  </div>

                  {/* Category Pill */}
                  <div className="mt-3">
                    <span className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getCategoryBadgeClass(scam.scam_category)}`}>
                      {scam.scam_category.replace(/_/g, ' ')}
                    </span>
                  </div>

                  {/* Snippet */}
                  <p className="mt-3 text-xs text-slate-400 line-clamp-3 leading-relaxed bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/60 font-sans">
                    "{scam.description_snippet}"
                  </p>

                  {/* Red Flags Preview */}
                  {scam.red_flags && scam.red_flags.length > 0 && (
                    <div className="mt-3 space-y-1">
                      <div className="text-[11px] font-semibold text-rose-400 flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" />
                        Key Red Flag:
                      </div>
                      <p className="text-[11px] text-slate-300 line-clamp-1 pl-4 border-l-2 border-rose-500/50">
                        {scam.red_flags[0]}
                      </p>
                    </div>
                  )}
                </div>

                {/* Card Footer Actions */}
                <div className="mt-5 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                  <button
                    onClick={(e) => handleConfirm(e, scam.public_id)}
                    disabled={confirmingId === scam.public_id}
                    className="inline-flex items-center gap-1.5 text-slate-400 hover:text-cyan-300 transition-colors group/btn py-1"
                    title="Confirm this threat"
                  >
                    <ThumbsUp className={`w-3.5 h-3.5 group-hover/btn:scale-110 transition-transform ${confirmingId === scam.public_id ? 'animate-spin' : ''}`} />
                    <span>{scam.community_confirmations} Confirmations</span>
                  </button>

                  <span className="inline-flex items-center gap-1 text-cyan-400 font-semibold group-hover:translate-x-0.5 transition-transform">
                    View Dossier <ChevronRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination Bar */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between bg-slate-900/60 px-4 py-3 rounded-xl border border-slate-800">
            <div className="text-xs text-slate-400">
              Showing page <span className="font-semibold text-white">{page}</span> of <span className="font-semibold text-white">{totalPages}</span> ({totalCount} total threats)
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

      </div>

      {/* Forensic Dossier Modal */}
      {selectedScam && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
            
            {/* Modal Header */}
            <div className="px-6 py-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <ShieldAlert className="w-5 h-5 text-red-400" />
                <span className="font-mono text-sm font-bold text-cyan-400">{selectedScam.public_id}</span>
                <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getCategoryBadgeClass(selectedScam.scam_category)}`}>
                  {selectedScam.scam_category.replace(/_/g, ' ')}
                </span>
              </div>
              <button
                onClick={() => setSelectedScam(null)}
                className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-6">
              
              {/* Job & Impostor Header */}
              <div>
                <h2 className="text-xl font-extrabold text-white">{selectedScam.job_title}</h2>
                <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-slate-300">
                  <div className="flex items-center gap-1.5">
                    <Building2 className="w-4 h-4 text-slate-400" />
                    <span>Impostor: <strong className="text-white">{selectedScam.impostor_company}</strong></span>
                  </div>
                  {selectedScam.impostor_domain && (
                    <div className="flex items-center gap-1.5 font-mono text-xs bg-slate-800/80 px-2 py-0.5 rounded text-cyan-300 border border-slate-700">
                      <span>Domain: {selectedScam.impostor_domain}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Risk Gauge Bar */}
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="text-xs text-slate-400 uppercase font-semibold">Threat Risk Level</div>
                  <div className="text-xl font-bold text-red-400 mt-0.5 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5" />
                    {selectedScam.risk_score} / 100 ({selectedScam.risk_level.toUpperCase()})
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-400 uppercase font-semibold">Community Tally</div>
                  <div className="text-sm font-semibold text-cyan-400 mt-0.5">
                    {selectedScam.community_confirmations} Verified Job Seekers
                  </div>
                </div>
              </div>

              {/* Red Flags List */}
              {selectedScam.red_flags && selectedScam.red_flags.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4" />
                    Verified Scam Indicators & Evidence
                  </h4>
                  <ul className="space-y-2">
                    {selectedScam.red_flags.map((flag, i) => (
                      <li key={i} className="text-xs text-slate-200 flex items-start gap-2 bg-rose-500/5 p-2.5 rounded-lg border border-rose-500/20">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-1 shrink-0" />
                        <span>{flag}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Redacted Job Snippet */}
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                  Sanitized Job Content / Message
                </h4>
                <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 text-xs text-slate-300 leading-relaxed font-mono whitespace-pre-wrap">
                  {selectedScam.description_snippet}
                </div>
              </div>

              {/* Safe Action Guidance */}
              <div className="bg-cyan-950/30 border border-cyan-500/30 rounded-xl p-4 text-xs text-cyan-200 space-y-1.5">
                <div className="font-bold text-cyan-300 flex items-center gap-1.5">
                  <Info className="w-4 h-4" />
                  What you should do if contacted:
                </div>
                <p>1. <strong>Do not</strong> send any money, cryptocurrency (USDT), or deposit any cashier check.</p>
                <p>2. <strong>Do not</strong> share your SSN, banking info, or ID on Telegram or unverified forms.</p>
                <p>3. Verify the job directly on the official employer careers site or Applicant Tracking System (ATS).</p>
              </div>

            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between">
              <button
                onClick={(e) => handleConfirm(e, selectedScam.public_id)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-md transition-all"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
                Confirm Threat ({selectedScam.community_confirmations})
              </button>
              <button
                onClick={() => setSelectedScam(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-lg transition-colors"
              >
                Close Dossier
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}

export default CommunityScamDatabasePage;
