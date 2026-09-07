import React, { createContext, useContext, useState, useEffect } from 'react';

export const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English', native: 'English', flag: '🌐' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी', flag: '🇮🇳' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ', flag: '🇮🇳' },
];

export const TRANSLATIONS = {
  en: {
    chooseLanguage: 'CHOOSE LANGUAGE',
    brandName: 'SentinelJob AI',
    jobScamChecker: 'Job Scam Checker',
    scamDatabase: 'Scam Database',
    redFlagsGuide: 'Red Flags Guide',
    scamSimulator: 'Scam Simulator',
    dashboard: 'Dashboard',
    scanHistory: 'Scan History & Vault',
    settings: 'Settings & API',
    signIn: 'Sign In',
    getStarted: 'Get Started',
    signOut: 'Sign Out',
    reportScam: 'Report Scam',
    overview: 'Overview',
    gameBadge: 'GAME',
    heroTitle: 'AI-Powered Fake Job & Internship Scam Detection',
    heroSubtitle: 'Protecting students, fresh graduates, and job seekers from fraudulent recruitment offers, identity theft, and fake checks.',
    scanBoxPlaceholder: 'Paste job description text, email body, or interview invitation here...',
    analyzeNow: 'Analyze Scam Risk',
    uploadOfferLetter: 'Upload PDF / Screenshot',
    enterUrl: 'Analyze Job URL',
    quickScanHeader: 'Free Multi-Modal Scam Detector',
    lowRisk: 'Low Risk',
    mediumRisk: 'Medium Risk',
    highRisk: 'High Risk',
    criticalRisk: 'Critical Risk',
    safe: 'Verified / Safe',
    scamDetected: 'Scam Detected',
    auditCertificate: 'Audit Certificate',
    searchPlaceholder: 'Search scam database...',
    submit: 'Submit',
    cancel: 'Cancel',
    copied: 'Copied!',
    copyLink: 'Copy Embed Code',
    topAdvisory: '⚡ Real-time Scam Alert: Beware of Telegram & WhatsApp job interviews asking for upfront fees.',
    pdfForensics: '📄 PDF Document Forensics & Metadata Check',
    logoConsistency: 'Logo & Signature Authenticity',
    fontTampering: 'Font & Layout Tampering Analysis',
    voipCarrier: 'Recruiter Carrier & Line Classification',
    federalAdvisories: 'External Watchlist Cross-Reference (FTC/BBB/IC3)',
    autoScanOverlay: '🛡️ SentinelJob 1-Click Auto-Scan Badge Active',
  },
  hi: {
    chooseLanguage: 'भाषा चुनें',
    brandName: 'सेंटिनलजॉब एआई',
    jobScamChecker: 'नौकरी घोटाला जांचकर्ता',
    scamDatabase: 'स्कैम डेटाबेस',
    redFlagsGuide: 'रेड फ्लैग्स गाइड',
    scamSimulator: 'स्कैम सिम्युलेटर',
    dashboard: 'डैशबोर्ड',
    scanHistory: 'स्कैन इतिहास और वॉल्ट',
    settings: 'सेटिंग्स और एपीआई',
    signIn: 'साइन इन करें',
    getStarted: 'शुरू करें',
    signOut: 'साइन आउट',
    reportScam: 'घोटाले की रिपोर्ट करें',
    overview: 'अवलोकन',
    gameBadge: 'गेम',
    heroTitle: 'एआई-संचालित फर्जी नौकरी और इंटर्नशिप घोटाला पहचान',
    heroSubtitle: 'छात्रों, नए स्नातकों और नौकरी चाहने वालों को फर्जी ऑफर लेटर, पहचान की चोरी और घोटालों से सुरक्षित रखें।',
    scanBoxPlaceholder: 'नौकरी का विवरण, ईमेल या साक्षात्कार का निमंत्रण यहां पेस्ट करें...',
    analyzeNow: 'स्कैम जोखिम का विश्लेषण करें',
    uploadOfferLetter: 'पीडीएफ / स्क्रीनशॉट अपलोड करें',
    enterUrl: 'नौकरी का यूआरएल जांचें',
    quickScanHeader: 'मुफ्त मल्टी-मॉडल स्कैम डिटेक्टर',
    lowRisk: 'कम जोखिम',
    mediumRisk: 'मध्यम जोखिम',
    highRisk: 'उच्च जोखिम',
    criticalRisk: 'गंभीर जोखिम',
    safe: 'सत्यापित / सुरक्षित',
    scamDetected: 'घोटाला पहचाना गया',
    auditCertificate: 'ऑडिट प्रमाणपत्र',
    searchPlaceholder: 'स्कैम डेटाबेस में खोजें...',
    submit: 'जमा करें',
    cancel: 'रद्द करें',
    copied: 'कॉपी हो गया!',
    copyLink: 'कोड कॉपी करें',
    topAdvisory: '⚡ लाइव स्कैम अलर्ट: टेलीग्राम और व्हाट्सएप इंटरव्यू से सावधान रहें जो अग्रिम शुल्क मांगते हैं।',
    pdfForensics: '📄 पीडीएफ दस्तावेज़ फॉरेंसिक और मेटाडेटा जांच',
    logoConsistency: 'लोगो और हस्ताक्षर की प्रामाणिकता',
    fontTampering: 'फ़ॉन्ट और लेआउट छेड़छाड़ विश्लेषण',
    voipCarrier: 'रिक्रूटर लाइन वर्गीकरण (वीओआईपी/वर्चुअल)',
    federalAdvisories: 'सरकारी निगरानी सूची मिलान (FTC/BBB/IC3)',
    autoScanOverlay: '🛡️ जॉब पोर्टल पर ऑटो-स्कैन बैज सक्रिय',
  },
  kn: {
    chooseLanguage: 'ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ',
    brandName: 'ಸೆಂಟಿನೆಲ್-ಜಾಬ್ ಎಐ',
    jobScamChecker: 'ಉದ್ಯೋಗ ವಂಚನೆ ಪರೀಕ್ಷಕ',
    scamDatabase: 'ವಂಚನೆ ಡೇಟಾಬೇಸ್',
    redFlagsGuide: 'ಅಪಾಯ ಸೂಚನೆಗಳ ಮಾರ್ಗದರ್ಶಿ',
    scamSimulator: 'ವಂಚನೆ ಸಿಮ್ಯುಲೇಟರ್',
    dashboard: 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
    scanHistory: 'ಪರಿಶೀಲನಾ ಇತಿಹಾಸ',
    settings: 'ಸೇಟಿಂಗ್ಸ್ ಮತ್ತು ಎಪಿಐ',
    signIn: 'ಸೈನ್ ಇನ್ ಮಾಡಿ',
    getStarted: 'ಪ್ರಾರಂಭಿಸಿ',
    signOut: 'ಸೈನ್ ಔಟ್',
    reportScam: 'ವಂಚನೆಯ ವರದಿ ಮಾಡಿ',
    overview: 'ಅವಲೋಕನ',
    gameBadge: 'ಆಟ',
    heroTitle: 'ಎಐ-ಆಧಾರಿತ ನಕಲಿ ಉದ್ಯೋಗ ಮತ್ತು ಇಂಟರ್ನ್‌ಶಿಪ್ ವಂಚನೆ ಪತ್ತೆ',
    heroSubtitle: 'ವಿದ್ಯಾರ್ಥಿಗಳು ಮತ್ತು ಉದ್ಯೋಗಾಕಾಂಕ್ಷಿಗಳನ್ನು ನಕಲಿ ಆಫರ್ ಲೆಟರ್, ಹಣದ ಬೇಡಿಕೆ ಮತ್ತು ವಂಚನೆಯಿಂದ ರಕ್ಷಿಸಿ.',
    scanBoxPlaceholder: 'ಉದ್ಯೋಗ ವಿವರಣೆ, ಇಮೇಲ್ ಅಥವಾ ಸಂದರ್ಶನ ಕರೆಯನ್ನು ಇಲ್ಲಿ ಪೇಸ್ಟ್ ಮಾಡಿ...',
    analyzeNow: 'ವಂಚನೆ ಅಪಾಯವನ್ನು ವಿಶ್ಲೇಷಿಸಿ',
    uploadOfferLetter: 'ಪಿಡಿಎಫ್ / ಸ್ಕ್ರೀನ್‌ಶಾಟ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ',
    enterUrl: 'ಉದ್ಯೋಗ ಯುಆರ್‌ಎಲ್ ಪರಿಶೀಲಿಸಿ',
    quickScanHeader: 'ಉಚಿತ ಮಲ್ಟಿ-ಮಾಡೆಲ್ ವಂಚನೆ ಪತ್ತೆಕಾರಕ',
    lowRisk: 'ಕಡಿಮೆ ಅಪಾಯ',
    mediumRisk: 'ಮಧ್ಯಮ ಅಪಾಯ',
    highRisk: 'ಹೆಚ್ಚಿನ ಅಪಾಯ',
    criticalRisk: 'ತೀವ್ರ ಅಪಾಯ',
    safe: 'ಪರಿಶೀಲಿಸಿದ / ಸುರಕ್ಷಿತ',
    scamDetected: 'ವಂಚನೆ ಪತ್ತೆಯಾಗಿದೆ',
    auditCertificate: 'ಪರಿಶೀಲನಾ ಪ್ರಮಾಣಪತ್ರ',
    searchPlaceholder: 'ವಂಚನೆ ಡೇಟಾಬೇಸ್‌ನಲ್ಲಿ ಹುಡುಕಿ...',
    submit: 'ಸಲ್ಲಿಸಿ',
    cancel: 'ರದ್ದುಗೊಳಿಸಿ',
    copied: 'ಕಾಪಿ ಮಾಡಲಾಗಿದೆ!',
    copyLink: 'ಕೋಡ್ ಕಾಪಿ ಮಾಡಿ',
    topAdvisory: '⚡ ಲೈವ್ ವಂಚನೆ ಎಚ್ಚರಿಕೆ: ಮುಂಗಡ ಹಣ ಕೇಳುವ ಟೆಲಿಗ್ರಾಮ್ ಮತ್ತು ವಾಟ್ಸಾಪ್ ಸಂದರ್ಶನಗಳಿಂದ ಎಚ್ಚರದಿಂದಿರಿ.',
    pdfForensics: '📄 ಪಿಡಿಎಫ್ ದಾಖಲೆ ವಿಧಿವಿಜ್ಞಾನ ಮತ್ತು ಮೆಟಾಡೇಟಾ ಪರೀಕ್ಷೆ',
    logoConsistency: 'ಲೋಗೋ ಮತ್ತು ಸಹಿಯ ನೈಜತೆಯ ತಪಾಸಣೆ',
    fontTampering: 'ಫಾಂಟ್ ಮತ್ತು ಲೇಔಟ್ ಬದಲಾವಣೆ ವಿಶ್ಲೇಷಣೆ',
    voipCarrier: 'ಉದ್ಯೋಗದಾತ ಫೋನ್ ಲೈನ್ ವರ್ಗೀಕರಣ',
    federalAdvisories: 'ಸರ್ಕಾರಿ ವಾಚ್‌ಲಿಸ್ಟ್ ತಪಾಸಣೆ (FTC/BBB/IC3)',
    autoScanOverlay: '🛡️ ಉದ್ಯೋಗ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ 1-ಕ್ಲಿಕ್ ಆಟೋ-ಸ್ಕ್ಯಾನ್ ಸಕ್ರಿಯ',
  },
};

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
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

  const t = (key, fallback = '') => {
    const langDict = TRANSLATIONS[currentLang.code] || TRANSLATIONS.en;
    return langDict[key] || TRANSLATIONS.en[key] || fallback || key;
  };

  return (
    <LanguageContext.Provider value={{ currentLang, changeLanguage, languages: SUPPORTED_LANGUAGES, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    const saved = localStorage.getItem('sentinel_lang');
    const curr = SUPPORTED_LANGUAGES.find((l) => l.code === saved) || SUPPORTED_LANGUAGES[0];
    return {
      currentLang: curr,
      changeLanguage: (code) => localStorage.setItem('sentinel_lang', code),
      languages: SUPPORTED_LANGUAGES,
      t: (k, fb = '') => (TRANSLATIONS[curr.code]?.[k] || TRANSLATIONS.en[k] || fb || k),
    };
  }
  return context;
};

export default LanguageContext;
