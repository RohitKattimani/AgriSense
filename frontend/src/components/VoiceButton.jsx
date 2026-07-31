import { useVoiceInput } from "../hooks/useVoiceInput";

export default function VoiceButton({ lang = "en-US", onResult, title = "Speak instead of typing" }) {
  const { listening, supported, start, stop, error } = useVoiceInput({ lang, onResult });

  if (!supported) {
    return (
      <span className="voice-unsupported" title="Voice input isn't supported in this browser">
        🎤 N/A
      </span>
    );
  }

  return (
    <button
      type="button"
      title={title}
      className={`voice-btn ${listening ? "listening" : ""}`}
      onClick={listening ? stop : start}
    >
      {listening ? "🔴 Listening…" : "🎤 Speak"}
      {error && <span className="voice-error"> ({error})</span>}
    </button>
  );
}
