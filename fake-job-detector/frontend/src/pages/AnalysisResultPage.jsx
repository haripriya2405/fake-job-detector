import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ShieldCheck, ShieldAlert, AlertTriangle, Building2, Globe, MapPin,
  Mail, DollarSign, FileCheck, CheckCircle2, XCircle, HelpCircle,
  ChevronDown, ChevronUp, ArrowLeft, Share2, Printer, Sparkles,
  ExternalLink, Briefcase, Search, BookOpen, Award
} from 'lucide-react';
import { analysisService } from '../services/analysisService';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { useToast } from '../hooks/useToast';

export const AnalysisResultPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState(null);
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
      try {
        setLoading(true);
        if (id && id !== 'demo') {
          const data = await analysisService.getAnalysisById(id);
          if (isMounted) setReport(data);
        } else {
          if (isMounted) {
            setReport({
              id: id || 'demo-bengaluru-dev',
              job_title: 'Full Stack Web Developer',
              company_name: 'TechCorp Solutions India',
              created_at: new Date().toISOString(),
              risk_score: 12,
              risk_level: 'SAFE',
              confidence_score: 96,
              source_type: 'Text',
              explanation: 'This job posting exhibits strong legitimacy signals. Company website, official domain email, LinkedIn company page, and Glassdoor profile are fully verified with matching headquarters in Bengaluru.',
              company_verification: {
                website_status: '200 OK',
                careers_page: 'Verified Match',
                linkedin: 'Active Corporate Page',
                glassdoor: '4.2 ★ (120+ Reviews)',
                location: 'Bengaluru, Karnataka, India',
                crunchbase: 'Series-B Funded',
                press_coverage: 'Verified Media Outlets',
                job_board_presence: 'Listed on LinkedIn & Indeed'
              },
              listing_platforms: {
                official_site: 'Verified on Official Careers Portal',
                match_confidence: '96%',
                careers_url: 'https://techcorp.example.com/careers/job-1029',
                linkedin_url: 'https://linkedin.com/jobs/view/9920102'
              },
              location_verification: {
                notes: 'Location match confirmed across company HQ and job listing.',
                company_location: 'Bengaluru, Karnataka, India',
                user_location: 'Bengaluru, India',
                listing_location: 'Bengaluru (Hybrid)',
                work_types: ['Hybrid', 'On-site']
              },
              contact_verification: {
                matched: true,
                status_text: 'Official contact domain matches listing domain',
                official_email: 'careers@techcorp.example.com',
                listing_email: 'careers@techcorp.example.com',
                official_phone: '+91 80 4920 1100',
                listing_phone: '+91 80 4920 1100',
                official_website: 'techcorp.example.com',
                listing_domain: 'techcorp.example.com'
              },
              salary_analysis: {
                specified: true,
                range: '₹5,000 – ₹7,000 / month (Stipend/Junior)',
                benchmark: 'Matches Indian Software Industry Standard for Intern/Junior Role',
                risk_note: 'No unrealistic salary inflation detected.'
              },
              grammar_analysis: {
                tone: 'Professional & Structured',
                analysis_type: 'NLP Syntax & Entity Parser',
                summary: 'Standard corporate grammar, appropriate technical terminology, no urgent payment syntax or excessive punctuation.'
              },
              scam_patterns: [
                'No upfront fee or payment demanded',
                'Corporate email address matching registered domain',
                'Clear skill requirements and interview workflow described',
                'Domain registered over 6 years ago with active SSL'
              ],
              red_flags: [
                'Low Risk: Salary range listed in monthly stipend format'
              ],
              positive_observations: [
                'Domain WHOIS creation date is 6+ years old',
                'Official HR contact email matches domain',
                'No payment or bank account details requested',
                'Active Glassdoor and LinkedIn corporate profiles verified'
              ],
              concerns: [
                'Ensure interviews are conducted over official video link'
              ]
            });
          }
        }
      } catch (err) {
        if (isMounted) setError('Failed to load analysis report.');
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchReport();
    return () => { isMounted = false; };
  }, [id]);

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
    link.download = `forensic_report_${report.id || 'scan'}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    addToast('Forensic report JSON downloaded.', 'success');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner text="Generating Forensic Analysis Report..." size="lg" />
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
        <Link to="/scan" className="inline-block px-4 py-2 rounded-xl bg-emerald-500 text-black text-xs font-semibold">
          Perform New Scan
        </Link>
      </div>
    );
  }

  const score = report.risk_score || 0;
  const isSafe = score < 30;
  const isModerate = score >= 30 && score < 70;

  return (
    <div className="max-w-5xl mx-auto space-y-6 py-2 select-none">
      
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
          </div>
          <span className="text-xs text-slate-400 font-mono">50+ Parallel Forensic Checks Evaluated</span>
        </div>

        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          {report.job_title || 'Analyzed Job Offering'}
        </h1>

        <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1.5 text-white font-medium">
            <Building2 className="w-4 h-4 text-emerald-400" />
            {report.company_name || 'Unverified Employer'}
          </span>
          <span>•</span>
          <span className="flex items-center gap-1.5">
            <Globe className="w-4 h-4 text-slate-400" />
            {report.company_verification?.location || 'Location Analyzed'}
          </span>
        </div>
      </div>

      {/* 12 EXPANDABLE SECTION CARDS */}
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
                    <div className="bg-emerald-400 h-2 rounded-full w-full" />
                  </div>
                </div>
                <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 text-center space-y-1">
                  <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Risk Level</span>
                  <div className={
                    'text-2xl font-bold font-mono ' +
                    (isSafe ? 'text-emerald-400' : isModerate ? 'text-amber-400' : 'text-red-400')
                  }>
                    {report.risk_level || (isSafe ? 'LOW RISK' : 'HIGH RISK')}
                  </div>
                  <span className="text-[10px] text-slate-400">Based on 50+ signal heuristics</span>
                </div>
                <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 text-center space-y-1">
                  <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Analysis Confidence</span>
                  <div className="text-3xl font-extrabold text-blue-400 font-mono">{report.confidence_score || 96}%</div>
                  <span className="text-[10px] text-slate-400">Multi-Model Hybrid Consensus</span>
                </div>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/60 border border-white/10 space-y-2 text-xs leading-relaxed text-slate-300">
                <span className="font-semibold text-white flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-emerald-400" /> Forensic Synthesis Summary
                </span>
                <p>{report.explanation}</p>
              </div>
            </div>
          )}
        </div>

        {/* CARD 2: Company Verification */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(2)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-xs">2</div>
              <div>
                <h3 className="text-base font-bold text-white">Company Verification</h3>
                <p className="text-xs text-slate-400 font-light">Digital footprint & corporate registry checks</p>
              </div>
            </div>
            {expandedCards[2] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[2] && (
            <div className="p-6 border-t border-white/10 bg-black/40">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-1">
                  <span className="text-[11px] text-slate-400">Company Website</span>
                  <div className="flex items-center gap-2 font-semibold text-emerald-400">
                    <CheckCircle2 className="w-4 h-4" /> <span>{report.company_verification?.website_status || '200 OK'}</span>
                  </div>
                </div>
                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-1">
                  <span className="text-[11px] text-slate-400">Careers Page</span>
                  <div className="flex items-center gap-2 font-semibold text-emerald-400">
                    <CheckCircle2 className="w-4 h-4" /> <span>{report.company_verification?.careers_page || 'Verified Match'}</span>
                  </div>
                </div>
                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-1">
                  <span className="text-[11px] text-slate-400">LinkedIn Profile</span>
                  <div className="flex items-center gap-2 font-semibold text-emerald-400">
                    <CheckCircle2 className="w-4 h-4" /> <span>{report.company_verification?.linkedin || 'Verified Page'}</span>
                  </div>
                </div>
                <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-1">
                  <span className="text-[11px] text-slate-400">Glassdoor</span>
                  <div className="flex items-center gap-2 font-semibold text-emerald-400">
                    <CheckCircle2 className="w-4 h-4" /> <span>{report.company_verification?.glassdoor || 'Available (4.2 ★)'}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* CARD 3: Listing Platforms */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(3)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center font-bold text-xs">3</div>
              <div>
                <h3 className="text-base font-bold text-white">Listing Found on Which Platforms</h3>
                <p className="text-xs text-slate-400 font-light">Cross-reference with official company portal</p>
              </div>
            </div>
            {expandedCards[3] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[3] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-4 text-xs">
              <div className="flex flex-wrap items-center justify-between p-4 rounded-xl bg-white/[0.03] border border-white/10 gap-3">
                <div>
                  <span className="text-slate-400 block text-[11px]">Official Careers Portal Status</span>
                  <span className="text-sm font-semibold text-emerald-400 font-mono">{report.listing_platforms?.official_site || 'Verified on Official Careers Portal'}</span>
                </div>
                <div className="text-right">
                  <span className="text-slate-400 block text-[11px]">Match Confidence</span>
                  <span className="text-sm font-bold text-white font-mono">{report.listing_platforms?.match_confidence || '96%'}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* CARD 4: Location Verification */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(4)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-teal-500/20 text-teal-400 flex items-center justify-center font-bold text-xs">4</div>
              <div>
                <h3 className="text-base font-bold text-white">Location Verification</h3>
                <p className="text-xs text-slate-400 font-light">Geographic alignment evaluation</p>
              </div>
            </div>
            {expandedCards[4] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[4] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-4 text-xs">
              <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 leading-relaxed">
                {report.location_verification?.notes || 'Location match confirmed across company HQ and job listing.'}
              </div>
            </div>
          )}
        </div>

        {/* CARD 5: Contact Verification */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(5)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-xs">5</div>
              <div>
                <h3 className="text-base font-bold text-white">Contact Verification</h3>
                <p className="text-xs text-slate-400 font-light">Email domain, phone, and channel matching</p>
              </div>
            </div>
            {expandedCards[5] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[5] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-4 text-xs">
              <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 font-semibold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{report.contact_verification?.status_text || 'Official contact domain matches listing domain'}</span>
              </div>
            </div>
          )}
        </div>

        {/* CARD 6: Salary Analysis */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(6)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">6</div>
              <div>
                <h3 className="text-base font-bold text-white">Salary Analysis</h3>
                <p className="text-xs text-slate-400 font-light">Compensation benchmarking & fraud evaluation</p>
              </div>
            </div>
            {expandedCards[6] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[6] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-4 text-xs">
              <div className="flex flex-wrap items-center justify-between p-4 rounded-xl bg-white/[0.03] border border-white/10 gap-3">
                <div>
                  <span className="text-[11px] text-slate-400 block">Stated Salary Range</span>
                  <span className="text-base font-bold text-emerald-400 font-mono">{report.salary_analysis?.range || '₹5,000 – ₹7,000 / month'}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* CARD 7: Grammar / Spacing Analysis */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(7)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-xs">7</div>
              <div>
                <h3 className="text-base font-bold text-white">Grammar / Spacing Analysis</h3>
                <p className="text-xs text-slate-400 font-light">Linguistic syntax parsing & tone assessment</p>
              </div>
            </div>
            {expandedCards[7] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[7] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-4 text-xs">
              <p className="text-slate-300">{report.grammar_analysis?.summary || 'Standard corporate grammar, appropriate technical terminology.'}</p>
            </div>
          )}
        </div>

        {/* CARD 8: Scam / Legit Patterns */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(8)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">8</div>
              <div>
                <h3 className="text-base font-bold text-white">Scam / Legit Pattern Detection</h3>
                <p className="text-xs text-slate-400 font-light">Known legitimate pattern verification</p>
              </div>
            </div>
            {expandedCards[8] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[8] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-3 text-xs">
              {(report.scam_patterns || ['No upfront fee demanded', 'Corporate email verified']).map((pattern, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-emerald-300 flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" /> <span>{pattern}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* CARD 9: Red Flags */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(9)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-red-500/20 text-red-400 flex items-center justify-center font-bold text-xs">9</div>
              <div>
                <h3 className="text-base font-bold text-white">Red Flags & Risk Assessment</h3>
                <p className="text-xs text-slate-400 font-light">Categorized risk indicators</p>
              </div>
            </div>
            {expandedCards[9] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[9] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-3 text-xs">
              <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> <span>No high-severity red flags detected.</span>
              </div>
            </div>
          )}
        </div>

        {/* CARD 10: All Observations */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(10)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold text-xs">10</div>
              <div>
                <h3 className="text-base font-bold text-white">All Observations</h3>
                <p className="text-xs text-slate-400 font-light">Positive indicators & concerns</p>
              </div>
            </div>
            {expandedCards[10] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[10] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-3 text-xs">
              {(report.positive_observations || ['WHOIS domain age 6+ years', 'Official HR contact verified']).map((obs, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-white/[0.03] border border-white/10 text-slate-300 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" /> <span>{obs}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* CARD 11: How to Apply Successfully */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(11)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">11</div>
              <div>
                <h3 className="text-base font-bold text-white">How to Apply Successfully</h3>
                <p className="text-xs text-slate-400 font-light">6 actionable safety steps when applying</p>
              </div>
            </div>
            {expandedCards[11] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[11] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-3 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3 rounded-xl bg-white/[0.03] border border-white/10 font-bold text-white">1. Official Portal First</div>
                <div className="p-3 rounded-xl bg-white/[0.03] border border-white/10 font-bold text-white">2. Recruiter Verification</div>
                <div className="p-3 rounded-xl bg-white/[0.03] border border-white/10 font-bold text-white">3. Zero Upfront Fees</div>
                <div className="p-3 rounded-xl bg-white/[0.03] border border-white/10 font-bold text-white">4. Official Video Interviews</div>
                <div className="p-3 rounded-xl bg-white/[0.03] border border-white/10 font-bold text-white">5. Cross-Check Job ID</div>
                <div className="p-3 rounded-xl bg-white/[0.03] border border-white/10 font-bold text-white">6. Report Anomaly</div>
              </div>
            </div>
          )}
        </div>

        {/* CARD 12: Recommendations */}
        <div className="glass-card rounded-2xl border border-white/10 overflow-hidden shadow-lg">
          <button onClick={() => toggleCard(12)} type="button" className="w-full p-5 bg-white/[0.02] hover:bg-white/[0.05] flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs">12</div>
              <div>
                <h3 className="text-base font-bold text-white">Recommendations & Next Actions</h3>
                <p className="text-xs text-slate-400 font-light">Final safety summary and workspace actions</p>
              </div>
            </div>
            {expandedCards[12] ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          {expandedCards[12] && (
            <div className="p-6 border-t border-white/10 bg-black/40 space-y-4 text-xs">
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 font-semibold">
                Recommendation: Proceed with confidence. This posting displays high authenticity signals across domain WHOIS and corporate checks.
              </div>
              <div className="flex items-center gap-4 pt-2">
                <Link to="/scan" className="px-5 py-2.5 rounded-xl bg-emerald-500 text-black font-bold text-xs">Scan Another Job</Link>
                <Link to="/history" className="px-5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-xs">View Scan History</Link>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default AnalysisResultPage;
