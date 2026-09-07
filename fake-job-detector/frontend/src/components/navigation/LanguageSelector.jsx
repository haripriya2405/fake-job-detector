import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check } from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';

export const LanguageSelector = ({ variant = 'default' }) => {
  const { currentLang, changeLanguage, languages, t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Click outside & Escape key listeners
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button
        type="button"
        aria-label="Select language"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 rounded-full border border-white/15 bg-white/5 px-3 py-1.5 text-xs font-medium text-frost/80 hover:bg-white/10 hover:text-white transition-all shadow-sm focus:outline-none focus:ring-1 focus:ring-emerald-400"
      >
        <span aria-hidden="true" className="text-sm">🌐</span>
        <span className="font-normal">{currentLang.native}</span>
        <ChevronDown className={`h-3.5 w-3.5 opacity-60 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div
          role="listbox"
          aria-label="Languages"
          className="absolute right-0 mt-2 w-48 rounded-2xl border border-white/15 bg-[#07100c]/95 backdrop-blur-xl p-1.5 shadow-2xl z-50 animate-in fade-in slide-in-from-top-2 duration-150"
        >
          <div className="px-2.5 py-1 text-[10px] font-mono uppercase tracking-wider text-fog border-b border-white/10 mb-1">
            {t('chooseLanguage')}
          </div>
          {languages.map((lang) => {
            const isSelected = lang.code === currentLang.code;
            return (
              <button
                key={lang.code}
                type="button"
                role="option"
                aria-selected={isSelected}
                onClick={() => {
                  changeLanguage(lang.code);
                  setIsOpen(false);
                }}
                className={`w-full flex items-center justify-between px-3 py-2 text-xs rounded-xl transition-colors text-left ${
                  isSelected
                    ? 'bg-emerald-500/15 text-emerald-300 font-semibold border border-emerald-500/20'
                    : 'text-mist hover:text-frost hover:bg-white/5'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span>{lang.flag}</span>
                  <span>{lang.native}</span>
                  {lang.name !== lang.native && (
                    <span className="text-[10px] text-fog font-light">({lang.name})</span>
                  )}
                </div>
                {isSelected && <Check className="w-3.5 h-3.5 text-emerald-400" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default LanguageSelector;
