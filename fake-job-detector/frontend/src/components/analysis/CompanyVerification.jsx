import React from 'react';
import { Building2, CheckCircle2, AlertTriangle, XCircle, Globe, Calendar, Mail, Linkedin } from 'lucide-react';

export const CompanyVerification = ({ verification, companyName }) => {
  if (!verification) return null;

  const {
    status = 'unverified',
    domain_checked = 'N/A',
    whois_age_days = 0,
    mx_record_valid = false,
    linkedin_match = false,
    notes = '',
  } = verification;

  const getStatusBadge = () => {
    switch (status) {
      case 'verified':
        return {
          label: 'Verified Corporate Entity',
          icon: CheckCircle2,
          class: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
        };
      case 'warning':
        return {
          label: 'Domain Discrepancy / Caution',
          icon: AlertTriangle,
          class: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
        };
      case 'unverified':
      default:
        return {
          label: 'Unverified / High Impersonation Risk',
          icon: XCircle,
          class: 'bg-red-500/10 text-red-400 border-red-500/30',
        };
    }
  };

  const statusMeta = getStatusBadge();
  const StatusIcon = statusMeta.icon;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h4 className="text-sm font-semibold text-white flex items-center gap-2">
          <Building2 className="w-4 h-4 text-blue-400" />
          <span>Entity & Domain Verification</span>
        </h4>
        <div className={`px-2.5 py-1 rounded-full text-xs font-semibold border flex items-center gap-1.5 ${statusMeta.class}`}>
          <StatusIcon className="w-3.5 h-3.5" />
          <span>{statusMeta.label}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* Domain checked */}
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5 text-xs text-slate-300">
            <Globe className="w-4 h-4 text-slate-400" />
            <span>Target Domain</span>
          </div>
          <span className="text-xs font-mono font-medium text-white truncate max-w-[150px]">{domain_checked}</span>
        </div>

        {/* WHOIS age */}
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5 text-xs text-slate-300">
            <Calendar className="w-4 h-4 text-slate-400" />
            <span>Domain Age</span>
          </div>
          <span className={`text-xs font-mono font-medium ${whois_age_days < 90 ? 'text-red-400' : 'text-emerald-400'}`}>
            {whois_age_days > 0 ? `${whois_age_days} days` : 'Unregistered'}
          </span>
        </div>

        {/* MX Mail Records */}
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5 text-xs text-slate-300">
            <Mail className="w-4 h-4 text-slate-400" />
            <span>MX Mail Security</span>
          </div>
          <span className={`text-xs font-medium ${mx_record_valid ? 'text-emerald-400' : 'text-red-400'}`}>
            {mx_record_valid ? 'Valid SPF/DKIM' : 'Missing / Invalid'}
          </span>
        </div>

        {/* LinkedIn Match */}
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5 text-xs text-slate-300">
            <Linkedin className="w-4 h-4 text-slate-400" />
            <span>Corporate Org Link</span>
          </div>
          <span className={`text-xs font-medium ${linkedin_match ? 'text-emerald-400' : 'text-amber-400'}`}>
            {linkedin_match ? 'Cross-Matched' : 'Unconfirmed'}
          </span>
        </div>
      </div>

      {notes && (
        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs text-slate-400 leading-relaxed font-mono">
          <span className="text-slate-200 font-semibold">Diagnostic Notes: </span>
          {notes}
        </div>
      )}
    </div>
  );
};

export default CompanyVerification;
