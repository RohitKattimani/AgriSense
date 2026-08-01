# 🌱 AgriSense AI - Farm Companion

An AI-powered farm companion for smallholder farmers: diagnose crop diseases from a photo,
get plain-language advice from a chatbot, track market price trends, and get an AI-driven
"sell now vs hold" recommendation - all designed for basic smartphones and patchy connectivity.

Built as a **real two-part app**: a Python/FastAPI backend (ML + LLM + data logic) and a
React frontend (mobile-friendly UI). Everything runs locally; it degrades gracefully into a
fully working **demo mode** with zero API keys, and upgrades to real AI output the moment you
add your own OpenAI/Anthropic/HuggingFace/OpenWeather keys.

---

## What's implemented

**Core requirements**
- ✅ **Crop disease/pest detection** - pretrained HuggingFace image classifier
  ([`linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`](https://huggingface.co/linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification),
  38 PlantVillage classes), returns label + confidence score.
- ✅ **AI chatbot** - explains diagnoses in plain language and answers free-form farming
  questions, via a pluggable OpenAI/Anthropic LLM layer.
- ✅ **Market price trend view** - simulated historical price data for 5 crops, with a real
  `scikit-learn` linear + polynomial regression producing a trend direction and 7-day forecast.
- ✅ **Smart Sell/Hold advisor** - an **agent that uses real LLM function/tool calling**
  (OpenAI `tools` / Anthropic `tool_use`) to pull together the price trend, a simulated weather
  forecast, and crop perishability, then explains its "SELL NOW" or "HOLD" recommendation.
- ✅ **Voice input** - browser Web Speech API, wired into every text field (diagnosis notes,
  chat, community Q&A) so farmers can speak instead of type, in their own language.

**Bonus features**
- ✅ **Multi-photo field scan** - upload several plant photos, get an aggregate field health
  score and a per-condition breakdown.
- ✅ **Yield-loss estimation** - combines disease severity (from model confidence) with an
  affected-area estimate into a rough yield-loss percentage.
- ✅ **Community outbreak map** - simulates scan reports from many farmers across a region and
  runs **DBSCAN clustering** (`scikit-learn`) to flag geographic disease clusters vs isolated cases.
- ✅ **Multilingual/vernacular support** - 10 Indian languages (Hindi, Kannada, Tamil, Telugu,
  Marathi, Bengali, Gujarati, Punjabi, Malayalam + English) for chat, diagnosis explanations,
  and voice input; translation endpoint powered by the LLM.
- ✅ **Community Q&A** - ask a question, get an AI-suggested answer; uses TF-IDF cosine
  similarity to surface related past questions as grounding context for the LLM.
- ✅ **WhatsApp-bot concept mockup** - an interactive chat-style mockup showing how the same
  backend endpoints would power a WhatsApp Business API bot, with an implementation note.

---

## Architecture

```
agrisense-ai/
├── backend/                  FastAPI app (Python)
│   ├── app/
│   │   ├── main.py           App entrypoint, CORS, router wiring
│   │   ├── config.py         Env-driven settings (all keys optional)
│   │   ├── routers/          One file per feature: diagnose, field_scan, market,
│   │   │                     advisor, chat, outbreak, translate, qa
│   │   └── services/         Business logic: vision_model, llm_service, price_model,
│   │                         weather_service, outbreak_service, yield_estimator
│   ├── requirements.txt
│   └── .env.example
└── frontend/                 React + Vite app
    ├── src/
    │   ├── api/client.js      All backend calls
    │   ├── hooks/useVoiceInput.js
    │   ├── context/LanguageContext.jsx
    │   └── components/        Diagnose, FieldScan, MarketTrend, SellHoldAdvisor,
    │                          ChatBot, OutbreakMap, CommunityQA, WhatsAppMockup
    └── .env.example
```

The frontend never touches any AI API directly - it only calls the FastAPI backend, which is
where all model/LLM/API-key logic lives. That keeps API keys off the client and makes it easy
to swap providers later.

---

## Prerequisites

- **Python 3.10+** and `pip`
- **Node.js 18+** and `npm`
- (Optional but recommended for real AI output) an **OpenAI** or **Anthropic** API key
- (Optional) an **OpenWeather** API key for real weather instead of a simulated forecast
- (Optional) a **HuggingFace** token if the vision model requires auth on your network (the
  default model is public and usually doesn't need one)

> **Demo mode:** if you skip all the keys, the app still runs end-to-end - the vision model
> falls back to a deterministic mock classifier if it can't download from HuggingFace, and the
> LLM falls back to clear, labeled "[Demo mode]" rule-based text. This is intentional so you
> can run and click through the whole app immediately, then flip on real AI when ready.

---

## 1. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env   #if using Windows, then type copy .env.example .env
# then edit .env and add whichever keys you have, e.g.:
#   LLM_PROVIDER=groq
#   GROQ_API_KEY=gsk_...
#   WEATHER_PROVIDER=openweather
#   OPENWEATHER_API_KEY=...

uvicorn app.main:app --reload --port 8000
```

Backend is now running at **http://localhost:8000**. Interactive API docs (Swagger UI) are
auto-generated at **http://localhost:8000/docs** - useful for testing endpoints directly.

The first request to `/api/diagnose` or `/api/field-scan` will download the HuggingFace model
weights (a few hundred MB) - this happens once and is cached locally afterward.

## 2. Frontend setup

In a second terminal:

```bash
cd frontend
npm install

cp .env.example .env #if using Windows, then type copy .env.example .env
# defaults to VITE_API_BASE_URL=http://localhost:8000, change if needed

npm run dev
```

Frontend is now running at **http://localhost:5173** - open it in your browser (Chrome or Edge
recommended for full voice-input support).

---

## Using LLM function/tool calling (the Sell/Hold advisor)

`POST /api/advisor/sell-hold` is the most "agentic" endpoint: it hands the LLM three tools
(`get_price_trend`, `get_weather_forecast`, `get_perishability`) and lets the model decide to
call all of them, read the results, and produce a final natural-language recommendation. The
full tool-call trace (what was called, with what arguments, and what came back) is returned
alongside the recommendation and shown in the UI under "How the agent reached this" - useful
both for debugging and for building farmer trust in the recommendation.

This works with `LLM_PROVIDER=openai` or `LLM_PROVIDER=groq` (both use the OpenAI
`tools`/`tool_choice` schema - Groq's API is OpenAI-compatible, so it's handled by the same
code path) or `LLM_PROVIDER=anthropic` (uses `tools`/`tool_use`) - the request/response
translation between formats is handled in `backend/app/services/llm_service.py`.

---

## Swapping in real market/weather data later

- **Prices:** `backend/app/services/price_model.py` currently simulates history in
  `_simulate_history()`. Swap that function for a call to a real source (e.g. Agmarknet /
  data.gov.in mandi price APIs) - the regression and forecast logic downstream doesn't need to
  change.
- **Weather:** already supports real data - set `WEATHER_PROVIDER=openweather` and
  `OPENWEATHER_API_KEY` in `backend/.env`.
- **Outbreak reports:** `backend/app/services/outbreak_service.py` simulates farmer reports in
  `_simulate_reports()`. In production, each real `/api/diagnose` call would also log
  `{lat, lon, disease, date}` to a database, and this function would query that table instead.

---

## Notes & limitations

- This is a working prototype: the vision model is a general PlantVillage-trained classifier, not
  validated against any specific real field deployment - always pair with an actual agronomist
  for high-stakes decisions, and the UI says so in its footer.
- Market prices and weather are simulated by default; treat "sell/hold" advice as illustrative
  until wired to real data sources.
- Voice input relies on the browser's Web Speech API, which has the best support in Chrome/Edge
  and more limited support in Firefox/Safari.
