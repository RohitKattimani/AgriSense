import { useState, useRef } from "react";
import { fieldScan } from "../api/client";
import { useLanguage } from "../context/LanguageContext";

export default function FieldScan() {
  const { language } = useLanguage();
  const [files, setFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [affectedArea, setAffectedArea] = useState(30);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const onFiles = (list) => {
    const arr = Array.from(list);
    setFiles(arr);
    setPreviews(arr.map((f) => URL.createObjectURL(f)));
    setResult(null);
  };

  const submit = async () => {
    if (!files.length) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fieldScan(files, affectedArea, language);
      setResult(data);
    } catch (e) {
      setError(e?.response?.data?.detail || "Something went wrong scanning the field.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>🌾 Multi-Photo Field Scan</h2>
      <p className="muted">
        Scan several plants across your field in one session to get an aggregate field health
        score and a rough yield-loss estimate.
      </p>

      <div className="upload-zone" onClick={() => inputRef.current?.click()}>
        {previews.length ? (
          <div className="thumb-grid">
            {previews.map((p, i) => (
              <img key={i} src={p} className="thumb" alt={`plant ${i}`} />
            ))}
          </div>
        ) : (
          <span>Tap to choose multiple photos (up to 20)</span>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          multiple
          hidden
          onChange={(e) => onFiles(e.target.files)}
        />
      </div>

      <label className="slider-label">
        Estimated % of field showing similar symptoms: <b>{affectedArea}%</b>
        <input
          type="range"
          min="0"
          max="100"
          value={affectedArea}
          onChange={(e) => setAffectedArea(Number(e.target.value))}
        />
      </label>

      <button className="primary-btn" disabled={!files.length || loading} onClick={submit}>
        {loading ? "Scanning field…" : `Scan ${files.length || ""} Photos`}
      </button>

      {error && <p className="error-text">{error}</p>}

      {result && (
        <div className="result-panel">
          <div className="health-score-ring">
            <div className="score-value">{result.field_health_score_pct}%</div>
            <div className="score-caption">Field Health Score</div>
          </div>

          <h4>Condition Breakdown</h4>
          <ul className="breakdown-list">
            {result.condition_breakdown.length === 0 && <li>All scanned plants look healthy 🎉</li>}
            {result.condition_breakdown.map((b) => (
              <li key={b.condition}>
                {b.condition}: {b.count} plants ({b.pct}%)
              </li>
            ))}
          </ul>

          <h4>Estimated Yield Loss</h4>
          <p className="yield-loss-value">{result.yield_loss.estimated_yield_loss_pct}%</p>
          <p className="muted">{result.yield_loss.summary}</p>

          <h4>Field Summary</h4>
          <p>{result.ai_summary}</p>
        </div>
      )}
    </div>
  );
}
