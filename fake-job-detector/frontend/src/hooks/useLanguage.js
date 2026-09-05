import { useState, useEffect } from 'react';

export const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English', native: 'English', flag: '🌐' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी', flag: '🇮🇳' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ', flag: '🇮🇳' },
  { code: 'fil', name: 'Filipino', native: 'Wikang Filipino', flag: '🇵🇭' },
  { code: 'id', name: 'Indonesian', native: 'Bahasa Indonesia', flag: '🇮🇩' },
  { code: 'th', name: 'Thai', native: 'ไทย', flag: '🇹🇭' },
];

export const useLanguage = () => {
  const [currentLang, setCurrentLang] = useState(() => {
    const saved = localStorage.getItem('sentinel_lang');
    return SUPPORTED_LANGUAGES.find((l) => l.code === saved) || SUPPORTED_LANGUAGES[0];
  });

  const changeLanguage = (langCode) => {
    const selected = SUPPORTED_LANGUAGES.find((l) => l.code === langCode);
    if (selected) {
      setCurrentLang(selected);
      localStorage.setItem('sentinel_lang', selected.code);
    }
  };

  return {
    currentLang,
    changeLanguage,
    languages: SUPPORTED_LANGUAGES,
  };
};

export default useLanguage;
