import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  FileText,
  Link as LinkIcon,
  Image as ImageIcon,
  ArrowRight,
  ShieldCheck,
  Lock,
  Upload,
  X,
  Sparkles,
} from 'lucide-react';
import { analysisService } from '../../services/analysisService';
import { useToast } from '../../hooks/useToast';

const SCAN_STAGES = [
  'Scanning...',
  'Extracting company...',
  'Checking domain...',
  'Checking careers page...',
  'Checking recruiter...',
  'Benchmarking salary...',
  'Checking threat intelligence...',
  'Generating verdict...',
];

export const HeroScannerCard = ({ onSampleClick }) => {
  const navigate = useNavigate();
  const { error, success } = useToast();

  const [activeTab, setActiveTab] = useState('text'); // 'text' | 'url' | 'file'
  const [jobText, setJobText] = useState('');
  const [jobUrl, setJobUrl] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [currentStageIdx, setCurrentStageIdx] = useState(0);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        error('File size exceeds 10 MB limit.');
        return;
      }
      setSelectedFile(file);
      if (file.type.startsWith('image/')) {
        setFilePreview(URL.createObjectURL(file));
      } else {
        setFilePreview(null);
      }
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (filePreview) {
      URL.revokeObjectURL(filePreview);
      setFilePreview(null);
    }
  };

  const handleQuickLoad = () => {
    setJobText(
      "URGENT HIRING: Remote Data Entry & Crypto Processing Assistant. Salary: $65/hr, 10-20 hrs/week. No experience required. We will send you a $2,500 cashier check to purchase home-office equipment from our accredited vendor. To start immediately, send your resume to apexcareers.hr@gmail.com and message hiring manager on Telegram (@ApexRecruiter_David)."
    );
    setJobTitle("Remote Data Entry Assistant");
    setCompanyName("Apex Global Logistics");
    success("Loaded high-risk sample job description.");
  };

  const handleScan = async (e) => {
    e.preventDefault();

    if (activeTab === 'text') {
      if (!jobText.trim() || jobText.trim().length < 20) {
        error('Please enter at least 20 characters of job posting text to analyze.');
        return;
      }
    } else if (activeTab === 'url') {
      if (!jobUrl.trim() || !jobUrl.includes('.')) {
        error('Please enter a valid job URL (e.g. https://company.com/jobs/dev).');
        return;
      }
    } else if (activeTab === 'file') {
      if (!selectedFile) {
        error('Please select an image screenshot or PDF offer letter to upload.');
        return;
      }
    }

    setIsScanning(true);
    setCurrentStageIdx(0);

    const stageInterval = setInterval(() => {
      setCurrentStageIdx((prev) => (prev < SCAN_STAGES.length - 1 ? prev + 1 : prev));
    }, 280);

    try {
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
        const fileType = selectedFile.type.includes('pdf') ? 'pdf' : 'image';
        report = await analysisService.analyzeUpload(selectedFile, fileType, {
          job_title: jobTitle || selectedFile.name,
          company_name: companyName || undefined,
        });
      }

      clearInterval(stageInterval);
      success('Scan complete. Verdict ready.');
      navigate(`/analysis/${report.id}`, { state: { report } });
    } catch (err) {
      clearInterval(stageInterval);
      error(err.message || 'Scan failed. Please check the input and try again.');
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="w-full relative">
      {/* Subtle emerald spotlight blur behind card matching reference */}
      <div
        className="pointer-events-none absolute -inset-1 rounded-[1.8rem] bg-emerald-500/[0.08] blur-3xl opacity-90"
        aria-hidden="true"
      />

      <div className="relative rounded-2xl glass-modal p-5 sm:p-7 shadow-2xl border border-white/10 bg-[#07100c]/90">
        
        {/* Top Header with macOS window control dots matching Screenshot 1 */}
        <div className="mb-4 flex items-center justify-between gap-3">
          <p className="flex min-w-0 items-center gap-2 text-[11px] font-mono font-medium text-fog">
            <span className="inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" aria-hidden="true" />
            <span className="truncate tracking-wider">Paste text · URL · Screenshot</span>
          </p>
          <div className="flex shrink-0 items-center gap-1.5" aria-hidden="true">
            <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57] ring-1 ring-black/30" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e] ring-1 ring-black/30" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#28c840] ring-1 ring-black/30" />
          </div>
        </div>

        {/* Form Container */}
        <form onSubmit={handleScan} className="space-y-3.5">
          
          {/* Tab Switcher matching Screenshot 1 */}
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
              <span>Paste text</span>
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
              <span>URL</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('file')}
              className={`flex-1 min-w-0 flex items-center justify-center gap-1.5 rounded-full px-3 py-2 text-xs font-medium transition-all ${
                activeTab === 'file'
                  ? 'bg-white/10 text-frost shadow-hairline-inset border border-white/15'
                  : 'text-fog hover:text-frost'
              }`}
            >
              <ImageIcon className="w-3.5 h-3.5" />
              <span>Screenshot</span>
            </button>
          </div>

          {/* Mode 1: Paste Text */}
          {activeTab === 'text' && (
            <div className="space-y-2">
              <div className="relative">
                <textarea
                  id="landing-scan-input"
                  rows={5}
                  value={jobText}
                  onChange={(e) => setJobText(e.target.value)}
                  placeholder="Paste the full job description here..."
                  maxLength={10000}
                  className="w-full px-4 py-3.5 text-xs sm:text-sm rounded-xl border border-white/10 bg-black/50 text-frost placeholder-fog/60 resize-none focus:outline-none focus:ring-1 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all font-sans leading-relaxed"
                />
              </div>

              {/* Sample loader helper button */}
              <div className="flex items-center justify-between text-[11px] px-1 text-fog">
                <span className="font-mono text-[10px]">{jobText.length.toLocaleString()} / 10,000</span>
                <button
                  type="button"
                  onClick={handleQuickLoad}
                  className="text-emerald-400 hover:text-emerald-300 transition-colors inline-flex items-center gap-1 font-medium"
                >
                  <Sparkles className="w-3 h-3" />
                  Load sample scam text
                </button>
              </div>
            </div>
          )}

          {/* Mode 2: URL Input */}
          {activeTab === 'url' && (
            <div className="space-y-3 py-1">
              <div className="space-y-1.5">
                <label className="block text-xs font-medium text-mist">Job Posting URL</label>
                <input
                  type="url"
                  value={jobUrl}
                  onChange={(e) => setJobUrl(e.target.value)}
                  placeholder="https://company.com/jobs/software-engineer"
                  className="w-full px-4 py-3 text-xs sm:text-sm rounded-xl border border-white/10 bg-black/50 text-frost placeholder-fog/60 focus:outline-none focus:ring-1 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all font-mono"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="Job Title (optional)"
                  className="w-full px-3.5 py-2 text-xs rounded-xl border border-white/10 bg-black/40 text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/40"
                />
                <input
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="Company Name (optional)"
                  className="w-full px-3.5 py-2 text-xs rounded-xl border border-white/10 bg-black/40 text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/40"
                />
              </div>

              <p className="text-[11px] text-fog leading-relaxed font-light">
                SSRF-protected engine safely extracts visible job data and cross-checks official DNS/RDAP records.
              </p>
            </div>
          )}

          {/* Mode 3: Screenshot Upload */}
          {activeTab === 'file' && (
            <div className="space-y-3 py-1">
              {!selectedFile ? (
                <label className="flex flex-col items-center justify-center border-2 border-dashed border-white/15 hover:border-emerald-500/40 rounded-2xl p-6 bg-black/40 hover:bg-white/[0.02] cursor-pointer transition-all">
                  <Upload className="w-7 h-7 text-emerald-400 mb-2 opacity-80" />
                  <span className="text-xs font-semibold text-frost">Upload screenshot or offer letter</span>
                  <span className="text-[11px] text-fog mt-1">PNG, JPG, WEBP, or PDF (up to 10 MB)</span>
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/webp,application/pdf"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
              ) : (
                <div className="p-4 rounded-xl border border-white/10 bg-black/40 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 min-w-0">
                      <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                        {selectedFile.type.includes('pdf') ? <FileText className="w-4 h-4" /> : <ImageIcon className="w-4 h-4" />}
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs font-medium text-frost truncate">{selectedFile.name}</p>
                        <p className="text-[10px] text-fog">{(selectedFile.size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={handleRemoveFile}
                      className="p-1 text-fog hover:text-danger-bright transition-colors rounded-lg hover:bg-white/5"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  {filePreview && (
                    <div className="max-h-36 overflow-hidden rounded-lg border border-white/10">
                      <img src={filePreview} alt="Upload preview" className="w-full object-cover" />
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Large Solid Emerald CTA Button */}
          <div className="relative pt-1">
            <button
              type="submit"
              disabled={isScanning}
              className="relative w-full inline-flex items-center justify-center gap-2 rounded-full px-6 py-3.5 sm:py-4 text-sm sm:text-base font-semibold text-white bg-emerald-500 hover:bg-emerald-400 active:bg-emerald-600 shadow-emerald-button hover:shadow-emerald-glow transition-all duration-200 disabled:opacity-75 disabled:cursor-wait"
            >
              {isScanning ? (
                <span className="inline-flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span className="font-mono text-xs sm:text-sm">{SCAN_STAGES[currentStageIdx]}</span>
                </span>
              ) : (
                <>
                  <span>Scan Now</span>
                  <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5 transition-transform group-hover:translate-x-1" />
                </>
              )}
            </button>
          </div>
        </form>

        {/* Privacy Trust Row matching Screenshot 1 */}
        <div className="mt-4 flex flex-wrap items-center justify-center gap-x-2.5 gap-y-1 text-[11px] text-fog">
          <span className="flex items-center gap-1 text-emerald-400 font-light">
            <Lock className="h-3 w-3" />
            <span>Anonymous scan</span>
          </span>
          <span className="text-white/20">·</span>
          <span>Names redacted</span>
          <span className="text-white/20">·</span>
          <span>IP not stored</span>
          <span className="text-white/20">·</span>
          <span>Never sold</span>
        </div>

        {/* Compact Example Result Preview Card matching Screenshot 1 */}
        <div
          className="mt-4 rounded-xl bg-black/40 border border-white/10 shadow-hairline-inset p-4 transition-all cursor-pointer hover:border-red-500/40"
          onClick={() => {
            if (onSampleClick) onSampleClick('risky');
            else navigate('/analysis/sample-risky');
          }}
          aria-label="Example scan result preview"
        >
          <div className="flex items-start justify-between gap-2 mb-2.5">
            <div className="flex items-center gap-2 min-w-0">
              <span className="flex-shrink-0 h-2 w-2 rounded-full bg-red-500 ring-2 ring-red-500/20" aria-hidden="true" />
              <span className="text-xs font-medium text-frost/90 truncate font-mono">stempar-sciences.com · Data Scientist</span>
            </div>
            <span className="flex-shrink-0 inline-flex items-center gap-1.5 rounded-full bg-red-500/15 border border-red-500/30 px-2.5 py-0.5 tabular-nums">
              <span className="text-[11px] font-mono font-bold text-red-400">0 / 100</span>
              <span className="text-[9px] font-mono font-bold uppercase tracking-wider text-red-400/90 border-l border-red-500/30 pl-1.5">
                MAX RISK
              </span>
            </span>
          </div>

          <ul className="space-y-1 text-[11px] text-fog font-light">
            <li className="flex items-center gap-2">
              <span className="h-1 w-1 rounded-full bg-red-500/70 shrink-0" />
              Job not found on official careers page
            </li>
            <li className="flex items-center gap-2">
              <span className="h-1 w-1 rounded-full bg-red-500/70 shrink-0" />
              Task scam pattern — upfront work for pay
            </li>
            <li className="flex items-center gap-2">
              <span className="h-1 w-1 rounded-full bg-red-500/70 shrink-0" />
              Scamdoc trust score: 1%
            </li>
          </ul>

          <p className="mt-2.5 text-[10px] text-fog/70 font-light">
            Example result — real scan completed in 47 sec
          </p>
        </div>

      </div>

      {/* Bottom Link matching Screenshot 1 */}
      <p className="mt-4 text-center text-xs text-fog font-light">
        Want the full tool?{' '}
        <Link
          to="/analyze"
          className="text-emerald-400 hover:text-emerald-300 underline underline-offset-2 transition-colors"
        >
          Open the dedicated job scam checker →
        </Link>
      </p>
    </div>
  );
};

export default HeroScannerCard;
