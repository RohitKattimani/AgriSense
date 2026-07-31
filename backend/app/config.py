"""
Central configuration for AgriSense AI backend.
All secrets/keys are read from environment variables (see .env.example).
Nothing here hardcodes a key - the app degrades gracefully into
"demo/mock mode" for any service whose key is missing, so the app
is runnable out of the box, but gives real results once keys are added.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- LLM provider (used for chat, diagnosis explanation, sell/hold advisor, translation) ---
    LLM_PROVIDER: str = "openai"           # "openai" | "anthropic" | "groq" | "mock"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    # Groq (OpenAI-compatible endpoint - uses the `openai` SDK pointed at Groq's
    # API, so no extra dependency is required). Get a free key at console.groq.com.
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    # --- Vision model (HuggingFace) ---
    VISION_MODEL_ID: str = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
    HF_TOKEN: Optional[str] = None
    VISION_DEVICE: str = "cpu"

    # --- Weather ---
    WEATHER_PROVIDER: str = "mock"          # "openweather" | "mock"
    OPENWEATHER_API_KEY: Optional[str] = None

    # --- Misc ---
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"


settings = Settings()
