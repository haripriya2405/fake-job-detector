import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, Send, CheckCircle2 } from 'lucide-react';
import { useToast } from '../hooks/useToast';

export const ReportScamPage = () => {
  const { success, error } = useToast();
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    jobTitle: '',
    companyName: '',
    description: '',
    scamType: '',
    location: '',
    jobUrl: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.jobTitle.trim() || !formData.description.trim() || !formData.scamType) {
      error('Please fill in all required fields marked with * to submit your report.');
      return;
    }

    setSubmitted(true);
    success('Scam report submitted successfully! Thank you for protecting the community.');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-2 select-none text-frost">
      
      {/* 1. Header Section matching Screenshot 1 */}
      <div className="space-y-4">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-2xl bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-500 shrink-0">
            <AlertTriangle className="w-6 h-6 text-red-500" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Report a scam
            </h1>
            <p className="text-sm text-slate-400 font-light mt-1">
              Help protect others by reporting job scams you've encountered
            </p>
          </div>
        </div>

        <p className="text-xs text-slate-400 leading-relaxed font-light">
          Your report will be reviewed and may appear in our{' '}
          <Link to="/alerts" className="text-emerald-400 font-medium hover:underline">
            scam alerts
          </Link>{' '}
          to help protect the community. We limit reports to 5 per hour to prevent spam.
        </p>
      </div>

      {/* 2. Form Card or Submitted Success Banner */}
      {submitted ? (
        <div className="p-8 sm:p-10 rounded-3xl bg-[#09110d] border border-emerald-500/30 text-center space-y-4 shadow-2xl">
          <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 mx-auto flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-8 h-8 text-emerald-400" />
          </div>
          <h2 className="text-2xl font-bold text-white">Scam Report Received</h2>
          <p className="text-xs sm:text-sm text-slate-300 max-w-lg mx-auto leading-relaxed font-light">
            Thank you for contributing to the community database. Your submission is being cross-checked against our threat intelligence feeds.
          </p>
          <div className="pt-2">
            <button
              onClick={() => {
                setSubmitted(false);
                setFormData({
                  jobTitle: '',
                  companyName: '',
                  description: '',
                  scamType: '',
                  location: '',
                  jobUrl: '',
                });
              }}
              className="px-6 py-3 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-white font-bold text-xs transition-all shadow-lg shadow-emerald-500/20"
            >
              Submit Another Report
            </button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="p-6 sm:p-8 rounded-3xl bg-[#09110d] border border-white/10 shadow-2xl space-y-6">
          
          {/* Field 1: Job Title */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-white block">
              Job title (as shown in the scam) <span className="text-emerald-400">*</span>
            </label>
            <input
              type="text"
              name="jobTitle"
              required
              value={formData.jobTitle}
              onChange={handleChange}
              placeholder="e.g. Delivery Operations Specialist"
              className="w-full px-4 py-3.5 rounded-xl bg-black/60 border border-white/10 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 transition-colors"
            />
          </div>

          {/* Field 2: Company Name */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-white block">
              Company name or scam description
            </label>
            <input
              type="text"
              name="companyName"
              value={formData.companyName}
              onChange={handleChange}
              placeholder="e.g. Fake logistics / reshipping scam"
              className="w-full px-4 py-3.5 rounded-xl bg-black/60 border border-white/10 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 transition-colors"
            />
          </div>

          {/* Field 3: What happened? */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-white block">
              What happened? (describe the scam) <span className="text-emerald-400">*</span>
            </label>
            <textarea
              name="description"
              required
              rows={5}
              maxLength={2000}
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe how you encountered this scam, what you were asked to do, etc."
              className="w-full px-4 py-3.5 rounded-xl bg-black/60 border border-white/10 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 transition-colors resize-y leading-relaxed font-sans"
            />
            <div className="text-[11px] font-mono text-slate-500">
              {formData.description.length}/2000
            </div>
          </div>

          {/* Field 4: Type of scam */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-white block">
              Type of scam <span className="text-emerald-400">*</span>
            </label>
            <select
              name="scamType"
              required
              value={formData.scamType}
              onChange={handleChange}
              className="w-full px-4 py-3.5 rounded-xl bg-black/60 border border-white/10 text-xs sm:text-sm text-white focus:outline-none focus:border-emerald-500/50 transition-colors"
            >
              <option value="" disabled>
                Select type...
              </option>
              <option value="Upfront Fee">Upfront Fee / Registration Demand</option>
              <option value="Task Scam">Task Scam / YouTube Like & Subscribe</option>
              <option value="Fake Check">Fake Check / Equipment Deposit</option>
              <option value="Telegram Interview">Telegram / WhatsApp Only Interview</option>
              <option value="Phishing">Identity Theft / Phishing Offer Letter</option>
              <option value="Reshipping">Reshipping / Package Handling</option>
              <option value="Other">Other / Unspecified Fraud</option>
            </select>
          </div>

          {/* Field 5: Location */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-white block">
              Location (if known)
            </label>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="e.g. Remote (US)"
              className="w-full px-4 py-3.5 rounded-xl bg-black/60 border border-white/10 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 transition-colors"
            />
          </div>

          {/* Field 6: Job Posting URL */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-white block">
              Job posting URL (if you have it)
            </label>
            <input
              type="url"
              name="jobUrl"
              value={formData.jobUrl}
              onChange={handleChange}
              placeholder="https://..."
              className="w-full px-4 py-3.5 rounded-xl bg-black/60 border border-white/10 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 transition-colors font-mono"
            />
          </div>

          {/* Submit Button matching Screenshot 2 */}
          <div className="pt-2">
            <button
              type="submit"
              className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-2xl bg-emerald-500 hover:bg-emerald-400 active:bg-emerald-600 text-white font-bold text-sm shadow-lg shadow-emerald-500/20 transition-all duration-200"
            >
              <Send className="w-4 h-4" />
              <span>Submit report</span>
            </button>
          </div>

        </form>
      )}

    </div>
  );
};

export default ReportScamPage;
