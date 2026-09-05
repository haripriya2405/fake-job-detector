import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  ShieldAlert, 
  AlertTriangle, 
  CheckCircle2, 
  Copy, 
  Check, 
  Share2, 
  Printer, 
  ExternalLink, 
  Building2, 
  Calendar, 
  Fingerprint, 
  Key, 
  Lock, 
  ArrowLeft,
  Sparkles,
  Download
} from 'lucide-react';
import { certificateService } from '../services/certificateService';
import { useToast } from '../context/ToastContext';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

export function JobVerificationCertificatePage() {
  const { id } = useParams();
  const { addToast } = useToast();
  
  const [cert, setCert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copiedType, setCopiedType] = useState(null);

  useEffect(() => {
    async function fetchCert() {
      try {
        setLoading(true);
        const data = await certificateService.getCertificate(id);
        setCert(data);
      } catch (err) {
        addToast(err.message || 'Verification certificate not found or invalid.', 'error');
      } finally {
        setLoading(false);
      }
    }
    if (id) {
      fetchCert();
    }
  }, [id, addToast]);

  const handleCopy = (text, type) => {
    navigator.clipboard.writeText(text);
    setCopiedType(type);
    addToast('Copied to clipboard!', 'success');
    setTimeout(() => setCopiedType(null), 2000);
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
        <LoadingSpinner text="Validating cryptographic certificate signature..." size="lg" />
      </div>
    );
  }

  if (!cert) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center space-y-4 shadow-2xl">
          <ShieldAlert className="w-16 h-16 text-rose-500 mx-auto" />
          <h2 className="text-2xl font-bold text-white">Certificate Not Found</h2>
          <p className="text-sm text-slate-400">
            The verification certificate '{id}' could not be validated against our cryptographically signed registry.
          </p>
          <Link
            to="/analyze"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-sm font-semibold transition-all shadow-md mt-2"
          >
            Scan a New Job
          </Link>
        </div>
      </div>
    );
  }

  const isSafe = cert.legitimacy_verdict === 'VERIFIED_SAFE';
  const isCaution = cert.legitimacy_verdict === 'CAUTION_ADVISED';

  const themeConfig = isSafe
    ? {
        borderGradient: 'from-emerald-500/50 via-teal-500/30 to-emerald-600/60',
        badgeBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
        sealColor: 'text-emerald-400',
        sealBg: 'bg-emerald-500/10 border-emerald-500/30',
        scoreColor: 'text-emerald-400',
        glowColor: 'bg-emerald-500/15',
        verdictTitle: 'VERIFIED LEGITIMATE POSTING',
        sealLabel: 'AUTHENTIC & SAFE',
      }
    : isCaution
    ? {
        borderGradient: 'from-amber-500/50 via-yellow-500/30 to-amber-600/60',
        badgeBg: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
        sealColor: 'text-amber-400',
        sealBg: 'bg-amber-500/10 border-amber-500/30',
        scoreColor: 'text-amber-400',
        glowColor: 'bg-amber-500/15',
        verdictTitle: 'CAUTION ADVISED — REVIEWS RECOMMENDED',
        sealLabel: 'CAUTION AUDITED',
      }
    : {
        borderGradient: 'from-rose-500/50 via-red-500/30 to-rose-600/60',
        badgeBg: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
        sealColor: 'text-rose-400',
        sealBg: 'bg-rose-500/10 border-rose-500/30',
        scoreColor: 'text-rose-400',
        glowColor: 'bg-rose-500/15',
        verdictTitle: 'SUSPICIOUS POSTING — FRAUD WARNING',
        sealLabel: 'HIGH RISK THREAT',
      };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Top Back Navigation Bar */}
        <div className="flex items-center justify-between no-print">
          <Link
            to={`/analysis/${cert.analysis_id}`}
            className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Full Analysis Report
          </Link>
          <div className="flex items-center gap-3">
            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 text-xs font-medium transition-all shadow-sm"
            >
              <Printer className="w-4 h-4" /> Print / Save PDF
            </button>
            <Link
              to="/analyze"
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold transition-all shadow-md"
            >
              <Sparkles className="w-4 h-4" /> Scan Another Job
            </Link>
          </div>
        </div>

        {/* Certificate Card */}
        <div className="relative rounded-3xl p-[1.5px] bg-gradient-to-b shadow-2xl overflow-hidden transition-all duration-300">
          <div className={`absolute inset-0 bg-gradient-to-r ${themeConfig.borderGradient} opacity-90`} />
          
          <div className="relative bg-[#070b12] rounded-[23px] p-8 sm:p-12 overflow-hidden">
            {/* Background Ambient Glow */}
            <div className={`absolute -top-24 -right-24 w-96 h-96 ${themeConfig.glowColor} rounded-full blur-3xl pointer-events-none`} />
            <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

            {/* Certificate Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 pb-8 border-b border-slate-800/80">
              <div className="flex items-center gap-4">
                <div className={`w-14 h-14 rounded-2xl ${themeConfig.sealBg} flex items-center justify-center shadow-inner`}>
                  {isSafe ? (
                    <ShieldCheck className={`w-8 h-8 ${themeConfig.sealColor}`} />
                  ) : (
                    <ShieldAlert className={`w-8 h-8 ${themeConfig.sealColor}`} />
                  )}
                </div>
                <div>
                  <div className="text-[11px] font-bold text-cyan-400 tracking-widest uppercase font-mono">
                    JobScamScore Official Trust Registry
                  </div>
                  <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white mt-0.5">
                    Security Audit Certificate
                  </h1>
                </div>
              </div>

              {/* Certificate Identifier Badge */}
              <div className="text-left sm:text-right font-mono">
                <div className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Certificate ID</div>
                <div className="text-base font-bold text-white tracking-wide bg-slate-900/90 px-3 py-1 rounded-lg border border-slate-700/80 inline-block mt-1">
                  {cert.certificate_id}
                </div>
              </div>
            </div>

            {/* Position & Employer Body */}
            <div className="py-8 space-y-6">
              <div>
                <div className="text-xs uppercase tracking-widest text-slate-400 font-semibold mb-1">
                  Verified Job Position
                </div>
                <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
                  {cert.job_title}
                </h2>
                <div className="flex flex-wrap items-center gap-4 mt-2 text-sm text-slate-300">
                  <div className="flex items-center gap-1.5 font-medium">
                    <Building2 className="w-4 h-4 text-slate-400" />
                    <span>Company: <strong className="text-white">{cert.company_name}</strong></span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-slate-400">
                    <Calendar className="w-3.5 h-3.5 text-slate-500" />
                    <span>Audited: {new Date(cert.analyzed_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                  </div>
                </div>
              </div>

              {/* Verdict Banner Card */}
              <div className={`p-6 rounded-2xl border ${themeConfig.badgeBg} flex flex-col sm:flex-row sm:items-center justify-between gap-6 backdrop-blur-md`}>
                <div className="space-y-1">
                  <div className="text-xs font-bold uppercase tracking-wider text-slate-300">Official Verdict</div>
                  <div className={`text-xl sm:text-2xl font-black ${themeConfig.scoreColor} tracking-tight`}>
                    {themeConfig.verdictTitle}
                  </div>
                  <p className="text-xs text-slate-300 max-w-xl leading-relaxed mt-2 font-sans">
                    {cert.summary}
                  </p>
                </div>

                {/* Score Dial / Pill */}
                <div className="text-center sm:text-right shrink-0 bg-slate-950/70 p-4 rounded-xl border border-slate-800">
                  <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest">
                    {isSafe ? 'Legitimacy Score' : 'Threat Risk Score'}
                  </div>
                  <div className={`text-3xl font-extrabold ${themeConfig.scoreColor} mt-0.5`}>
                    {isSafe ? `${100 - cert.risk_score}/100` : `${cert.risk_score}/100`}
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1 font-mono uppercase">
                    Risk Level: {cert.risk_level}
                  </div>
                </div>
              </div>

              {/* Key Indicators */}
              {cert.key_indicators && cert.key_indicators.length > 0 && (
                <div className="space-y-2">
                  <div className="text-xs uppercase font-bold text-slate-400 tracking-wider">
                    Audited Signals & Evidence
                  </div>
                  <div className="grid grid-cols-1 gap-2">
                    {cert.key_indicators.map((ind, idx) => (
                      <div key={idx} className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-950/50 border border-slate-800/80 text-xs text-slate-300">
                        {isSafe ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                        ) : (
                          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                        )}
                        <span>{ind}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Cryptographic Tamper-Evident Proof Block */}
              <div className="mt-8 p-5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-3 font-mono text-xs">
                <div className="flex items-center justify-between text-slate-400 font-sans">
                  <div className="flex items-center gap-2 font-bold text-xs text-slate-200">
                    <Lock className="w-4 h-4 text-cyan-400" />
                    Cryptographic Authenticity Guarantee
                  </div>
                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 font-mono">
                    <CheckCircle2 className="w-3 h-3" /> HMAC-SHA256 SIGNED
                  </span>
                </div>

                <div className="space-y-2 pt-1">
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase block">Content SHA-256 Fingerprint</span>
                    <span className="text-slate-300 break-all text-[11px] select-all bg-slate-900/90 p-1.5 rounded block border border-slate-800/80">
                      {cert.sha256_fingerprint}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase block">Digital Signature</span>
                    <span className="text-cyan-300 break-all text-[11px] select-all bg-slate-900/90 p-1.5 rounded block border border-slate-800/80">
                      {cert.digital_signature}
                    </span>
                  </div>
                </div>
              </div>

            </div>

            {/* Certificate Footer */}
            <div className="pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Issued by JobScamScore Verification Network &middot; Real-time ATS & Threat Engine</span>
              </div>
              <div className="font-mono text-[11px] text-slate-400">
                Verified: {new Date(cert.verified_at).toUTCString()}
              </div>
            </div>

          </div>
        </div>

        {/* Live Embed & Share Toolkit (Web Only) */}
        <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-xl space-y-6 no-print">
          <div className="flex items-center gap-2 font-bold text-white text-base">
            <Share2 className="w-5 h-5 text-cyan-400" />
            Share & Embed Trust Badges
          </div>
          <p className="text-xs text-slate-400 -mt-4">
            Showcase this verified job certificate on LinkedIn, personal portfolio sites, or job boards.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Live Badge Preview */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Live Dynamic Badge Preview</label>
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-center">
                <img 
                  src={certificateService.getBadgeSvgUrl(cert.certificate_id)} 
                  alt="JobScamScore Live Verification Badge" 
                  className="h-9 shadow-md"
                />
              </div>
              <div className="text-[11px] text-slate-500 text-center">
                Updates dynamically when checked across the network.
              </div>
            </div>

            {/* Direct Link Share */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Public Verification URL</label>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  readOnly
                  value={window.location.href}
                  className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-slate-300 select-all"
                />
                <button
                  onClick={() => handleCopy(window.location.href, 'url')}
                  className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5"
                >
                  {copiedType === 'url' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  Copy
                </button>
              </div>
            </div>

          </div>

          {/* Embed Code Snippets */}
          <div className="space-y-4 pt-2 border-t border-slate-800">
            {/* Markdown */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-300">Markdown Badge (GitHub / Profile README)</span>
                <button
                  onClick={() => handleCopy(cert.embed_badge_markdown, 'md')}
                  className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 text-[11px]"
                >
                  {copiedType === 'md' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  Copy Markdown
                </button>
              </div>
              <pre className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-[11px] font-mono text-slate-300 overflow-x-auto select-all">
                {cert.embed_badge_markdown}
              </pre>
            </div>

            {/* HTML */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-300">HTML Embed (Career Page / Website)</span>
                <button
                  onClick={() => handleCopy(cert.embed_badge_html, 'html')}
                  className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 text-[11px]"
                >
                  {copiedType === 'html' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  Copy HTML
                </button>
              </div>
              <pre className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-[11px] font-mono text-slate-300 overflow-x-auto select-all">
                {cert.embed_badge_html}
              </pre>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}

export default JobVerificationCertificatePage;
