import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  ArrowLeft,
  AlertTriangle,
  Flame,
  CheckCircle2,
  XCircle,
  Gamepad2,
  BookOpen,
  Search,
  Filter,
  Sparkles,
  Trophy,
  Award,
  Zap,
  HelpCircle,
  ExternalLink,
  ChevronRight,
  RefreshCw,
  Mail,
  MessageSquare,
  Linkedin,
  ShieldCheck,
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import educationalService from '../services/educationalService';

const CATEGORIES = [
  'ALL',
  'Financial & Payment Traps',
  'Communication & Contact Channels',
  'Interview & Hiring Process',
  'Identity Theft & Privacy Extraction',
  'Role & Company Credibility',
];

const SEVERITIES = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'];

export const RedFlagsGuidePage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('directory'); // 'directory' | 'simulator'

  // Directory State
  const [redFlags, setRedFlags] = useState([]);
  const [loadingFlags, setLoadingFlags] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Simulator State
  const [scenarios, setScenarios] = useState([]);
  const [currentScenarioIndex, setCurrentScenarioIndex] = useState(0);
  const [loadingScenarios, setLoadingScenarios] = useState(true);
  const [submittingGuess, setSubmittingGuess] = useState(false);
  const [gameResult, setGameResult] = useState(null);
  const [userScore, setUserScore] = useState(0);
  const [userStreak, setUserStreak] = useState(0);
  const [completedScenarios, setCompletedScenarios] = useState(0);

  // Load Red Flags
  useEffect(() => {
    fetchRedFlags();
  }, [selectedCategory, selectedSeverity, searchQuery]);

  // Load Simulator Scenarios
  useEffect(() => {
    fetchScenarios();
  }, []);

  const fetchRedFlags = async () => {
    try {
      setLoadingFlags(true);
      const data = await educationalService.getRedFlags({
        category: selectedCategory,
        severity: selectedSeverity,
        search: searchQuery,
      });
      setRedFlags(data.red_flags || []);
    } catch (err) {
      console.error('Failed to fetch red flags:', err);
    } finally {
      setLoadingFlags(false);
    }
  };

  const fetchScenarios = async () => {
    try {
      setLoadingScenarios(true);
      const data = await educationalService.getSimulatorScenarios();
      setScenarios(data.scenarios || []);
    } catch (err) {
      console.error('Failed to fetch simulator scenarios:', err);
    } finally {
      setLoadingScenarios(false);
    }
  };

  const currentScenario = scenarios[currentScenarioIndex];

  const handleMakeGuess = async (isScamGuess) => {
    if (!currentScenario || submittingGuess || gameResult) return;

    try {
      setSubmittingGuess(true);
      const result = await educationalService.evaluateScenarioAttempt({
        scenarioId: currentScenario.id,
        userChoiceIsScam: isScamGuess,
        userFlaggedClues: [],
      });

      setGameResult(result);
      if (result.is_correct) {
        setUserScore((prev) => prev + result.total_xp);
        setUserStreak((prev) => prev + 1);
      } else {
        setUserStreak(0);
        setUserScore((prev) => prev + result.total_xp);
      }
      setCompletedScenarios((prev) => prev + 1);
    } catch (err) {
      console.error('Failed to evaluate guess:', err);
    } finally {
      setSubmittingGuess(false);
    }
  };

  const handleNextScenario = () => {
    setGameResult(null);
    if (currentScenarioIndex < scenarios.length - 1) {
      setCurrentScenarioIndex((prev) => prev + 1);
    } else {
      setCurrentScenarioIndex(0);
    }
  };

  const getRankTitle = (score) => {
    if (score >= 600) return { title: 'Chief Threat Detective', color: 'text-amber-400', badge: 'Diamond' };
    if (score >= 350) return { title: 'Senior Fraud Analyst', color: 'text-emerald-400', badge: 'Gold' };
    if (score >= 150) return { title: 'Junior Scam Hunter', color: 'text-skywash', badge: 'Silver' };
    return { title: 'Rookie Candidate', color: 'text-fog', badge: 'Bronze' };
  };

  const currentRank = getRankTitle(userScore);

  return (
    <div className="space-y-10 max-w-6xl mx-auto pb-20 pt-4 px-3 sm:px-0">
      
      {/* Top Header */}
      <div className="space-y-4">
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs text-fog hover:text-frost transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Job Scam Checker</span>
        </Link>

        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/25 bg-emerald-500/10 text-emerald-400 text-xs font-mono font-medium">
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>JobScamScore Forensic Matrix</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-semibold text-frost tracking-tight">
              25 Job Scam Red Flags & Simulator
            </h1>
            <p className="text-mist text-sm sm:text-base max-w-2xl font-light leading-relaxed">
              Master the 25 threat signatures weaponized by modern recruitment scammers, inspect verified forensic case studies, and test your skills in the Interactive Scam Hunter Game.
            </p>
          </div>

          {/* Tab Switcher Pills */}
          <div className="flex items-center p-1.5 rounded-2xl bg-black/60 border border-white/10 shrink-0 self-start md:self-auto">
            <button
              onClick={() => setActiveTab('directory')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
                activeTab === 'directory'
                  ? 'bg-emerald-500 text-white shadow-emerald-glow font-semibold'
                  : 'text-fog hover:text-frost hover:bg-white/5'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>25 Threat Matrix</span>
            </button>
            <button
              onClick={() => setActiveTab('simulator')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
                activeTab === 'simulator'
                  ? 'bg-emerald-500 text-white shadow-emerald-glow font-semibold'
                  : 'text-fog hover:text-frost hover:bg-white/5'
              }`}
            >
              <Gamepad2 className="w-3.5 h-3.5" />
              <span>Scam Hunter Game</span>
              <span className="px-1.5 py-0.2 rounded-full bg-amber-400/20 text-amber-300 font-mono text-[10px]">
                XP Mode
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* TAB 1: 25 RED FLAGS MATRIX */}
      {activeTab === 'directory' && (
        <div className="space-y-8 animate-in fade-in duration-200">
          
          {/* Filter & Search Bar */}
          <div className="glass-card rounded-2xl p-4 sm:p-5 border border-white/10 space-y-4">
            <div className="flex flex-col md:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-fog" />
                <input
                  type="text"
                  placeholder="Search by keywords (e.g. check, telegram, ssn, crypto, check bounce)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-black/40 border border-white/10 text-xs sm:text-sm text-frost placeholder-fog focus:outline-none focus:border-emerald-500/50"
                />
              </div>

              {/* Severity Quick Filter */}
              <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
                <span className="text-[11px] font-mono text-fog uppercase pl-1 pr-2">Severity:</span>
                {SEVERITIES.map((sev) => (
                  <button
                    key={sev}
                    onClick={() => setSelectedSeverity(sev)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all whitespace-nowrap ${
                      selectedSeverity === sev
                        ? sev === 'CRITICAL'
                          ? 'bg-red-500 text-white font-bold'
                          : sev === 'HIGH'
                          ? 'bg-amber-500 text-black font-bold'
                          : 'bg-emerald-500 text-white font-bold'
                        : 'bg-white/5 text-mist hover:text-frost hover:bg-white/10'
                    }`}
                  >
                    {sev}
                  </button>
                ))}
              </div>
            </div>

            {/* Category Filter Chips */}
            <div className="flex flex-wrap gap-2 pt-1 border-t border-white/5">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                    selectedCategory === cat
                      ? 'bg-white/20 text-frost border border-white/30 font-semibold'
                      : 'bg-white/5 text-fog hover:text-frost border border-transparent hover:bg-white/10'
                  }`}
                >
                  {cat === 'ALL' ? 'All Categories (25)' : cat}
                </button>
              ))}
            </div>
          </div>

          {/* Red Flags Grid */}
          {loadingFlags ? (
            <div className="py-20 flex justify-center">
              <LoadingSpinner text="Loading 25 threat signatures..." size="lg" />
            </div>
          ) : redFlags.length === 0 ? (
            <div className="p-12 text-center glass-card rounded-2xl border border-white/10 space-y-3">
              <HelpCircle className="w-8 h-8 text-fog mx-auto" />
              <p className="text-frost font-medium">No red flags matched your filters.</p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setSelectedCategory('ALL');
                  setSelectedSeverity('ALL');
                  setSearchQuery('');
                }}
              >
                Reset Filters
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {redFlags.map((rf) => (
                <div
                  key={rf.id}
                  className="glass-card rounded-2xl p-5 sm:p-6 border border-white/10 hover:border-emerald-500/30 transition-all flex flex-col justify-between space-y-4 group"
                >
                  <div className="space-y-3">
                    {/* Number & Badges */}
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="flex items-center justify-center w-6 h-6 rounded-md bg-white/10 text-frost font-mono text-xs font-bold">
                          #{rf.number}
                        </span>
                        <span className="text-[11px] font-medium text-fog uppercase tracking-wider">
                          {rf.category}
                        </span>
                      </div>
                      <span
                        className={`px-2 py-0.5 rounded-md text-[10px] font-mono font-bold uppercase tracking-wider ${
                          rf.severity === 'CRITICAL'
                            ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                            : rf.severity === 'HIGH'
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        }`}
                      >
                        {rf.severity} RISK
                      </span>
                    </div>

                    {/* Title & Summary */}
                    <h3 className="text-base sm:text-lg font-semibold text-frost group-hover:text-emerald-300 transition-colors">
                      {rf.title}
                    </h3>
                    <p className="text-xs text-mist leading-relaxed font-light">
                      {rf.summary}
                    </p>

                    {/* Indicators list */}
                    <div className="space-y-1.5 pt-1">
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-fog">
                        Warning Indicators:
                      </span>
                      <ul className="space-y-1">
                        {rf.indicators.map((ind, idx) => (
                          <li key={idx} className="flex items-start gap-1.5 text-xs text-slate-300">
                            <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                            <span>{ind}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Real Scammer Snippet */}
                    <div className="p-3 rounded-xl bg-black/50 border border-white/10 space-y-1">
                      <span className="text-[9px] font-mono uppercase tracking-wider text-fog">
                        Real Scammer Excerpt:
                      </span>
                      <p className="text-xs text-slate-300 font-mono italic leading-relaxed">
                        "{rf.real_scam_snippet}"
                      </p>
                    </div>
                  </div>

                  {/* Safety Protocol */}
                  <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/20 flex items-start gap-2 text-xs text-emerald-300 leading-relaxed">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <div>
                      <strong className="font-semibold text-emerald-200">Safety Protocol: </strong>
                      <span>{rf.safety_protocol}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: INTERACTIVE SCAM HUNTER SIMULATOR GAME */}
      {activeTab === 'simulator' && (
        <div className="space-y-8 animate-in fade-in duration-200">
          
          {/* Game Stats & Rank Banner */}
          <div className="glass-card rounded-2xl p-5 sm:p-6 border border-white/10 flex flex-col sm:flex-row items-center justify-between gap-6 shadow-hairline-inset">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400">
                <Trophy className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-fog">Current Rank</span>
                <h2 className={`text-xl font-bold ${currentRank.color}`}>{currentRank.title}</h2>
                <p className="text-xs text-mist">
                  {completedScenarios} Scenarios Investigated • Tier: {currentRank.badge}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-6 divide-x divide-white/10">
              <div className="text-center px-3">
                <div className="flex items-center justify-center gap-1 text-amber-400 font-mono font-bold text-xl">
                  <Zap className="w-4 h-4" />
                  <span>{userScore}</span>
                </div>
                <span className="text-[10px] text-fog uppercase font-mono">Total XP</span>
              </div>

              <div className="text-center pl-6">
                <div className="flex items-center justify-center gap-1 text-emerald-400 font-mono font-bold text-xl">
                  <Flame className="w-4 h-4" />
                  <span>{userStreak}</span>
                </div>
                <span className="text-[10px] text-fog uppercase font-mono">Current Streak</span>
              </div>
            </div>
          </div>

          {/* Scenario Board */}
          {loadingScenarios ? (
            <div className="py-20 flex justify-center">
              <LoadingSpinner text="Loading scam investigation simulator..." size="lg" />
            </div>
          ) : !currentScenario ? (
            <div className="p-8 text-center glass-card rounded-2xl border border-white/10">
              <p className="text-frost">No scenarios loaded.</p>
            </div>
          ) : (
            <div className="glass-card rounded-3xl p-6 sm:p-8 border border-white/15 space-y-6 shadow-2xl relative overflow-hidden">
              
              {/* Scenario Top Bar */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-white/10">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-white/10 text-frost">
                      Case #{currentScenarioIndex + 1} of {scenarios.length}
                    </span>
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-mono uppercase bg-skywash/15 text-skywash border border-skywash/30">
                      {currentScenario.difficulty} Difficulty
                    </span>
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-mono text-fog border border-white/10 flex items-center gap-1">
                      {currentScenario.channel === 'Email' && <Mail className="w-3 h-3 text-skywash" />}
                      {currentScenario.channel === 'SMS' && <MessageSquare className="w-3 h-3 text-emerald-400" />}
                      {currentScenario.channel === 'LinkedIn' && <Linkedin className="w-3 h-3 text-blue-400" />}
                      <span>{currentScenario.channel} Case</span>
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold text-frost">
                    {currentScenario.title}
                  </h3>
                </div>

                <div className="text-xs font-mono text-fog">
                  <span>Potential Bounty: </span>
                  <span className="text-amber-400 font-bold">+{currentScenario.xp_reward} XP</span>
                </div>
              </div>

              {/* Message Simulation Client Card */}
              <div className="rounded-2xl bg-black/60 border border-white/15 p-5 sm:p-6 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-white/10 text-xs">
                  <div className="flex items-center gap-2 truncate">
                    <span className="text-fog">Sender:</span>
                    <span className="font-mono text-emerald-400 font-medium truncate">
                      {currentScenario.sender}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-fog">Encrypted Channel</span>
                </div>

                {/* Body Text */}
                <div className="font-mono text-xs sm:text-sm text-slate-200 whitespace-pre-wrap leading-relaxed">
                  {currentScenario.body}
                </div>
              </div>

              {/* Interactive Guess Actions (If not yet submitted) */}
              {!gameResult && (
                <div className="space-y-4 pt-2">
                  <p className="text-center text-xs text-mist font-light">
                    Carefully analyze the sender domain, interview method, compensation, and payment instructions. What is your forensic verdict?
                  </p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <button
                      onClick={() => handleMakeGuess(false)}
                      disabled={submittingGuess}
                      className="p-4 rounded-2xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 hover:border-emerald-500/60 text-emerald-400 font-semibold text-sm transition-all flex items-center justify-center gap-2 group disabled:opacity-50"
                    >
                      <ShieldCheck className="w-5 h-5 group-hover:scale-110 transition-transform" />
                      <span>Legitimate Job Offer</span>
                    </button>

                    <button
                      onClick={() => handleMakeGuess(true)}
                      disabled={submittingGuess}
                      className="p-4 rounded-2xl bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 hover:border-red-500/60 text-red-400 font-semibold text-sm transition-all flex items-center justify-center gap-2 group disabled:opacity-50"
                    >
                      <AlertTriangle className="w-5 h-5 group-hover:scale-110 transition-transform" />
                      <span>Fraudulent Scam / Phishing</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Evaluation Result Card (When submitted) */}
              {gameResult && (
                <div className="space-y-5 pt-2 animate-in fade-in duration-200">
                  <div
                    className={`p-5 rounded-2xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${
                      gameResult.is_correct
                        ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300'
                        : 'bg-red-950/30 border-red-500/40 text-red-300'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      {gameResult.is_correct ? (
                        <CheckCircle2 className="w-8 h-8 text-emerald-400 shrink-0" />
                      ) : (
                        <XCircle className="w-8 h-8 text-red-400 shrink-0" />
                      )}
                      <div>
                        <h4 className="text-base font-bold text-frost">
                          {gameResult.is_correct ? 'Correct Forensic Analysis!' : 'Incorrect Identification!'}
                        </h4>
                        <p className="text-xs text-mist">
                          Actual Verdict: <strong className="text-frost">{gameResult.actual_verdict}</strong>
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 font-mono text-xs font-bold px-3 py-1.5 rounded-xl bg-black/40 border border-white/10 text-amber-300">
                      <Sparkles className="w-4 h-4 text-amber-400" />
                      <span>+{gameResult.total_xp} XP Earned</span>
                    </div>
                  </div>

                  {/* Forensic Explanation */}
                  <div className="p-5 rounded-2xl bg-black/50 border border-white/10 space-y-3">
                    <h5 className="text-xs font-semibold uppercase tracking-wider text-fog">
                      Forensic Investigation Summary:
                    </h5>
                    <p className="text-xs sm:text-sm text-mist leading-relaxed font-light">
                      {gameResult.forensic_explanation}
                    </p>

                    {/* Detected Red Flags */}
                    {gameResult.red_flags && gameResult.red_flags.length > 0 && (
                      <div className="space-y-1.5 pt-2 border-t border-white/5">
                        <span className="text-[10px] font-mono text-fog uppercase">
                          Detected Red Flags in this Case:
                        </span>
                        <ul className="space-y-1">
                          {gameResult.red_flags.map((rf, idx) => (
                            <li key={idx} className="flex items-center gap-2 text-xs text-red-300">
                              <AlertTriangle className="w-3.5 h-3.5 text-red-400 shrink-0" />
                              <span>{rf}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* Next Scenario Button */}
                  <div className="flex justify-end pt-2">
                    <Button
                      variant="primary"
                      size="md"
                      onClick={handleNextScenario}
                      className="bg-emerald-500 hover:bg-emerald-400 flex items-center gap-2"
                    >
                      <span>Next Case Investigation</span>
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}

            </div>
          )}

        </div>
      )}

      {/* Bottom Floating CTA Banner */}
      <div className="p-8 rounded-2xl glass-card border border-emerald-500/25 text-center space-y-4 shadow-emerald-glow">
        <h3 className="text-xl sm:text-2xl font-semibold text-frost">
          Have an actual suspicious job offer in your inbox right now?
        </h3>
        <p className="text-xs sm:text-sm text-mist max-w-xl mx-auto font-light">
          Run an instant forensic scan with our 50+ threat heuristics, Phone VoIP lookup, and 2026 FTC/IC3 fraud watchlists.
        </p>
        <Button
          variant="primary"
          size="lg"
          onClick={() => navigate('/analyze')}
          className="bg-emerald-500 hover:bg-emerald-400 shadow-emerald-button"
        >
          Scan Your Job Offer Now →
        </Button>
      </div>

    </div>
  );
};

export default RedFlagsGuidePage;
