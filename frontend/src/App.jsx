import { useState } from "react";
import { Routes, Route, Link } from "react-router-dom";
import { LanguageProvider } from "./context/LanguageContext";
import LanguageSelector from "./components/LanguageSelector";
import Diagnose from "./components/Diagnose";
import FieldScan from "./components/FieldScan";
import MarketTrend from "./components/MarketTrend";
import SellHoldAdvisor from "./components/SellHoldAdvisor";
import ChatBot from "./components/ChatBot";
import OutbreakMap from "./components/OutbreakMap";
import CommunityQA from "./components/CommunityQA";
import WhatsAppMockup from "./components/WhatsAppMockup";
import Landing from "./pages/Landing";
import "./App.css";

const TABS = [
  { id: "diagnose", label: "🔍 Diagnose", component: Diagnose },
  { id: "field", label: "🌾 Field Scan", component: FieldScan },
  { id: "market", label: "📈 Market", component: MarketTrend },
  { id: "advisor", label: "🤖 Sell/Hold", component: SellHoldAdvisor },
  { id: "chat", label: "💬 Chat", component: ChatBot },
  { id: "outbreak", label: "🗺️ Outbreak Map", component: OutbreakMap },
  { id: "qa", label: "🧑‍🌾 Community", component: CommunityQA },
  { id: "whatsapp", label: "📱 WhatsApp Concept", component: WhatsAppMockup },
];

function AppShell() {
  const [active, setActive] = useState("diagnose");
  const Active = TABS.find((t) => t.id === active)?.component ?? Diagnose;

  return (
    <div className="app-root">
      <header className="app-header">
        <Link to="/" className="brand" aria-label="AgriSense AI home">
          <span className="brand-icon">🌱</span>
          <div>
            <h1>AgriSense AI</h1>
            <p className="tagline">Your AI farm companion - crop health, weather &amp; fair pricing</p>
          </div>
        </Link>
        <LanguageSelector />
      </header>

      <nav className="tab-nav">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`tab-btn ${active === t.id ? "active" : ""}`}
            onClick={() => setActive(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main className="app-main">
        <Active />
      </main>

      <footer className="app-footer">
        AgriSense AI - prototype. Diagnosis and market data are for guidance only; consult a local
        agronomist and market authority for high-value decisions.
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <LanguageProvider>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/app" element={<AppShell />} />
      </Routes>
    </LanguageProvider>
  );
}
