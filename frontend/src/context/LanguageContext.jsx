import { createContext, useContext, useState } from "react";

export const LANGUAGES = [
  { code: "en", label: "English", speechLang: "en-US" },
  { code: "hi", label: "हिंदी (Hindi)", speechLang: "hi-IN" },
  { code: "kn", label: "ಕನ್ನಡ (Kannada)", speechLang: "kn-IN" },
  { code: "ta", label: "தமிழ் (Tamil)", speechLang: "ta-IN" },
  { code: "te", label: "తెలుగు (Telugu)", speechLang: "te-IN" },
  { code: "mr", label: "मराठी (Marathi)", speechLang: "mr-IN" },
  { code: "bn", label: "বাংলা (Bengali)", speechLang: "bn-IN" },
  { code: "gu", label: "ગુજરાતી (Gujarati)", speechLang: "gu-IN" },
  { code: "pa", label: "ਪੰਜਾਬੀ (Punjabi)", speechLang: "pa-IN" },
  { code: "ml", label: "മലയാളം (Malayalam)", speechLang: "ml-IN" },
];

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState("en");
  const current = LANGUAGES.find((l) => l.code === language) || LANGUAGES[0];
  return (
    <LanguageContext.Provider value={{ language, setLanguage, current, LANGUAGES }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
