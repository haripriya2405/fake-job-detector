import React from 'react';
import { Quote, Search, ShieldAlert, FileText, Image as ImageIcon, Globe } from 'lucide-react';

export const EvidenceViewer = ({ evidenceSnippets = [], rawContent = '' }) => {
  if (!evidenceSnippets || evidenceSnippets.length === 0) {
    return (
      <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 text-xs text-slate-400 text-center">
        No severe risk spans detected in the analyzed content.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-white flex items-center gap-2">
          <Quote className="w-4 h-4 text-orange-400" />
          <span>Extracted Forensic Evidence Snippets</span>
        </h4>
        <span className="text-xs text-slate-400 font-mono">{evidenceSnippets.length} Flagged Spans</span>
      </div>

      <div className="space-y-2.5">
        {evidenceSnippets.map((snippet, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-xl bg-slate-900/90 border border-orange-500/20 hover:border-orange-500/40 transition-colors space-y-2"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-orange-500/10 text-orange-400 border border-orange-500/20">
                  {snippet.type || 'Suspicious Pattern'}
                </span>
                {snippet.page_number && (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-blue-500/10 text-blue-300 border border-blue-500/20">
                    PDF Page {snippet.page_number}
                  </span>
                )}
                {snippet.confidence && (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                    OCR Conf: {Math.round(snippet.confidence * 100)}%
                  </span>
                )}
              </div>

              {snippet.risk_weight && (
                <span className="text-[11px] font-mono font-bold text-red-400">
                  {snippet.risk_weight}
                </span>
              )}
            </div>

            <blockquote className="text-xs text-slate-200 border-l-2 border-orange-500 pl-3 py-1 font-mono italic leading-relaxed bg-slate-950/40 rounded-r">
              "{snippet.quote}"
            </blockquote>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EvidenceViewer;
