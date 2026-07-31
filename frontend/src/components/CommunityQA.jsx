import { useEffect, useState } from "react";
import { listQuestions, askQuestion } from "../api/client";
import { useLanguage } from "../context/LanguageContext";
import VoiceButton from "./VoiceButton";

export default function CommunityQA() {
  const { language, current } = useLanguage();
  const [questions, setQuestions] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [latest, setLatest] = useState(null);

  const load = () => listQuestions().then((qs) => setQuestions(qs.slice().reverse()));

  useEffect(() => {
    load();
  }, []);

  const submit = async () => {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const res = await askQuestion({ question: text, language });
      setLatest(res);
      setText("");
      load();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>🧑‍🌾 Community Q&A</h2>
      <p className="muted">Ask a question - AgriSense finds similar past questions and suggests an answer.</p>

      <div className="row">
        <input
          className="text-input"
          placeholder="Ask something about your crops…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
        />
        <VoiceButton lang={current.speechLang} onResult={(t) => setText(t)} />
      </div>
      <button className="primary-btn" onClick={submit} disabled={loading}>
        {loading ? "Thinking…" : "Ask the Community"}
      </button>

      {latest && (
        <div className="result-panel">
          <h4>Suggested Answer</h4>
          <p>{latest.new_entry.answer}</p>
          {latest.similar_past_questions.length > 0 && (
            <>
              <h4>Similar past questions used</h4>
              <ul>
                {latest.similar_past_questions.map((q) => (
                  <li key={q.id}>
                    {q.question} <span className="muted">(similarity {(q.similarity * 100).toFixed(0)}%)</span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}

      <h3 className="section-subhead">Recent Community Questions</h3>
      <div className="qa-list">
        {questions.map((q) => (
          <div key={q.id} className="qa-item">
            <p className="qa-question">Q: {q.question}</p>
            <p className="qa-answer">A: {q.answer}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
