import { useState } from "react";

const SCRIPT = [
  { from: "bot", text: "🌱 *AgriSense Bot*\nHi! Send a photo of your crop leaf and I'll check it for disease. Or type *market tomato* for prices, or *help*." },
  { from: "user", text: "📷 [photo of tomato leaf]" },
  { from: "bot", text: "🔍 Analyzing…\n\n*Diagnosis:* Early Blight (Tomato)\n*Confidence:* 91%\n\nCaused by a fungus, common after rain. Remove infected lower leaves, avoid wetting leaves when watering, and consider a copper-based spray.\n\nReply *1* to ask a follow-up question, or *2* for market prices." },
  { from: "user", text: "market tomato" },
  { from: "bot", text: "📈 *Tomato - Bengaluru region*\nCurrent: ₹18.6/kg\nTrend: Rising (+4% over 7 days)\n\n🤖 *Advice:* HOLD for a few more days - prices are trending up and no rain expected that would spoil your harvest.\n\nReply *sell* to see nearby buyers, or *menu* for options." },
  { from: "user", text: "menu" },
  { from: "bot", text: "🌾 *Main Menu*\n1️⃣ Diagnose a crop photo\n2️⃣ Market prices\n3️⃣ Weather forecast\n4️⃣ Ask a question (voice note OK 🎙️)\n5️⃣ Community outbreak alerts near me" },
];

export default function WhatsAppMockup() {
  const [visible, setVisible] = useState(1);

  return (
    <div className="card">
      <h2>📱 WhatsApp-Bot Delivery Concept</h2>
      <p className="muted">
        Many farmers already use WhatsApp daily. This mockup shows how the same diagnosis, market,
        and advisor logic from this app could be delivered as a WhatsApp bot (via the WhatsApp
        Business Cloud API) - no app install required, works on the most basic smartphones.
      </p>

      <div className="whatsapp-frame">
        <div className="whatsapp-header">🌱 AgriSense Bot</div>
        <div className="whatsapp-body">
          {SCRIPT.slice(0, visible).map((m, i) => (
            <div key={i} className={`wa-bubble ${m.from}`}>
              {m.text.split("\n").map((line, j) => (
                <div key={j}>{line}</div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {visible < SCRIPT.length && (
        <button className="primary-btn small" onClick={() => setVisible((v) => v + 1)}>
          ▶ Next message
        </button>
      )}
      {visible >= SCRIPT.length && (
        <button className="primary-btn small" onClick={() => setVisible(1)}>
          ↺ Replay conversation
        </button>
      )}

      <p className="muted implementation-note">
        <b>Implementation note:</b> the WhatsApp Business Cloud API would receive incoming
        messages/media via webhook, forward photos to the same <code>/api/diagnose</code> endpoint
        and text to <code>/api/chat</code> / <code>/api/advisor/sell-hold</code> used by this web
        app, then send the reply back through the WhatsApp API - the backend built here needs no
        changes to support it.
      </p>
    </div>
  );
}
