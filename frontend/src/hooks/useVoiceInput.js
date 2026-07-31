import { useEffect, useRef, useState, useCallback } from "react";

/**
 * Wraps the browser's SpeechRecognition API (Web Speech API) so any input
 * in the app can be filled by voice - important since many smallholder
 * farmers are more comfortable speaking than typing, especially in their
 * own language.
 *
 * Note: SpeechRecognition is a browser feature (Chrome/Edge support it
 * well; Firefox/Safari support varies) - no backend call is needed for
 * this to work.
 */
export function useVoiceInput({ lang = "en-US", onResult } = {}) {
  const [listening, setListening] = useState(false);
  const [supported, setSupported] = useState(true);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSupported(false);
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = lang;

    recognition.onresult = (event) => {
      let text = "";
      for (let i = 0; i < event.results.length; i++) {
        text += event.results[i][0].transcript;
      }
      setTranscript(text);
      if (event.results[event.results.length - 1].isFinal && onResult) {
        onResult(text);
      }
    };
    recognition.onerror = (e) => setError(e.error);
    recognition.onend = () => setListening(false);

    recognitionRef.current = recognition;
    return () => recognition.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);

  const start = useCallback(() => {
    if (!recognitionRef.current) return;
    setError(null);
    setTranscript("");
    setListening(true);
    recognitionRef.current.start();
  }, []);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    setListening(false);
  }, []);

  return { listening, supported, transcript, error, start, stop };
}
