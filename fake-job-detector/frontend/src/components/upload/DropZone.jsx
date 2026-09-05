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
    const isPdf = Boolean(
      (file.type && file.type.includes('pdf')) || 
      (file.name && file.name.toLowerCase().endsWith('.pdf'))
    );
    const isImage = Boolean(
      (file.type && file.type.startsWith('image/')) ||
      (file.name && /\.(png|jpe?g|webp|gif|bmp)$/i.test(file.name))
    );
    
    if (acceptType === 'pdf' && !isPdf) {
      alert('Please upload a valid PDF document.');
      return;
    }
    if (acceptType === 'image' && !isImage && !isPdf) {
      alert('Please upload a valid image (PNG, JPG, WebP) or PDF file.');
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
              ? 'border-emerald-500 bg-emerald-500/10 shadow-glow-primary scale-[1.01]'
              : 'border-white/15 hover:border-emerald-500/40 bg-black/40 hover:bg-white/[0.02]'
          }`}
        >
          <div className="flex flex-col items-center justify-center space-y-3">
            <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <UploadCloud className="w-7 h-7" />
            </div>

            <div>
              <p className="text-sm font-semibold text-frost">
                Drag & drop your offer letter, job description PDF or screenshot
              </p>
              <p className="text-xs text-fog mt-1">
                Supports PDF, PNG, JPG, WebP up to 10MB
              </p>
            </div>

            <div className="flex items-center gap-2 pt-2">
              <span className="px-2.5 py-1 rounded-lg bg-black/60 border border-white/10 text-[11px] font-mono text-fog flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-red-400" /> PDF Letters
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-black/60 border border-white/10 text-[11px] font-mono text-fog flex items-center gap-1.5">
                <ImageIcon className="w-3.5 h-3.5 text-emerald-400" /> Screenshots & Images
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-4 rounded-2xl bg-black/50 border border-emerald-500/40 flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              {(selectedFile.type?.includes('pdf') || selectedFile.name?.toLowerCase().endsWith('.pdf')) ? (
                <FileText className="w-5 h-5 text-red-400" />
              ) : (
                <ImageIcon className="w-5 h-5 text-emerald-400" />
              )}
            </div>
            <div>
              <p className="text-sm font-medium text-frost truncate max-w-xs sm:max-w-md">{selectedFile.name}</p>
              <p className="text-xs text-fog font-mono">{formatFileSize(selectedFile.size)} • Ready for analysis</p>
            </div>
          </div>

          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onRemoveFile();
            }}
            className="p-1.5 rounded-lg text-fog hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  );
};

export default DropZone;
