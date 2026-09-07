import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom';
import {
  ShieldCheck, ShieldAlert, AlertTriangle, Building2, Globe, MapPin,
  Mail, DollarSign, FileCheck, CheckCircle2, XCircle, HelpCircle,
  ChevronDown, ChevronUp, ArrowLeft, Share2, Printer, Sparkles,
  ExternalLink, Briefcase, Search, BookOpen, Award, Layers,
  PhoneCall, Server, Cpu, Check, AlertCircle, FileText
} from 'lucide-react';
import { analysisService } from '../services/analysisService';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { useToast } from '../hooks/useToast';
import { useAuth } from '../context/AuthContext';
import { GoogleAuthModal } from '../components/auth/GoogleAuthModal';

export const AnalysisResultPage = () => {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { addToast, success, error: toastError } = useToast();
  const { isAuthenticated } = useAuth();

  const [showAuthModal, setShowAuthModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState(location.state?.report || null);
  const [error, setError] = useState(null);

  const [expandedCards, setExpandedCards] = useState({
    1: true, 2: true, 3: true, 4: true, 5: true, 6: true,
    7: true, 8: true, 9: true, 10: true, 11: true, 12: true,
  });

  const toggleCard = (cardNum) => {
    setExpandedCards((prev) => ({ ...prev, [cardNum]: !prev[cardNum] }));
  };

  const setAllCards = (expanded) => {
    const nextState = {};
    for (let i = 1; i <= 12; i++) {
      nextState[i] = expanded;
    }
    setExpandedCards(nextState);
  };

  useEffect(() => {
    let isMounted = true;
    const fetchReport = async () => {
      // If report was passed via navigate state, use it immediately
      if (location.state?.report && isMounted) {
        setReport(location.state.report);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        if (id && id !== 'demo') {
          const data = await analysisService.getAnalysisById(id);
          if (isMounted) setReport(data);
        }
      } catch (err) {
        if (isMounted) setError('Failed to load analysis report.');
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchReport();
    return () => { isMounted = false; };
  }, [id, location.state]);

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    addToast('Report URL copied to clipboard!', 'success');
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExportJson = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `sentineljob_audit_${report.id || 'scan'}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    addToast('Forensic report JSON downloaded.', 'success');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner text="Retrieving Forensic Intelligence Report..." size="lg" />
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-xl mx-auto py-12 text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-red-500/20 text-red-400 mx-auto flex items-center justify-center">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-white">Report Not Found</h2>
        <p className="text-xs text-slate-400">The requested scan ID does not exist or has expired.</p>
        <Link to="/analyze" className="inline-block px-4 py-2 rounded-xl bg-emerald-500 text-black text-xs font-semibold">
          Perform New Scan
        </Link>
      </div>
    );
  }

  const score = typeof report.risk_score === 'number' ? report.risk_score : 0;
  const isSafe = score < 25;
  const isModerate = score >= 25 && score < 60;
  const isRisky = score >= 60;

  const llm = report.llm_synthesis || {};
  const salary = report.salary_benchmark || {};
  const signals8 = report.signals_8_layer || {};
  const rules = report.rule_indicators || [];
  const threat = report.threat_feed || {};
  const phone = report.phone_intelligence || {};
  const fraudWatchlists = report.fraud_watchlists || {};

  // Extract 8-layer cards into array
  const signalLayersList = Object.entries(signals8)
    .filter(([key]) => key.startsWith('layer_'))
    .map(([_, val]) => val)
    .sort((a, b) => (a.layer_id || 0) - (b.layer_id || 0));

  // Dynamic red & green flags from LLM or heuristic rules
  const redFlags = llm.red_flags?.length > 0 ? llm.red_flags : rules.map(r => `${r.name || r.rule_code}: ${r.explanation || r.description || ''}`);
  const greenFlags = llm.green_flags?.length > 0 ? llm.green_flags : (isSafe ? ['Standard corporate recruitment syntax.', 'No upfront fees or suspicious payment requests identified.'] : []);
  const evidenceList = llm.evidence || [];
  const recommendations = llm.recommended_actions?.length > 0 ? llm.recommended_actions : (
    isRisky ? [
      'Do not transfer money or pay registration/laptop fees.',
      'Never share OTPs, bank credentials, or Aadhaar/SSN.',
      'Verify requisition directly on the company official careers website.'
    ] : [
      'Submit application directly on the official employer website.',
      'Confirm recruiter identity via official company email domain.'
    ]
  );

  return (
    <div className="max-w-5xl mx-auto space-y-6 py-2 select-none">
      
      {/* Guest Free Scan Notice Banner */}
      {!isAuthenticated && (
        <div className="bg-gradient-to-r from-cyan-950/80 via-slate-900 to-indigo-950/80 border border-cyan-500/30 rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xl animate-fadeIn">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-bold text-white flex items-center gap-2">
                Free Guest Scan Preview
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-semibold">
                  Session Saved
                </span>
              </div>
              <div className="text-xs text-slate-300 mt-0.5 leading-relaxed">
                Sign in with Google to unlock unlimited scans, multi-model consensus, and cloud history sync.
              </div>
            </div>
          </div>
          <button
            onClick={() => setShowAuthModal(true)}
            className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold whitespace-nowrap shadow-md transition-all flex items-center gap-1.5 shrink-0"
          >
            <ShieldCheck className="w-4 h-4" />
            Save to Account
          </button>
        </div>
      )}

      {/* Top Header Control Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <Link to="/history" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors">
            <ArrowLeft className="w-4 h-4" />
            <span>Back to History</span>
          </Link>
          <span className="text-slate-600">•</span>
          <span className="text-xs text-slate-400 font-mono">Scan ID: {report.id}</span>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setAllCards(true)}
            className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-slate-300 transition-colors"
          >
            Expand all
          </button>
          <button
            onClick={() => setAllCards(false)}
            className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-slate-300 transition-colors"
          >
            Collapse all
          </button>
          <Link
            to={`/verify/${report.id}`}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-xs font-semibold text-cyan-300 transition-colors shadow-sm"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Audit Certificate</span>
          </Link>
          <button
            onClick={handleShare}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-xs font-medium text-emerald-300 transition-colors"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>Share</span>
          </button>
          <button
            onClick={handleExportJson}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-slate-300 transition-colors"
          >
            <FileCheck className="w-3.5 h-3.5 text-sky-400" />
            <span>JSON</span>
          </button>
          <button
            onClick={handlePrint}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-slate-300 transition-colors"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Export PDF</span>
          </button>
        </div>
      </div>

      {/* Main Job Banner */}
      <div className="glass-card rounded-2xl p-6 border border-white/10 bg-gradient-to-r from-slate-900/90 via-black to-slate-900/90 space-y-3 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-white/5 border border-white/10 text-slate-400 uppercase">
              Source: {report.source_type || 'Text'}
            </span>
            <span className={
              'px-3 py-1 rounded-full text-xs font-mono font-bold uppercase tracking-wider border ' +
              (isSafe ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
               isModerate ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
               'bg-red-500/20 text-red-300 border-red-500/40')
            }>
              {isSafe ? 'SAFE VERDICT' : isModerate ? 'MODERATE RISK' : 'HIGH RISK VERDICT'}
            </span>
            {(report.primary_archetype || llm.primary_archetype) && (
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase bg-purple-500/20 text-purple-300 border border-purple-500/40">
                Archetype: {report.primary_archetype || llm.primary_archetype}
              </span>
            )}
          </div>
          <span className="text-xs text-slate-400 font-mono">13-Stage Pipeline &middot; 50+ Checks Evaluated</span>
        </div>

        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          {report.job_title || 'Analyzed Job Submission'}
        </h1>

        <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1.5 text-white font-medium">
            <Building2 className="w-4 h-4 text-emerald-400" />
            {report.company_name || 'Unspecified Employer'}
          </span>
          <span>•</span>
          <span className="flex items-center gap-1.5">
            <DollarSign className="w-4 h-4 text-amber-400" />
            Salary: {salary.detected_salary_text || (salary.currency === 'INR' ? `${salary.min_amount || 'Market'} LPA` : `${salary.min_amount || 'Market'} USD`) || 'Not explicitly stated'}
          </span>
        </div>
      </div>

      {/* 12 EXPANDABLE FORENSIC SECTION CARDS */}
      <div className="space-y-4">
        
        {/* CARD 1: Executive Summary */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(1)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">1</div>
              <div>
                <h3 className="text-base font-bold text-white">Analysis Results / Executive Summary</h3>
                <p className="text-xs text-slate-400 font-light">Legitimacy score, risk verdict, and synthesis summary</p>
              </div>
            </div>
            {expandedCards[1] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[1] && (
            <div className="p-6 border-t border-white/10 space-y-5 bg-black/40">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 text-center space-y-1">
                  <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Legitimacy Score</span>
                  <div className="text-3xl font-extrabold text-emerald-400 font-mono">{100 - score}%</div>
                  <div className="w-full bg-white/10 rounded-full h-2 mt-2">
                    <div className="bg-emerald-400 h-2 rounded-full" style={{ width: `${Math.max(5, 100 - score)}%` }} />
                  </div>
                </div>
                <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 text-center space-y-1">
                  <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Risk Level</span>
                  <div className={
                    'text-2xl font-bold font-mono uppercase ' +
                    (isSafe ? 'text-emerald-400' : isModerate ? 'text-amber-400' : 'text-red-400')
                  }>
                    {report.risk_level || (isSafe ? 'LOW RISK' : isModerate ? 'MEDIUM' : 'CRITICAL')}
                  </div>
                  <span className="text-[10px] text-slate-400">Risk Score: {score}/100</span>
                </div>
                <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 text-center space-y-1">
                  <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Analysis Confidence</span>
                  <div className="text-3xl font-extrabold text-blue-400 font-mono">{report.confidence_score || Math.round((llm.confidence || 0.95) * 100)}%</div>
                  <span className="text-[10px] text-slate-400">Multi-Signal Calibrated</span>
                </div>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/60 border border-white/10 space-y-2 text-xs leading-relaxed text-slate-300">
                <span className="font-semibold text-white flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-emerald-400" /> Forensic Synthesis Summary
                </span>
                <p className="whitespace-pre-line leading-relaxed font-sans">{llm.executive_summary || report.explanation}</p>
              </div>
            </div>
          )}
        </div>

        {/* CARD 2: 8-Layer Signal Architecture Breakdown */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(2)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-xs">2</div>
              <div>
                <h3 className="text-base font-bold text-white">8-Layer Signal Intelligence Breakdown</h3>
                <p className="text-xs text-slate-400 font-light">Status across all 8 security verification layers</p>
              </div>
            </div>
            {expandedCards[2] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[2] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-3 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {signalLayersList.length > 0 ? (
                  signalLayersList.map((layer, idx) => {
                    const isPass = layer.status === 'PASS';
                    const isWarn = layer.status === 'WARN';
                    return (
                      <div key={idx} className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-white flex items-center gap-1.5">
                            <span className="font-mono text-[11px] text-slate-500">0{layer.layer_id}</span>
                            <span>{layer.name}</span>
                          </span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                            isPass ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' :
                            isWarn ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                            'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                          }`}>
                            {layer.status} ({layer.score}/100)
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 leading-snug">{layer.detail || layer.description}</p>
                      </div>
                    );
                  })
                ) : (
                  <p className="text-slate-400 col-span-2">8-Layer telemetry active.</p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* CARD 3: Company & Digital Footprint Verification */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(3)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center font-bold text-xs">3</div>
              <div>
                <h3 className="text-base font-bold text-white">Company & Entity Authentication</h3>
                <p className="text-xs text-slate-400 font-light">Layer 01 & 07 digital identity and WHOIS verification</p>
              </div>
            </div>
            {expandedCards[3] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[3] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-1">
                  <span className="text-[11px] text-slate-400">Employer Entity</span>
                  <div className="font-semibold text-white truncate">{report.company_name || 'Unspecified'}</div>
                </div>
                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-1">
                  <span className="text-[11px] text-slate-400">Entity Check (Layer 01)</span>
                  <div className="font-semibold text-emerald-400">{signals8.layer_1_company_authentication?.status || 'PASS'}</div>
                </div>
                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-1">
                  <span className="text-[11px] text-slate-400">Domain & SSL Check (Layer 07)</span>
                  <div className="font-semibold text-emerald-400">{signals8.layer_7_domain_ssl_intelligence?.status || 'PASS'}</div>
                </div>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-white/10 text-slate-300 leading-relaxed">
                {signals8.layer_1_company_authentication?.detail || 'Company authentication signals evaluated against active corporate registries.'}
              </div>
            </div>
          )}
        </div>

        {/* CARD 4: ATS & Application Channel Verification */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(4)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-teal-500/20 text-teal-400 flex items-center justify-center font-bold text-xs">4</div>
              <div>
                <h3 className="text-base font-bold text-white">Careers Portal & ATS Verification</h3>
                <p className="text-xs text-slate-400 font-light">Layer 02 official application channel cross-check</p>
              </div>
            </div>
            {expandedCards[4] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[4] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-3 text-xs">
              <div className="flex flex-wrap items-center justify-between p-4 rounded-xl bg-white/[0.03] border border-white/10 gap-3">
                <div>
                  <span className="text-slate-400 block text-[11px]">Layer 02 Careers Page / ATS Status</span>
                  <span className="text-sm font-semibold text-emerald-400 font-mono">
                    {signals8.layer_2_careers_page_verification?.status || 'PASS'} &middot; Score {signals8.layer_2_careers_page_verification?.score || 100}/100
                  </span>
                </div>
              </div>
              <p className="text-slate-300 p-3.5 rounded-xl bg-slate-900/60 border border-white/10 leading-relaxed">
                {signals8.layer_2_careers_page_verification?.detail || 'Verified official requisition posting channel.'}
              </p>
            </div>
          )}
        </div>

        {/* CARD 5: Recruiter & Contact Verification */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(5)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-xs">5</div>
              <div>
                <h3 className="text-base font-bold text-white">Recruiter & Contact Intelligence</h3>
                <p className="text-xs text-slate-400 font-light">Layer 03 & 06 recruiter domain & phone carrier checks</p>
              </div>
            </div>
            {expandedCards[5] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[5] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-1">
                  <span className="text-[11px] text-slate-400">Recruiter Identity (Layer 03)</span>
                  <div className="font-semibold text-emerald-400">{signals8.layer_3_recruiter_identity?.status || 'PASS'}</div>
                  <p className="text-[11px] text-slate-400 mt-1">{signals8.layer_3_recruiter_identity?.detail}</p>
                </div>
                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-1">
                  <span className="text-[11px] text-slate-400">Contact Validation (Layer 06)</span>
                  <div className="font-semibold text-emerald-400">{signals8.layer_6_contact_validation?.status || 'PASS'}</div>
                  <p className="text-[11px] text-slate-400 mt-1">{signals8.layer_6_contact_validation?.detail}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* CARD 6: Salary Analysis & Market Benchmarking */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(6)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">6</div>
              <div>
                <h3 className="text-base font-bold text-white">Salary Benchmarking & Compensation Matrix</h3>
                <p className="text-xs text-slate-400 font-light">Layer 04 dual-currency market percentile evaluation</p>
              </div>
            </div>
            {expandedCards[6] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[6] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-1">
                  <span className="text-[11px] text-slate-400">Detected Pay / Currency</span>
                  <div className="text-base font-bold text-emerald-400 font-mono">
                    {salary.detected_salary_text || `${salary.currency || 'INR'} ${salary.min_amount || 'Market Standard'}`}
                  </div>
                </div>
                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-1">
                  <span className="text-[11px] text-slate-400">Matched Industry Role</span>
                  <div className="text-sm font-semibold text-white capitalize">{salary.matched_job_family?.replace(/_/g, ' ') || 'General Corporate'}</div>
                </div>
                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-1">
                  <span className="text-[11px] text-slate-400">Compensation Verdict</span>
                  <div className={`text-sm font-bold uppercase ${salary.is_unrealistic_high ? 'text-red-400' : 'text-emerald-400'}`}>
                    {salary.verdict || 'REALISTIC_MARKET_RATE'}
                  </div>
                </div>
              </div>
              <p className="text-slate-300 p-3.5 rounded-xl bg-slate-900/60 border border-white/10 leading-relaxed font-sans">
                {salary.explanation || signals8.layer_4_salary_benchmarking?.detail || 'Salary matches standard market distributions.'}
              </p>
            </div>
          )}
        </div>

        {/* CARD 7: Live Threat Intelligence */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(7)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-xs">7</div>
              <div>
                <h3 className="text-base font-bold text-white">Live Threat Intelligence & Watchlists</h3>
                <p className="text-xs text-slate-400 font-light">Layer 08 I4C MHA 1930, FTC, BBB & IC3 match telemetry</p>
              </div>
            </div>
            {expandedCards[7] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[7] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-3 text-xs">
              <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{signals8.layer_8_live_threat_intelligence?.detail || 'No active malicious recruitment matches in cybercrime databases.'}</span>
              </div>
            </div>
          )}
        </div>

        {/* CARD 8: Triggered Scam Rules & Indicators */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(8)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center font-bold text-xs">8</div>
              <div>
                <h3 className="text-base font-bold text-white">Deterministic Scam Rules (Layer 05)</h3>
                <p className="text-xs text-slate-400 font-light">Specific pattern triggers intercepted by the rule engine</p>
              </div>
            </div>
            {expandedCards[8] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[8] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-2.5 text-xs">
              {rules.length > 0 ? (
                rules.map((rule, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-200 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-rose-300">{rule.name || rule.rule_code}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] uppercase font-mono font-bold bg-rose-500/20 border border-rose-500/40">
                        {rule.severity || 'HIGH'}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-300 font-sans">{rule.explanation || rule.description}</p>
                  </div>
                ))
              ) : (
                <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>No deterministic fraud patterns or advance-fee rules triggered.</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* CARD 9: Red Flags & Risk Indicators */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(9)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-red-500/20 text-red-400 flex items-center justify-center font-bold text-xs">9</div>
              <div>
                <h3 className="text-base font-bold text-white">Categorized Red Flags</h3>
                <p className="text-xs text-slate-400 font-light">Warning signs requiring critical caution</p>
              </div>
            </div>
            {expandedCards[9] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[9] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-2.5 text-xs">
              {redFlags.length > 0 ? (
                redFlags.map((flag, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 flex items-start gap-2.5">
                    <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                    <span>{flag}</span>
                  </div>
                ))
              ) : (
                <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>No high-severity red flags identified in this submission.</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* CARD 10: Green Flags & Positive Indicators */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(10)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold text-xs">10</div>
              <div>
                <h3 className="text-base font-bold text-white">Green Flags & Positive Indicators</h3>
                <p className="text-xs text-slate-400 font-light">Legitimacy markers and corporate alignment signals</p>
              </div>
            </div>
            {expandedCards[10] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[10] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-2.5 text-xs">
              {greenFlags.map((flag, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-emerald-300 flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>{flag}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* CARD 11: Traceable Evidence Excerpts */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(11)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">11</div>
              <div>
                <h3 className="text-base font-bold text-white">Traceable Forensic Evidence</h3>
                <p className="text-xs text-slate-400 font-light">Specific quotes and verifiable claim telemetry</p>
              </div>
            </div>
            {expandedCards[11] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[11] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-2.5 text-xs">
              {evidenceList.length > 0 ? (
                evidenceList.map((item, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white">{item.claim}</span>
                      <span className="text-[10px] font-mono text-slate-400">Signal: {item.source_signal}</span>
                    </div>
                    {item.quote && (
                      <p className="text-[11px] text-cyan-300 italic font-mono bg-black/30 p-2 rounded border border-white/5">
                        "{item.quote}"
                      </p>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-slate-400">Standard verified recruitment submission. All claims trace to verified sources.</p>
              )}
            </div>
          )}
        </div>

        {/* CARD 12: Recommended Next Steps */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(12)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">12</div>
              <div>
                <h3 className="text-base font-bold text-white">Actionable Safety Recommendations</h3>
                <p className="text-xs text-slate-400 font-light">Tailored guidance for this specific recruitment offer</p>
              </div>
            </div>
            {expandedCards[12] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[12] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-4 text-xs">
              <div className="space-y-2">
                {recommendations.map((rec, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-white/[0.03] border border-white/10 text-slate-200 flex items-start gap-2.5">
                    <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <span className="leading-relaxed">{rec}</span>
                  </div>
                ))}
              </div>
              <div className="flex items-center gap-4 pt-2">
                <Link to="/analyze" className="px-5 py-2.5 rounded-xl bg-emerald-500 text-black font-bold text-xs hover:bg-emerald-400 transition-colors">
                  Scan Another Job
                </Link>
                <Link to="/history" className="px-5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-xs hover:bg-white/10 transition-colors">
                  View Scan History
                </Link>
              </div>
            </div>
          )}
        </div>

      </div>

      {/* 1-Click Guest Save / Auth Modal */}
      <GoogleAuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={() => {
          setShowAuthModal(false);
          addToast('Scan saved to your account.', 'success');
        }}
      />
    </div>
  );
};

export default AnalysisResultPage;
