import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  AlertTriangle,
  UploadCloud,
  CheckCircle2,
  Send,
  Building,
  Briefcase,
  Globe,
  FileText,
  Lock,
  ArrowLeft
} from 'lucide-react';
import { useToast } from '../hooks/useToast';

export const ReportScamPage = () => {
  const { addToast } = useToast();
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    jobTitle: '',
    companyName: '',
    scamType: 'Fake Recruiter',
    platform: 'LinkedIn',
    contactInfo: '',
    description: '',
    evidenceUrl: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.jobTitle || !formData.companyName || !formData.description) {
      addToast('Please fill in all required fields to submit a report.', 'error');
      return;
    }

    setSubmitted(true);
    addToast('Scam report submitted successfully! Thank you for protecting job seekers.', 'success');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-4">
      {/* Back Navigation */}
      <div className="flex items-center justify-between">
        <Link to="/scan" className="inline-flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Scam Scanner</span>
        </Link>
      </div>

      {/* Header Banner matching PDF Page 11 */}
      <div className="glass-card rounded-2xl p-6 sm:p-8 border border-red-500/30 bg-gradient-to-r from-red-950/40 via-black to-red-950/20 space-y-3 relative overflow-hidden shadow-2xl">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-red-500/20 border border-red-500/40 flex items-center justify-center text-red-400 shrink-0 shadow-lg">
            <ShieldAlert className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
              Report a Job Scam
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 font-light mt-1">
              Help protect job seekers by reporting fake job listings, fraudulent recruiters, or hiring scams.
            </p>
          </div>
        </div>
      </div>

      {/* Form or Confirmation */}
      {submitted ? (
        <div className="glass-card rounded-2xl p-8 border border-emerald-500/30 bg-emerald-950/20 text-center space-y-4 shadow-xl">
          <div className="w-14 h-14 rounded-full bg-emerald-500/20 border border-emerald-500/40 mx-auto flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-white">Scam Report Submitted</h2>
          <p className="text-xs sm:text-sm text-slate-300 max-w-md mx-auto leading-relaxed">
            Our intelligence engine and community moderators have received your report. Your contribution helps protect thousands of candidates from fraud.
          </p>
          <div className="pt-2">
            <button
              onClick={() => {
                setSubmitted(false);
                setFormData({
                  jobTitle: '',
                  companyName: '',
                  scamType: 'Fake Recruiter',
                  platform: 'LinkedIn',
                  contactInfo: '',
                  description: '',
                  evidenceUrl: ''
                });
              }}
              className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-semibold text-xs transition-all shadow-lg"
            >
              Report Another Scam
            </button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="glass-card rounded-2xl p-6 sm:p-8 border border-white/10 space-y-6 shadow-xl">
          
          {/* Security Banner */}
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3 text-xs text-amber-300">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <span className="leading-relaxed">
              <strong>Important Notice:</strong> Do not include sensitive personal info (such as your full credit card number or bank passwords) in your report. Focus on suspicious communication logs, recruiter contacts, and job links.
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {/* Job Title */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <Briefcase className="w-3.5 h-3.5 text-emerald-400" />
                <span>Job Title <span className="text-red-400">*</span></span>
              </label>
              <input
                type="text"
                name="jobTitle"
                required
                value={formData.jobTitle}
                onChange={handleChange}
                placeholder="e.g. Remote Data Entry Assistant"
                className="w-full px-4 py-2.5 rounded-xl bg-black/50 border border-white/15 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50"
              />
            </div>

            {/* Company Name */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <Building className="w-3.5 h-3.5 text-emerald-400" />
                <span>Company Name / Entity <span className="text-red-400">*</span></span>
              </label>
              <input
                type="text"
                name="companyName"
                required
                value={formData.companyName}
                onChange={handleChange}
                placeholder="e.g. Apex Global Solutions"
                className="w-full px-4 py-2.5 rounded-xl bg-black/50 border border-white/15 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50"
              />
            </div>

            {/* Scam Type */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <ShieldAlert className="w-3.5 h-3.5 text-red-400" />
                <span>Category of Fraud</span>
              </label>
              <select
                name="scamType"
                value={formData.scamType}
                onChange={handleChange}
                className="w-full px-4 py-2.5 rounded-xl bg-black/50 border border-white/15 text-xs text-white focus:outline-none focus:border-emerald-500/50"
              >
                <option value="Fake Recruiter">Imposter Recruiter / Fake HR</option>
                <option value="Fee Demand">Payment Required for Training/Equipment</option>
                <option value="Phishing">Phishing / Personal Identity Theft</option>
                <option value="Fake Interview">Telegram/WhatsApp Instant Interview</option>
                <option value="Unrealistic Pay">Unrealistic Compensation Scheme</option>
              </select>
            </div>

            {/* Platform / Source */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <Globe className="w-3.5 h-3.5 text-emerald-400" />
                <span>Platform / Channel Encountered</span>
              </label>
              <select
                name="platform"
                value={formData.platform}
                onChange={handleChange}
                className="w-full px-4 py-2.5 rounded-xl bg-black/50 border border-white/15 text-xs text-white focus:outline-none focus:border-emerald-500/50"
              >
                <option value="LinkedIn">LinkedIn</option>
                <option value="Indeed">Indeed</option>
                <option value="WhatsApp">WhatsApp / Telegram</option>
                <option value="Email">Unsolicited Email</option>
                <option value="Glassdoor">Glassdoor / ZipRecruiter</option>
                <option value="Other">Other Job Board / Social Media</option>
              </select>
            </div>
          </div>

          {/* Recruiter Contact Details */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-2">
              <FileText className="w-3.5 h-3.5 text-slate-400" />
              <span>Recruiter Email / Phone / Handle (Optional)</span>
            </label>
            <input
              type="text"
              name="contactInfo"
              value={formData.contactInfo}
              onChange={handleChange}
              placeholder="e.g. hr-hiring@apex-jobs-careers.com or +1 800..."
              className="w-full px-4 py-2.5 rounded-xl bg-black/50 border border-white/15 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50"
            />
          </div>

          {/* Scam Details */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-2">
              <FileText className="w-3.5 h-3.5 text-emerald-400" />
              <span>Detailed Explanation of Scam <span className="text-red-400">*</span></span>
            </label>
            <textarea
              name="description"
              required
              rows={4}
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe what happened: Did they demand money for background checks? Did they conduct an interview over chat? Were checks issued for laptop purchases?"
              className="w-full px-4 py-2.5 rounded-xl bg-black/50 border border-white/15 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 resize-y"
            />
          </div>

          {/* Link or Screenshot URL */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-2">
              <UploadCloud className="w-3.5 h-3.5 text-emerald-400" />
              <span>Job Posting URL or Evidence Link (Optional)</span>
            </label>
            <input
              type="url"
              name="evidenceUrl"
              value={formData.evidenceUrl}
              onChange={handleChange}
              placeholder="https://..."
              className="w-full px-4 py-2.5 rounded-xl bg-black/50 border border-white/15 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50"
            />
          </div>

          {/* Submit Button */}
          <div className="pt-4 flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
              <Lock className="w-3.5 h-3.5 text-emerald-400" />
              <span>Submissions are anonymously processed for threat detection.</span>
            </div>

            <button
              type="submit"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-red-600 hover:bg-red-500 text-white text-xs font-semibold shadow-lg shadow-red-950/50 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <Send className="w-4 h-4" />
              <span>Submit Scam Report</span>
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default ReportScamPage;
