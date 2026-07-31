import { useLanguage } from "../context/LanguageContext";

export default function LanguageSelector() {
  const { language, setLanguage, LANGUAGES } = useLanguage();
  return (
    <select
      className="lang-select"
      value={language}
      onChange={(e) => setLanguage(e.target.value)}
      title="Choose your language"
    >
      {LANGUAGES.map((l) => (
        <option key={l.code} value={l.code}>
          {l.label}
        </option>
      ))}
    </select>
  );
}
