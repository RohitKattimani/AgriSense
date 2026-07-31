import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { LANGUAGES } from "../context/LanguageContext";
import "./Landing.css";

// Same script/content as the in-app WhatsApp mockup, condensed for the hero -
// kept consistent so the promise on the landing page matches the product.
const HERO_SCRIPT = [
  { from: "user", text: "📷 [photo of tomato leaf]" },
  {
    from: "bot",
    text: "Diagnosis: Early Blight (Tomato)\nConfidence: 91%\n\nRemove infected lower leaves, avoid wetting leaves when watering, consider a copper-based spray.",
  },
  { from: "user", text: "market tomato" },
  {
    from: "bot",
    text: "Tomato · Bengaluru region\n₹18.6/kg · Rising +4% (7d)\n\nAdvice: HOLD - price trending up, no rain expected to spoil your harvest.",
  },
];

const TICKER = [
  { crop: "Tomato", price: "₹18.6/kg", trend: "up" },
  { crop: "Onion", price: "₹22.4/kg", trend: "down" },
  { crop: "Wheat", price: "₹24.1/kg", trend: "flat" },
  { crop: "Cotton", price: "₹64.8/kg", trend: "up" },
  { crop: "Groundnut", price: "₹58.3/kg", trend: "up" },
  { crop: "Chilli", price: "₹142/kg", trend: "down" },
  { crop: "Paddy", price: "₹21.9/kg", trend: "flat" },
  { crop: "Maize", price: "₹19.2/kg", trend: "up" },
];

const STEPS = [
  {
    n: "01",
    title: "Snap a photo",
    body: "Point any phone camera at a leaf or a stretch of field - no special equipment, no signal needed to take the shot.",
  },
  {
    n: "02",
    title: "Get a read in seconds",
    body: "The AI names the disease, scores field health, checks today's mandi trend and the weather - together, not one at a time.",
  },
  {
    n: "03",
    title: "Decide with confidence",
    body: "A plain-language treatment plan and a clear sell-or-hold call, spoken back to you in your own language.",
  },
];

const FEATURES = [
  {
    icon: "🔍",
    title: "Instant crop diagnosis",
    body: "Photograph a leaf and get a disease call with a confidence score and a treatment plan you can act on today.",
  },
  {
    icon: "🌾",
    title: "Whole-field health score",
    body: "Scan a full field, not just one leaf - see a stress map and an estimated yield-loss range.",
  },
  {
    icon: "📈",
    title: "Live mandi prices",
    body: "Track price trends for your crop in your region, so you're never selling blind at the farm gate.",
  },
  {
    icon: "🤖",
    title: "Sell or hold advisor",
    body: "An AI agent weighs price trend, weather and shelf life together, then shows its reasoning for SELL or HOLD.",
  },
  {
    icon: "🗺️",
    title: "Outbreak map",
    body: "See disease reports from nearby farms so you can treat early, before an outbreak reaches your own field.",
  },
  {
    icon: "💬",
    title: "Voice, in your language",
    body: "Type or speak your question and get an answer read back to you - built for low-literacy, low-bandwidth use.",
  },
];

function TrendGlyph({ trend }) {
  if (trend === "up") return <span className="tick-trend up">▲</span>;
  if (trend === "down") return <span className="tick-trend down">▼</span>;
  return <span className="tick-trend flat">▬</span>;
}

function PhoneDemo() {
  const [visible, setVisible] = useState(0);
  const [typing, setTyping] = useState(false);
  const timers = useRef([]);

  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) {
      setVisible(HERO_SCRIPT.length);
      return;
    }
    let delay = 500;
    HERO_SCRIPT.forEach((msg, i) => {
      if (msg.from === "bot") {
        timers.current.push(setTimeout(() => setTyping(true), delay));
        delay += 700;
      }
      timers.current.push(
        setTimeout(() => {
          setTyping(false);
          setVisible(i + 1);
        }, delay)
      );
      delay += msg.from === "bot" ? 1400 : 900;
    });
    return () => timers.current.forEach(clearTimeout);
  }, []);

  return (
    <div className="phone" aria-hidden="true">
      <div className="phone-notch" />
      <div className="phone-head">
        <span className="phone-avatar">🌱</span>
        <div>
          <div className="phone-name">AgriSense Bot</div>
          <div className="phone-status">{typing ? "typing…" : "online"}</div>
        </div>
      </div>
      <div className="phone-body">
        {HERO_SCRIPT.slice(0, visible).map((m, i) => (
          <div key={i} className={`phone-bubble ${m.from}`}>
            {m.text.split("\n").map((line, j) => (
              <div key={j}>{line}</div>
            ))}
          </div>
        ))}
        {typing && (
          <div className="phone-bubble bot typing-bubble">
            <span className="dot" />
            <span className="dot" />
            <span className="dot" />
          </div>
        )}
      </div>
    </div>
  );
}

export default function Landing() {
  return (
    <div className="landing">
      <div className="landing-glow" aria-hidden="true" />

      <header className="ld-nav">
        <div className="ld-brand">
          <span className="ld-brand-icon">🌱</span>
          <span className="ld-brand-name">AgriSense AI</span>
        </div>
        <Link to="/app" className="ld-nav-cta">
          Open the app <span aria-hidden="true">→</span>
        </Link>
      </header>

      <section className="ld-hero">
        <div className="ld-hero-copy">
          <p className="ld-eyebrow">Built for the field, not the office</p>
          <h1>
            Point your phone
            <br />
            at a leaf. <span className="ld-hero-accent">Know what to do next.</span>
          </h1>
          <p className="ld-hero-sub">
            AgriSense AI reads crop photos, checks today's mandi prices and the weather, then
            tells you - in your own language - what's wrong, what to spray, and whether to sell
            or hold.
          </p>
          <div className="ld-hero-actions">
            <Link to="/app" className="ld-btn-primary">
              Try the live demo
            </Link>
            <a href="#how-it-works" className="ld-btn-ghost">
              See how it works
            </a>
          </div>
          <p className="ld-hero-note">
            Free, open prototype · works over a slow connection · also designed to run as a
            WhatsApp bot
          </p>
        </div>
        <div className="ld-hero-visual">
          <PhoneDemo />
        </div>
      </section>

      <div className="ld-ticker" role="presentation">
        <div className="ld-ticker-track">
          {[...TICKER, ...TICKER].map((t, i) => (
            <span className="tick-item" key={i}>
              <span className="tick-crop">{t.crop}</span>
              <span className="tick-price">{t.price}</span>
              <TrendGlyph trend={t.trend} />
            </span>
          ))}
        </div>
      </div>

      <section className="ld-section" id="how-it-works">
        <h2 className="ld-h2">From photo to decision, in three steps</h2>
        <div className="ld-steps">
          {STEPS.map((s) => (
            <div className="ld-step" key={s.n}>
              <span className="ld-step-n">{s.n}</span>
              <h3>{s.title}</h3>
              <p>{s.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="ld-section ld-section-tight">
        <h2 className="ld-h2">Everything a smallholder farm actually needs</h2>
        <p className="ld-section-sub">
          Seven tools, one companion - crop health, market pricing and community alerts in a
          single place.
        </p>
        <div className="ld-features">
          {FEATURES.map((f) => (
            <div className="ld-feature-card" key={f.title}>
              <span className="ld-feature-icon">{f.icon}</span>
              <h3>{f.title}</h3>
              <p>{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="ld-section ld-lang-section">
        <h2 className="ld-h2">Talk to it in your language</h2>
        <p className="ld-section-sub">
          Type or use your voice - AgriSense AI answers back in the language you picked, not just
          English.
        </p>
        <div className="ld-lang-cloud">
          {LANGUAGES.map((l) => (
            <span className="ld-lang-chip" key={l.code}>
              {l.label}
            </span>
          ))}
        </div>
      </section>

      <section className="ld-cta-band">
        <h2>Bring it to your field</h2>
        <p>No account, no install. Open it in a browser and try it with a real crop photo.</p>
        <Link to="/app" className="ld-btn-primary ld-btn-light">
          Open AgriSense AI <span aria-hidden="true">→</span>
        </Link>
      </section>

      <footer className="ld-footer">
        <span>🌱 AgriSense AI</span>
        <span>
          Prototype - diagnosis and market data are for guidance only; consult a local agronomist
          and market authority for high-value decisions.
        </span>
      </footer>
    </div>
  );
}
