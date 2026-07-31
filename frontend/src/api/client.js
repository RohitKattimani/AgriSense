import axios from "axios";

export const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({ baseURL: API_BASE });

export const diagnosePhoto = (file, language, notes) => {
  const form = new FormData();
  form.append("image", file);
  form.append("language", language || "en");
  if (notes) form.append("notes", notes);
  return api.post("/api/diagnose", form).then((r) => r.data);
};

export const fieldScan = (files, affectedAreaPct, language) => {
  const form = new FormData();
  Array.from(files).forEach((f) => form.append("images", f));
  form.append("affected_area_pct", affectedAreaPct);
  form.append("language", language || "en");
  return api.post("/api/field-scan", form).then((r) => r.data);
};

export const getCrops = () => api.get("/api/market/crops").then((r) => r.data.crops);

export const getTrend = (crop, nDays = 90, forecastDays = 7) =>
  api
    .get(`/api/market/trend/${crop}`, { params: { n_days: nDays, forecast_days: forecastDays } })
    .then((r) => r.data);

export const getSellHoldAdvice = (payload) =>
  api.post("/api/advisor/sell-hold", payload).then((r) => r.data);

export const sendChat = (payload) => api.post("/api/chat", payload).then((r) => r.data);

export const getOutbreakMap = () => api.get("/api/outbreak/map").then((r) => r.data);

export const getLanguages = () => api.get("/api/translate/languages").then((r) => r.data);

export const translateText = (text, targetLanguage) =>
  api.post("/api/translate", { text, target_language: targetLanguage }).then((r) => r.data);

export const listQuestions = () => api.get("/api/qa").then((r) => r.data.questions);

export const askQuestion = (payload) => api.post("/api/qa/ask", payload).then((r) => r.data);

export default api;
