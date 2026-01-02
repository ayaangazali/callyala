import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// Lazy load translations using i18next-http-backend
i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    // Remove direct localStorage access - let LanguageDetector handle it
    
    backend: {
      // Load from public folder for lazy loading
      loadPath: '/locales/{{lng}}.json',
    },
    
    interpolation: {
      escapeValue: false, // React already escapes
    },
    
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
    
    react: {
      useSuspense: false, // Disable suspense for better performance
    },
    
    // Performance optimizations
    load: 'languageOnly', // Only load 'en', not 'en-US'
    cleanCode: true, // Remove region code from language
    
    // Debug in development only
    debug: false,
  });

// Listen for language changes and update document direction
i18n.on('languageChanged', (lng) => {
  const dir = lng === 'ar' ? 'rtl' : 'ltr';
  document.documentElement.dir = dir;
  document.documentElement.lang = lng;
  localStorage.setItem('language', lng);
});

// Set initial direction
const currentLang = i18n.language;
const initialDir = currentLang === 'ar' ? 'rtl' : 'ltr';
document.documentElement.dir = initialDir;
document.documentElement.lang = currentLang;

export default i18n;
