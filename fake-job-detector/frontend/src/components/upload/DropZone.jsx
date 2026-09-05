import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Image as ImageIcon, CheckCircle2, X, AlertCircle } from 'lucide-react';
import { formatFileSize } from '../../utils/formatters';

export const DropZone = ({ onFileSelected, acceptType = 'both', selectedFile, onRemoveFile }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const acceptedMimeTypes = acceptType === 'pdf' 
    ? '.pdf,application/pdf'
    : acceptType === 'image'
    ? 'image/png,image/jpeg,image/webp,image/jpg'
    : '.pdf,application/pdf,image/png,image/jpeg,image/webp,image/jpg';

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndProcessFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndProcessFile(e.target.files[0]);
    }
  };

  const validateAndProcessFile = (file) => {
    const isPdf = file.type === 'application/pdf' || file.name.endsWith('.pdf');
    const isImage = file.type.startsWith('image/');
    
    if (acceptType === 'pdf' && !isPdf) {
      alert('Please upload a valid PDF document.');
      return;
    }
    if (acceptType === 'image' && !isImage) {
      alert('Please upload a valid image file (PNG, JPG, WebP).');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      alert('File size exceeds 10MB limit.');
      return;
    }

    onFileSelected(file, isPdf ? 'pdf' : 'image');
  };

  return (
    <div className="w-full">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept={acceptedMimeTypes}
        className="hidden"
      />

      {!selectedFile ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200 ${
            isDragOver
              ? 'border-blue-500 bg-blue-500/10 shadow-glow-primary scale-[1.01]'
              : 'border-slate-800 hover:border-slate-700 bg-slate-900/40 hover:bg-slate-900/70'
          }`}
        >
          <div className="flex flex-col items-center justify-center space-y-3">
            <div className="w-14 h-14 rounded-2xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
              <UploadCloud className="w-7 h-7" />
            </div>

            <div>
              <p className="text-sm font-semibold text-white">
                Drag & drop your offer letter, job description PDF or screenshot
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Supports PDF, PNG, JPG, WebP up to 10MB
              </p>
            </div>

            <div className="flex items-center gap-2 pt-2">
              <span className="px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-[11px] font-mono text-slate-300 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-red-400" /> PDF Letters
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-[11px] font-mono text-slate-300 flex items-center gap-1.5">
                <ImageIcon className="w-3.5 h-3.5 text-purple-400" /> WhatsApp/Telegram Captures
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-4 rounded-2xl bg-slate-900 border border-blue-500/40 flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-blue-400">
              {selectedFile.type.includes('pdf') ? (
                <FileText className="w-5 h-5 text-red-400" />
              ) : (
                <ImageIcon className="w-5 h-5 text-purple-400" />
              )}
            </div>
            <div>
              <p className="text-sm font-medium text-white truncate max-w-xs sm:max-w-md">{selectedFile.name}</p>
              <p className="text-xs text-slate-400 font-mono">{formatFileSize(selectedFile.size)} • Ready for OCR extraction</p>
            </div>
          </div>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onRemoveFile();
            }}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  );
};

export default DropZone;
