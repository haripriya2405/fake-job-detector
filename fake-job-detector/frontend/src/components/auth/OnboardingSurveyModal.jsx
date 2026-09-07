import React, { useState } from 'react';
import {
  Sparkles,
  Youtube,
  Twitter,
  MessageSquare,
  ExternalLink,
  Search,
  Users,
  X as CloseIcon,
  Globe,
  ArrowLeft,
  ArrowRight,
  Check,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const OPTIONS = [
  { id: 'llm', label: 'LLM (ChatGPT, Claude, etc.)', icon: Sparkles },
  { id: 'youtube', label: 'YouTube', icon: Youtube },
  { id: 'twitter', label: 'X (Twitter)', icon: Twitter },
  { id: 'reddit', label: 'Reddit', icon: MessageSquare },
  { id: 'producthunt', label: 'Product Hunt', icon: ExternalLink },
  { id: 'google', label: 'Google Search', icon: Search },
  { id: 'friend', label: 'Friend/Colleague', icon: Users },
  { id: 'other', label: 'Other', icon: ExternalLink },
];

export const OnboardingSurveyModal = ({ isOpen, onClose, onComplete }) => {
  const navigate = useNavigate();
  const [selectedOption, setSelectedOption] = useState(null);
  const [otherText, setOtherText] = useState('');
  const [step, setStep] = useState(1);

  if (!isOpen) return null;

  const handleSelect = (id) => {
    setSelectedOption(id);
  };

  const handleContinue = () => {
    if (onComplete) {
      onComplete({ option: selectedOption, detail: otherText });
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl bg-[#0c121d] border border-slate-800 rounded-2xl shadow-2xl p-6 sm:p-8 space-y-6 overflow-hidden">
        
        {/* Header Bar */}
        <div className="flex items-center justify-between text-xs text-slate-400">
          <button
            type="button"
            onClick={onClose}
            className="inline-flex items-center gap-1.5 hover:text-slate-200 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to home</span>
          </button>

          <div className="flex items-center gap-4">
            <span className="font-mono text-[10px] tracking-wider uppercase text-slate-400">
              OPTIONAL STEP {step} OF 3
            </span>
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span className="w-2 h-2 rounded-full bg-slate-700" />
              <span className="w-2 h-2 rounded-full bg-slate-700" />
            </div>
            <button
              type="button"
              onClick={onClose}
              className="text-emerald-400 hover:text-emerald-300 font-medium transition-colors pl-2"
            >
              Skip to scan
            </button>
          </div>
        </div>

        {/* Title & Description */}
        <div className="space-y-1.5">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Where did you find us?
          </h2>
          <p className="text-sm text-slate-400 font-light">
            Help us understand how you discovered JobScamScore
          </p>
        </div>

        {/* Options Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {OPTIONS.map((opt) => {
            const Icon = opt.icon;
            const isSelected = selectedOption === opt.id;
            return (
              <button
                key={opt.id}
                type="button"
                onClick={() => handleSelect(opt.id)}
                className={`flex items-center gap-3.5 p-4 rounded-xl border text-left transition-all duration-200 ${
                  isSelected
                    ? 'border-emerald-500/80 bg-emerald-950/30 text-emerald-300 ring-1 ring-emerald-500/50 shadow-lg shadow-emerald-500/10'
                    : 'border-slate-800/80 bg-slate-900/50 text-slate-300 hover:border-slate-700 hover:bg-slate-800/50'
                }`}
              >
                <div
                  className={`p-2 rounded-lg shrink-0 ${
                    isSelected ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <span className="text-xs sm:text-sm font-medium">{opt.label}</span>
                {isSelected && <Check className="w-4 h-4 ml-auto text-emerald-400" />}
              </button>
            );
          })}
        </div>

        {/* Dynamic slide-down text box when 'other' is selected */}
        {selectedOption === 'other' && (
          <div className="space-y-2 pt-1 animate-in slide-in-from-top-2 duration-200">
            <label className="block text-xs font-medium text-slate-300">
              Please specify where you found us
            </label>
            <input
              type="text"
              value={otherText}
              onChange={(e) => setOtherText(e.target.value)}
              placeholder="e.g. Facebook, a blog, a newsletter..."
              className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>
        )}

        {/* Action Button */}
        {selectedOption && (
          <div className="pt-2 animate-in fade-in duration-200">
            <button
              type="button"
              onClick={handleContinue}
              className="w-full py-3 px-4 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-sm transition-all shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2"
            >
              <span>Continue</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

      </div>
    </div>
  );
};

export default OnboardingSurveyModal;
