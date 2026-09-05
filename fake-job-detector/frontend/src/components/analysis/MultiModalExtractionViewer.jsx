import React from 'react';
import { FileText, Image as ImageIcon, Globe, Cpu, CheckCircle2, AlertTriangle, Hash, FileCode, Layers } from 'lucide-react';

export const MultiModalExtractionViewer = ({ extraction, sourceType }) => {
  if (!extraction) return null;

  const {
    source_type = sourceType?.toUpperCase() || 'TEXT',
    extraction_method = 'direct',
    extraction_confidence = 1.0,
    original_filename = null,
    mime_type = null,
    file_size_bytes = null,
    page_count = null,
    content_hash = null,
    warnings = [],
    extracted_urls = [],
    extracted_emails = [],
    extracted_messaging_handles = [],
  } = extraction;

  const getSourceIcon = () => {
    switch (source_type.toLowerCase()) {
      case 'pdf':
        return FileText;
      case 'image':
        return ImageIcon;
      case 'url':
        return Globe;
      default:
        return FileCode;
    }
  };

  const Icon = getSourceIcon();
  const confidencePercent = Math.round(extraction_confidence * 100);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h4 className="text-sm font-semibold text-white flex items-center gap-2">
          <Cpu className="w-4 h-4 text-purple-400" />
          <span>Multi-Modal Extraction & Ingestion Telemetry</span>
        </h4>
        <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-purple-500/10 text-purple-300 border border-purple-500/20">
          {source_type} INGESTION
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {/* Method */}
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
          <div className="text-[11px] text-slate-400 font-medium flex items-center gap-1.5">
            <Icon className="w-3.5 h-3.5 text-blue-400" />
            <span>Extraction Method</span>
          </div>
          <p className="text-xs font-mono font-semibold text-white truncate uppercase">
            {extraction_method}
          </p>
        </div>

        {/* Confidence (especially for OCR) */}
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
          <div className="text-[11px] text-slate-400 font-medium flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Extraction Confidence</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  confidencePercent >= 80 ? 'bg-emerald-400' : confidencePercent >= 50 ? 'bg-amber-400' : 'bg-red-400'
                }`}
                style={{ width: `${confidencePercent}%` }}
              />
            </div>
            <span className="text-xs font-mono font-semibold text-emerald-300">
              {confidencePercent}%
            </span>
          </div>
        </div>

        {/* Page count / File Size */}
        {page_count ? (
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] text-slate-400 font-medium flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              <span>Parsed Pages</span>
            </div>
            <p className="text-xs font-mono font-semibold text-white">
              {page_count} {page_count === 1 ? 'Page' : 'Pages'}
            </p>
          </div>
        ) : file_size_bytes ? (
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] text-slate-400 font-medium flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-cyan-400" />
              <span>Payload Size</span>
            </div>
            <p className="text-xs font-mono font-semibold text-white">
              {(file_size_bytes / 1024).toFixed(1)} KB
            </p>
          </div>
        ) : (
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] text-slate-400 font-medium flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Sanitization Status</span>
            </div>
            <p className="text-xs font-mono font-semibold text-emerald-300">
              Validated & Cleaned
            </p>
          </div>
        )}
      </div>

      {/* Filename and Content Hash */}
      {(original_filename || content_hash) && (
        <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1 text-xs">
          {original_filename && (
            <div className="flex items-center gap-2 text-slate-300">
              <span className="text-slate-500 font-mono text-[11px]">Filename:</span>
              <span className="font-mono text-white truncate">{original_filename}</span>
              {mime_type && <span className="text-slate-500 font-mono text-[10px]">({mime_type})</span>}
            </div>
          )}
          {content_hash && (
            <div className="flex items-center gap-2 text-slate-400 font-mono text-[11px] truncate">
              <Hash className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              <span className="text-slate-500">SHA-256:</span>
              <span className="text-slate-300 truncate">{content_hash}</span>
            </div>
          )}
        </div>
      )}

      {/* Warnings if any */}
      {warnings && warnings.length > 0 && (
        <div className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/20 text-xs text-amber-300 space-y-1">
          <div className="flex items-center gap-1.5 font-semibold">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span>Extraction Warnings</span>
          </div>
          <ul className="list-disc list-inside space-y-0.5 text-amber-200/90 text-[11px]">
            {warnings.map((w, idx) => (
              <li key={idx}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default MultiModalExtractionViewer;
