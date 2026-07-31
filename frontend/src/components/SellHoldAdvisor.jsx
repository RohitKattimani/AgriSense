import { useEffect, useState } from "react";
import { getCrops, getSellHoldAdvice } from "../api/client";
import { useLanguage } from "../context/LanguageContext";

export default function SellHoldAdvisor() {
  const { language } = useLanguage();
  const [crops, setCrops] = useState([]);
  const [crop, setCrop] = useState("tomato");
  const [qty, setQty] = useState(50);
  const [loading, setLoading] = useState(false);
  const [advice, setAdvice] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getCrops().then(setCrops).catch(() => setCrops(["tomato", "potato", "onion", "wheat", "grapes"]));
  }, []);

  const ask = async () => {
    setLoading(true);
    setError(null);
    setAdvice(null);
    try {
      const data = await getSellHoldAdvice({ crop, quantity_kg: Number(qty), language });
      setAdvice(data);
    } catch (e) {
      setError(e?.response?.data?.detail || "Couldn't get advice right now.");
    } finally {
      setLoading(false);
    }
  };

  const decisionTag = advice?.recommendation_text?.toUpperCase().includes("SELL") ? "sell" : "hold";

  return (
    <div className="card">
      <h2>🤖 Smart Sell / Hold Advisor</h2>
      <p className="muted">
        An AI agent that checks price trends, weather, and how perishable your crop is - then
        tells you whether to sell now or hold.
      </p>

      <div className="row">
        <select className="crop-select" value={crop} onChange={(e) => setCrop(e.target.value)}>
          {crops.map((c) => (
            <option key={c} value={c}>
              {c[0].toUpperCase() + c.slice(1)}
            </option>
          ))}
        </select>
        <input
          className="text-input qty-input"
          type="number"
          min="0"
          value={qty}
          onChange={(e) => setQty(e.target.value)}
          placeholder="Quantity (kg)"
        />
      </div>

      <button className="primary-btn" onClick={ask} disabled={loading}>
        {loading ? "Consulting price + weather data…" : "Get Advice"}
      </button>

      {error && <p className="error-text">{error}</p>}

      {advice && (
        <div className={`advice-panel ${decisionTag}`}>
          <p className="advice-text">{advice.recommendation_text}</p>

          <details>
            <summary>How the agent reached this ({advice.tool_calls.length} tool calls)</summary>
            <ul className="tool-trace">
              {advice.tool_calls.map((t, i) => (
                <li key={i}>
                  <b>{t.name}</b>
                  <pre>{JSON.stringify(t.result, null, 2).slice(0, 600)}</pre>
                </li>
              ))}
            </ul>
          </details>
        </div>
      )}
    </div>
  );
}
