import React from 'react';
import { Textarea, Input } from '../ui/Input';
import { Sparkles, Trash2, FileSignature } from 'lucide-react';

export const TextInputTab = ({
  jobText,
  setJobText,
  jobTitle,
  setJobTitle,
  companyName,
  setCompanyName,
  onClear,
}) => {
  return (
    <div className="space-y-4">
      {/* Optional Metadata Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Input
          label="Job Title (Optional)"
          placeholder="e.g. Remote Data Entry / Software Engineer"
          value={jobTitle}
          onChange={(e) => setJobTitle(e.target.value)}
        />
        <Input
          label="Company Name (Optional)"
          placeholder="e.g. Acme Corp / Apex Global"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
        />
      </div>

      {/* Main Job Description Text Area */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
            Raw Job Posting / Offer Message / Email Body
          </label>
          <div className="flex items-center gap-3">
            {jobText && (
              <button
                type="button"
                onClick={onClear}
                className="text-xs text-slate-400 hover:text-red-400 flex items-center gap-1 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Clear
              </button>
            )}
            <span className="text-xs font-mono text-slate-500">
              {jobText.length} characters
            </span>
          </div>
        </div>

        <textarea
          rows={8}
          value={jobText}
          onChange={(e) => setJobText(e.target.value)}
          placeholder="Paste the full job description, WhatsApp message, email offer letter, or recruitment pitch here..."
          className="w-full rounded-2xl bg-slate-900/90 border border-slate-800 focus:border-blue-500 text-slate-100 placeholder-slate-500 text-sm p-4 transition-colors focus:outline-none focus:ring-1 focus:ring-blue-500/50 leading-relaxed font-sans"
        />
      </div>
    </div>
  );
};

export default TextInputTab;
