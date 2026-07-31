import { useState, useRef, useEffect } from "react";
import { sendChat } from "../api/client";
import { useLanguage } from "../context/LanguageContext";
import VoiceButton from "./VoiceButton";

export default function ChatBot() {
  const { language, current } = useLanguage();
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Namaste! I'm AgriSense. Ask me anything about your crops, pests, weather, or prices." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text) => {
    const content = (text ?? input).trim();
    if (!content) return;
    const newMessages = [...messages, { role: "user", content }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);
    try {
      const data = await sendChat({
        message: content,
        history: newMessages.slice(-8),
        language,
      });
      setMessages((m) => [...m, { role: "assistant", content: data.reply }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "Sorry, I couldn't reach the server. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card chat-card">
      <h2>💬 Ask AgriSense</h2>
      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role}`}>
            {m.content}
          </div>
        ))}
        {loading && <div className="chat-bubble assistant">…</div>}
        <div ref={bottomRef} />
      </div>
      <div className="row chat-input-row">
        <input
          className="text-input"
          value={input}
          placeholder="Type or speak your question…"
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <VoiceButton lang={current.speechLang} onResult={(t) => send(t)} />
        <button className="primary-btn small" onClick={() => send()} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}
