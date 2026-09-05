import React from 'react';
import { ShieldCheck, AlertTriangle, XCircle, CheckCircle2, Layers } from 'lucide-react';

export const SignalStack8Layer = ({ signals }) => {
  if (!signals) return null;

  const layersList = [
    signals.layer_1_company_authentication,
    signals.layer_2_careers_page_verification,
    signals.layer_3_recruiter_identity,
    signals.layer_4_salary_benchmarking,
    signals.layer_5_scam_pattern_detection,
    signals.layer_6_contact_validation,
    signals.layer_7_domain_ssl_intelligence,
    signals.layer_8_live_threat_intelligence,
  ].filter(Boolean);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'PASS':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3" />
            PASS
          </span>
        );
      case 'WARN':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <AlertTriangle className="w-3 h-3" />
            WARN
          </span>
        );
      case 'FAIL':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-red-500/15 text-red-400 border border-red-500/30">
            <XCircle className="w-3 h-3" />
            FAIL
          </span>
        );
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">8-Layer Signal Intelligence Stack</h3>
            <p className="text-[11px] text-slate-400">Parallel forensic analysis across 50+ threat checks</p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-xs font-mono font-bold text-emerald-400">{signals.checks_passed}</span>
          <span className="text-xs font-mono text-slate-500"> / {signals.checks_total} checks passed</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {layersList.map((layer) => (
          <div
            key={layer.layer_id}
            className={`p-3.5 rounded-xl border transition-colors ${
              layer.status === 'FAIL'
                ? 'bg-red-950/20 border-red-500/30'
                : layer.status === 'WARN'
                ? 'bg-amber-950/20 border-amber-500/30'
                : 'bg-black/30 border-white/10 hover:border-emerald-500/30'
            }`}
          >
            <div className="flex items-start justify-between gap-2 mb-1.5">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono font-bold text-slate-500">0{layer.layer_id}</span>
                <span className="text-xs font-semibold text-white">{layer.name}</span>
              </div>
              {getStatusBadge(layer.status)}
            </div>
            <p className="text-[11px] text-slate-400 font-light leading-relaxed mb-1">{layer.description}</p>
            <p className="text-[11px] font-medium text-slate-300 bg-white/5 rounded px-2 py-1 border border-white/5">
              {layer.detail}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
