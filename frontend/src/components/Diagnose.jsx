import { useState, useRef } from "react";
import { diagnosePhoto } from "../api/client";
import { useLanguage } from "../context/LanguageContext";
import VoiceButton from "./VoiceButton";

export default function Diagnose() {
  const { language, current } = useLanguage();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const onFile = (f) => {
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  };

  const submit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const data = await diagnosePhoto(file, language, notes);
      setResult(data);
    } catch (e) {
      setError(e?.response?.data?.detail || "Something went wrong diagnosing this photo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>📷 Crop Health Diagnosis</h2>
      <p className="muted">Upload a photo of a leaf or plant and get an instant AI diagnosis.</p>

      <div className="upload-zone" onClick={() => inputRef.current?.click()}>
        {preview ? (
          <img src={preview} alt="preview" className="preview-img" />
        ) : (
          <span>Tap to choose or take a photo</span>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          capture="environment"
          hidden
          onChange={(e) => onFile(e.target.files[0])}
        />
      </div>

      <div className="row">
        <input
          className="text-input"
          placeholder="Optional notes (e.g. 'spots appeared after rain')"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
        <VoiceButton lang={current.speechLang} onResult={(t) => setNotes(t)} />
      </div>

      <button className="primary-btn" disabled={!file || loading} onClick={submit}>
        {loading ? "Diagnosing…" : "Diagnose Photo"}
      </button>

      {error && <p className="error-text">{error}</p>}

      {result && (
        <div className={`result-panel ${result.is_healthy ? "healthy" : "unhealthy"}`}>
          <h3>
            {result.is_healthy ? "✅" : "⚠️"} {result.crop}: {result.condition}
          </h3>
          <p className="confidence">Confidence: {(result.top_confidence * 100).toFixed(1)}%</p>

          <div className="pred-bars">
            {result.predictions.map((p) => (
              <div key={p.label} className="pred-bar-row">
                <span className="pred-label">{p.label.replace(/___|_/g, " ")}</span>
                <div className="pred-bar-track">
                  <div className="pred-bar-fill" style={{ width: `${p.score * 100}%` }} />
                </div>
                <span className="pred-pct">{(p.score * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>

          <h4>What this means</h4>
          <p>{result.explanation}</p>

          <p className="model-source">Model: {result.model_source}</p>
        </div>
      )}
    </div>
  );
}
